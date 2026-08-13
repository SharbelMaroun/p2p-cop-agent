"""The search engine: legal, decisive, and reproducible."""

from __future__ import annotations

import pytest

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move, is_legal_move
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, MoveIntent
from p2p_cop_agent.strategy.engine import engine_turn_intent

BOARD = Board(7, 0, "top-left")
QUOTA = 14
SMALL = 4_000


def decide(cop, thief, barriers=(), *, budget=SMALL, quota=QUOTA):
    field = BarrierField(quota, tuple(Coordinate(*cell) for cell in barriers))
    return engine_turn_intent(BOARD, Coordinate(*cop), Coordinate(*thief), field,
                              None, budget=budget, horizon=35)


def test_steps_onto_an_adjacent_thief() -> None:
    """The capture is one move away; nothing else is worth considering."""
    assert decide((3, 3), (3, 4)) == MoveIntent(Action.EAST)


@pytest.mark.parametrize("thief", [(2, 3), (4, 3), (3, 2), (3, 4)])
def test_captures_from_every_direction(thief: tuple[int, int]) -> None:
    intent = decide((3, 3), thief)
    assert isinstance(intent, MoveIntent)
    assert apply_move(BOARD, Coordinate(3, 3), intent.action).as_pair() == thief


def test_walls_a_thief_that_one_barrier_would_trap() -> None:
    """A corner Thief with a single exit: closing it is a capture, so take it."""
    intent = decide((0, 2), (0, 0), barriers=[(1, 0)])
    assert intent == BarrierIntent(Coordinate(0, 1))


def test_does_not_stand_still_when_the_thief_is_far_away() -> None:
    """`STAY` is legal and was the shipped stack's failure mode; it must not be the default."""
    intent = decide((0, 0), (6, 6))
    assert intent != MoveIntent(Action.STAY)


@pytest.mark.parametrize(
    "cop,thief",
    [((0, 0), (6, 6)), ((3, 3), (0, 6)), ((6, 0), (2, 5)), ((1, 1), (5, 4))],
)
def test_every_decision_is_legal(cop, thief) -> None:
    intent = decide(cop, thief)
    if isinstance(intent, MoveIntent):
        assert is_legal_move(BOARD, Coordinate(*cop), intent.action)
    else:
        distance = abs(intent.cell.row - cop[0]) + abs(intent.cell.col - cop[1])
        assert distance <= 1


def test_is_deterministic() -> None:
    """Rule 53's audit and M6-03d both require the same match to replay identically."""
    first = decide((0, 0), (5, 5))
    for _ in range(3):
        assert decide((0, 0), (5, 5)) == first


def test_never_places_a_barrier_it_has_no_quota_for() -> None:
    spent = tuple(Coordinate(0, col) for col in range(7)) + tuple(
        Coordinate(1, col) for col in range(7))
    field = BarrierField(14, spent)
    intent = engine_turn_intent(BOARD, Coordinate(3, 3), Coordinate(5, 5), field,
                                None, budget=SMALL, horizon=35)
    assert isinstance(intent, MoveIntent)


def test_a_belief_on_our_own_cell_is_never_read_as_a_capture() -> None:
    """Rule 22: a false capture claim is disqualification, not a lost turn.

    The Thief cannot be standing on us -- the sub-game would already be over -- so this
    is a mis-aimed belief, and the engine must move rather than report a capture.
    """
    intent = decide((3, 3), (3, 3))
    assert isinstance(intent, MoveIntent)
    assert intent.action is not Action.STAY


def test_stays_when_the_believed_cell_is_already_walled() -> None:
    """A belief pointing at a barrier is not a target; walking at it would be worse."""
    intent = decide((3, 3), (0, 0), barriers=[(0, 0)])
    assert intent == MoveIntent(Action.STAY)
