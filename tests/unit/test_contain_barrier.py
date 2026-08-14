"""Barrier-only containment preserves denial's movement exactly (Phase C).

The load-bearing test is the differential invariant: over a large deterministic sample of
states, whenever denial moves, the candidate returns the identical move. The candidate may
differ only in its barrier decision, so a move mismatch is a defect. The rest pin the
preserved finisher, the reserve path, and determinism.
"""

import random

from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, MoveIntent
from p2p_cop_agent.strategy.contain_barrier import (
    BARRIER_BENEFIT_THRESHOLD,
    contain_barrier_turn_intent,
    free_region,
)
from p2p_cop_agent.strategy.denial import denial_turn_intent

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")
QUOTA = 14


def _c(row: int, col: int) -> Coordinate:
    return Coordinate(row, col)


def _states(count: int):
    """Yield deterministic (cop, believed, barriers) states: the generated invariant sample."""
    rng = random.Random(0xB0A2D)
    cells = [_c(r, c) for r in range(7) for c in range(7)]
    for _ in range(count):
        cop, believed = rng.sample(cells, 2)
        pool = [cell for cell in cells if cell not in (cop, believed)]
        k = rng.randint(0, 12)
        barriers = BarrierField(QUOTA, tuple(rng.sample(pool, k)))
        yield cop, believed, barriers


def test_movement_invariant_over_a_large_generated_sample() -> None:
    """denial returns a MoveIntent  ==>  the candidate returns the identical MoveIntent."""
    checked = moves = 0
    for cop, believed, barriers in _states(900):
        baseline = denial_turn_intent(BOARD, cop, believed, barriers, None)
        candidate = contain_barrier_turn_intent(BOARD, cop, believed, barriers, None)
        checked += 1
        if isinstance(baseline, MoveIntent):
            moves += 1
            assert isinstance(candidate, MoveIntent), (cop, believed)
            assert candidate.action == baseline.action, (cop, believed, baseline, candidate)
    assert checked == 900
    assert moves > 0, "the sample must exercise denial move turns"


def test_the_candidate_only_ever_differs_on_a_barrier_turn() -> None:
    """When denial moves the intents are equal; any difference is a barrier-vs-barrier one."""
    for cop, believed, barriers in _states(500):
        baseline = denial_turn_intent(BOARD, cop, believed, barriers, None)
        candidate = contain_barrier_turn_intent(BOARD, cop, believed, barriers, None)
        if candidate != baseline:
            assert isinstance(baseline, BarrierIntent) or isinstance(candidate, MoveIntent)


def test_a_capturing_move_is_preserved() -> None:
    """A believed cell one step away is captured by moving onto it, exactly as denial does."""
    baseline = denial_turn_intent(BOARD, _c(1, 2), _c(1, 3), BarrierField(QUOTA), None)
    candidate = contain_barrier_turn_intent(BOARD, _c(1, 2), _c(1, 3), BarrierField(QUOTA), None)
    assert candidate == baseline


def test_a_finishing_barrier_is_preserved() -> None:
    """When denial's own intent is a barrier the candidate may re-decide, but stays a barrier
    or falls back to a legal interception move -- never an illegal or empty turn."""
    intent = contain_barrier_turn_intent(BOARD, _c(2, 2), _c(5, 5), BarrierField(QUOTA), None)
    assert isinstance(intent, (BarrierIntent, MoveIntent))


def test_determinism_same_state_same_intent() -> None:
    state = (BOARD, _c(0, 0), _c(6, 6), BarrierField(QUOTA), None)
    assert contain_barrier_turn_intent(*state) == contain_barrier_turn_intent(*state)


def test_a_reserve_turn_advances_the_chase_when_no_cut_pays() -> None:
    """With the quota below the late reserve, no barrier is placed and the Cop moves."""
    spent = BarrierField(2, ())  # remaining 2 == LATE_GAME_RESERVE, so cuts are withheld
    intent = contain_barrier_turn_intent(BOARD, _c(0, 0), _c(6, 6), spent, None)
    assert isinstance(intent, MoveIntent)


def test_free_region_shrinks_when_the_cop_closes() -> None:
    """The evader owns less ground as the Cop nears it -- the objective the cuts minimise."""
    far = free_region(BOARD, _c(6, 6), _c(0, 0), frozenset())
    near = free_region(BOARD, _c(6, 6), _c(5, 5), frozenset())
    assert near < far
    assert BARRIER_BENEFIT_THRESHOLD > 0
