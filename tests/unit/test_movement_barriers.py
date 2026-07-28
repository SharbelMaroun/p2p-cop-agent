"""Tests for barrier-aware legal movement."""

import pytest

from p2p_cop_agent.domain import (
    Action,
    BarrierField,
    Board,
    Coordinate,
    MovementError,
    apply_move,
    is_legal_move,
    legal_moves,
)


def board() -> Board:
    """Return a 7x7 top-left-origin board."""
    return Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def blocked_cells(*cells: Coordinate) -> frozenset[Coordinate]:
    """Return a barrier cell set built through the barrier field."""
    field = BarrierField(max_barriers=14)
    for cell in cells:
        field = field.place(board(), cell)
    return field.cells


def test_directional_move_onto_barrier_is_illegal() -> None:
    blocked = blocked_cells(Coordinate(2, 3))
    assert is_legal_move(board(), Coordinate(3, 3), Action.NORTH, blocked) is False


def test_directional_move_to_free_cell_is_legal() -> None:
    blocked = blocked_cells(Coordinate(2, 3))
    assert is_legal_move(board(), Coordinate(3, 3), Action.SOUTH, blocked) is True


def test_stay_remains_legal_even_when_neighbours_are_barriered() -> None:
    blocked = blocked_cells(
        Coordinate(2, 3), Coordinate(4, 3), Coordinate(3, 2), Coordinate(3, 4)
    )
    assert is_legal_move(board(), Coordinate(3, 3), Action.STAY, blocked) is True


def test_legal_moves_exclude_barriered_neighbours() -> None:
    blocked = blocked_cells(Coordinate(2, 3), Coordinate(3, 4))
    assert legal_moves(board(), Coordinate(3, 3), blocked) == (
        Action.SOUTH,
        Action.WEST,
        Action.STAY,
    )


def test_legal_moves_without_barriers_match_board_only() -> None:
    assert legal_moves(board(), Coordinate(3, 3)) == (
        Action.NORTH,
        Action.SOUTH,
        Action.EAST,
        Action.WEST,
        Action.STAY,
    )


def test_apply_move_rejects_barriered_destination() -> None:
    blocked = blocked_cells(Coordinate(2, 3))
    with pytest.raises(MovementError, match="is not a legal move"):
        apply_move(board(), Coordinate(3, 3), Action.NORTH, blocked)


def test_apply_move_allows_free_destination_with_barriers_present() -> None:
    blocked = blocked_cells(Coordinate(2, 3))
    assert apply_move(board(), Coordinate(3, 3), Action.SOUTH, blocked) == Coordinate(4, 3)
