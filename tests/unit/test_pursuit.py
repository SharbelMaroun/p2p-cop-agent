"""Tests for the deterministic Cop pursuit baseline."""

import pytest

from p2p_cop_agent.domain import (
    Action,
    BarrierField,
    Board,
    BoardError,
    Coordinate,
    apply_move,
    legal_moves,
)
from p2p_cop_agent.strategy import choose_action


def board() -> Board:
    """Return a 7x7 top-left-origin board."""
    return Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def blocked_cells(*cells: Coordinate) -> frozenset[Coordinate]:
    """Return a barrier cell set built through the barrier field."""
    field = BarrierField(max_barriers=14)
    for cell in cells:
        field = field.place(board(), cell)
    return field.cells


def test_moves_south_toward_a_target_below() -> None:
    assert choose_action(board(), Coordinate(1, 3), Coordinate(5, 3)) is Action.SOUTH


def test_moves_north_toward_a_target_above() -> None:
    assert choose_action(board(), Coordinate(5, 3), Coordinate(1, 3)) is Action.NORTH


def test_moves_east_toward_a_target_to_the_right() -> None:
    assert choose_action(board(), Coordinate(3, 1), Coordinate(3, 5)) is Action.EAST


def test_moves_west_toward_a_target_to_the_left() -> None:
    assert choose_action(board(), Coordinate(3, 5), Coordinate(3, 1)) is Action.WEST


def test_open_board_diagonal_tie_breaks_by_declaration_order() -> None:
    assert choose_action(board(), Coordinate(3, 3), Coordinate(1, 1)) is Action.NORTH


def test_barrier_aware_route_beats_the_apparently_equal_one() -> None:
    blocked = blocked_cells(Coordinate(3, 1), Coordinate(2, 1))
    assert choose_action(board(), Coordinate(3, 0), Coordinate(3, 2), blocked) is Action.SOUTH


def test_equal_length_detours_break_by_declaration_order() -> None:
    blocked = blocked_cells(Coordinate(3, 1))
    assert choose_action(board(), Coordinate(3, 0), Coordinate(3, 2), blocked) is Action.NORTH


def test_stays_when_already_standing_on_the_target() -> None:
    assert choose_action(board(), Coordinate(3, 3), Coordinate(3, 3)) is Action.STAY


def test_stays_when_sealed_off_from_the_target() -> None:
    blocked = blocked_cells(Coordinate(0, 1), Coordinate(1, 0))
    assert choose_action(board(), Coordinate(0, 0), Coordinate(3, 3), blocked) is Action.STAY


def test_returned_action_is_always_legal() -> None:
    blocked = blocked_cells(Coordinate(2, 3), Coordinate(3, 4))
    action = choose_action(board(), Coordinate(3, 3), Coordinate(0, 6), blocked)
    assert action in legal_moves(board(), Coordinate(3, 3), blocked)


def test_never_steps_onto_a_barrier() -> None:
    blocked = blocked_cells(Coordinate(2, 3))
    action = choose_action(board(), Coordinate(3, 3), Coordinate(0, 3), blocked)
    assert apply_move(board(), Coordinate(3, 3), action, blocked) not in blocked


def test_repeated_calls_return_the_same_action() -> None:
    blocked = blocked_cells(Coordinate(3, 1), Coordinate(2, 1))
    calls = [choose_action(board(), Coordinate(3, 0), Coordinate(3, 2), blocked) for _ in range(5)]
    assert len(set(calls)) == 1


def test_pursuit_reaches_the_target_deterministically() -> None:
    cop, target = Coordinate(6, 0), Coordinate(0, 6)
    for _ in range(12):
        cop = apply_move(board(), cop, choose_action(board(), cop, target), frozenset())
    assert cop == target


def test_rejects_an_off_board_cop() -> None:
    with pytest.raises(BoardError, match="outside board bounds"):
        choose_action(board(), Coordinate(7, 0), Coordinate(3, 3))


def test_rejects_an_off_board_target() -> None:
    with pytest.raises(BoardError, match="outside board bounds"):
        choose_action(board(), Coordinate(3, 3), Coordinate(-1, 3))
