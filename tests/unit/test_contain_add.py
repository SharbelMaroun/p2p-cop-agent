"""Additive-only containment: denial untouched, extra walls only where denial places none.

The load-bearing checks are the five differential invariants over a deterministic state
sample: candidate move == baseline move; a baseline barrier is reproduced identically; any
extra barrier occurs only on a baseline no-barrier turn; determinism; legal actions only.
"""

import random

from p2p_cop_agent.domain.barriers import BarrierError, BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import legal_moves
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, MoveIntent
from p2p_cop_agent.strategy.contain_add import QUOTA_RESERVE, contain_add_turn_intent
from p2p_cop_agent.strategy.denial import denial_turn_intent

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")
QUOTA = 14


def _c(row: int, col: int) -> Coordinate:
    return Coordinate(row, col)


def _states(count: int):
    rng = random.Random(0xADD5)
    cells = [_c(r, c) for r in range(7) for c in range(7)]
    for _ in range(count):
        cop, believed = rng.sample(cells, 2)
        pool = [cell for cell in cells if cell not in (cop, believed)]
        barriers = BarrierField(QUOTA, tuple(rng.sample(pool, rng.randint(0, 12))))
        yield cop, believed, barriers


def _is_legal(board, cop, barriers, intent) -> bool:
    if isinstance(intent, MoveIntent):
        return intent.action in legal_moves(board, cop, barriers.cells)
    try:
        barriers.place_adjacent(board, cop, intent.cell)
    except BarrierError:
        return False
    return True


def test_the_five_differential_invariants_hold_over_the_sample() -> None:
    baseline_moves = 0
    for cop, believed, barriers in _states(900):
        base = denial_turn_intent(BOARD, cop, believed, barriers, None)
        cand = contain_add_turn_intent(BOARD, cop, believed, barriers, None)
        # (2) a baseline barrier is reproduced identically.
        if isinstance(base, BarrierIntent):
            assert cand == base, (cop, believed)
        # (1) whenever the candidate moves, the move equals baseline's.
        if isinstance(cand, MoveIntent):
            assert isinstance(base, MoveIntent) and cand.action == base.action, (cop, believed)
            baseline_moves += 1
        # (3) an extra barrier occurs only on a baseline no-barrier (move) turn.
        if isinstance(cand, BarrierIntent) and cand != base:
            assert isinstance(base, MoveIntent), (cop, believed)
        # (5) legal actions only.
        assert _is_legal(BOARD, cop, barriers, cand), (cop, believed, cand)
    assert baseline_moves > 0


def test_determinism_same_state_same_intent() -> None:
    state = (BOARD, _c(3, 2), _c(3, 4), BarrierField(QUOTA), None)
    assert contain_add_turn_intent(*state) == contain_add_turn_intent(*state)


def test_a_baseline_barrier_turn_is_returned_verbatim() -> None:
    """Adjacent to a distant sanctuary, denial walls; the candidate must not touch it."""
    barriers = BarrierField(QUOTA)
    base = denial_turn_intent(BOARD, _c(2, 2), _c(5, 5), barriers, None)
    cand = contain_add_turn_intent(BOARD, _c(2, 2), _c(5, 5), barriers, None)
    if isinstance(base, BarrierIntent):
        assert cand == base


def test_quota_safety_blocks_additions_when_the_reserve_is_reached() -> None:
    """With remaining quota at the reserve, no addition may be made -- denial's action stands."""
    at_reserve = BarrierField(QUOTA_RESERVE, ())  # remaining == QUOTA_RESERVE
    base = denial_turn_intent(BOARD, _c(3, 2), _c(3, 3), at_reserve, None)
    cand = contain_add_turn_intent(BOARD, _c(3, 2), _c(3, 3), at_reserve, None)
    assert cand == base
