"""Tests for the deterministic move-or-barrier turn decision."""

import pytest

from p2p_cop_agent.domain import Action, BarrierField, Board, BoardError, Coordinate
from p2p_cop_agent.strategy import BarrierIntent, MoveIntent, choose_turn_intent


def board() -> Board:
    """Return a 7x7 top-left-origin board."""
    return Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def field(*cells: Coordinate, quota: int = 14) -> BarrierField:
    """Return a barrier field holding the given cells."""
    placed = BarrierField(max_barriers=quota)
    for cell in cells:
        placed = placed.place(board(), cell)
    return placed


def test_moves_onto_an_adjacent_thief_rather_than_spending_a_barrier() -> None:
    intent = choose_turn_intent(board(), Coordinate(3, 3), Coordinate(3, 4), field())
    assert intent == MoveIntent(Action.EAST)


def test_capture_by_moving_is_preferred_even_with_quota_available() -> None:
    intent = choose_turn_intent(board(), Coordinate(0, 0), Coordinate(1, 0), field())
    assert isinstance(intent, MoveIntent)


def test_places_the_final_barrier_to_trap_a_cornered_thief() -> None:
    barriers = field(Coordinate(1, 0))
    intent = choose_turn_intent(board(), Coordinate(0, 2), Coordinate(0, 0), barriers)
    assert intent == BarrierIntent(Coordinate(0, 1))


def test_pursues_when_a_move_closes_the_distance() -> None:
    intent = choose_turn_intent(board(), Coordinate(6, 6), Coordinate(0, 0), field())
    assert isinstance(intent, MoveIntent)


def test_returns_a_move_when_no_barrier_helps() -> None:
    intent = choose_turn_intent(board(), Coordinate(6, 6), Coordinate(0, 0), field(quota=0))
    assert isinstance(intent, MoveIntent)


def test_exhausted_quota_never_yields_a_barrier_intent() -> None:
    intent = choose_turn_intent(board(), Coordinate(0, 2), Coordinate(0, 0), field(quota=0))
    assert isinstance(intent, MoveIntent)


def test_intent_is_exclusive_by_construction() -> None:
    intent = choose_turn_intent(board(), Coordinate(3, 3), Coordinate(3, 4), field())
    assert not (isinstance(intent, MoveIntent) and isinstance(intent, BarrierIntent))


def test_decision_is_repeatable() -> None:
    calls = [
        choose_turn_intent(board(), Coordinate(0, 2), Coordinate(0, 0), field(Coordinate(1, 0)))
        for _ in range(5)
    ]
    assert len(set(calls)) == 1


def test_rejects_an_off_board_cop() -> None:
    with pytest.raises(BoardError, match="outside board bounds"):
        choose_turn_intent(board(), Coordinate(9, 9), Coordinate(0, 0), field())


def test_rejects_an_off_board_target() -> None:
    with pytest.raises(BoardError, match="outside board bounds"):
        choose_turn_intent(board(), Coordinate(0, 0), Coordinate(9, 9), field())


def test_does_not_waste_a_barrier_on_an_already_trapped_thief() -> None:
    barriers = field(Coordinate(0, 1), Coordinate(1, 0))
    intent = choose_turn_intent(board(), Coordinate(3, 3), Coordinate(0, 0), barriers)
    assert isinstance(intent, MoveIntent)


def test_trap_is_chosen_over_a_merely_closer_move() -> None:
    barriers = field(Coordinate(1, 0))
    intent = choose_turn_intent(board(), Coordinate(0, 2), Coordinate(0, 0), barriers)
    assert isinstance(intent, BarrierIntent)
