"""Tests for legal orthogonal movement and STAY."""

import pytest

from p2p_cop_agent.domain import (
    Action,
    Board,
    Coordinate,
    MovementError,
    apply_move,
    destination,
    is_legal_move,
    legal_moves,
)


def top_left_board() -> Board:
    """Return a 7x7 top-left-origin board."""
    return Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


@pytest.mark.parametrize(
    ("action", "expected"),
    [
        (Action.NORTH, Coordinate(2, 3)),
        (Action.SOUTH, Coordinate(4, 3)),
        (Action.EAST, Coordinate(3, 4)),
        (Action.WEST, Coordinate(3, 2)),
        (Action.STAY, Coordinate(3, 3)),
    ],
)
def test_top_left_deltas_move_one_cell(action: Action, expected: Coordinate) -> None:
    assert destination(top_left_board(), Coordinate(3, 3), action) == expected


@pytest.mark.parametrize(
    ("corner", "expected"),
    [
        ("top-left", Coordinate(2, 3)),
        ("bottom-left", Coordinate(4, 3)),
        ("top-right", Coordinate(2, 3)),
        ("bottom-right", Coordinate(4, 3)),
    ],
)
def test_north_direction_depends_on_vertical_origin(corner: str, expected: Coordinate) -> None:
    board = Board(grid_size=7, axis_start_index=0, axis_origin_corner=corner)
    assert destination(board, Coordinate(3, 3), Action.NORTH) == expected


@pytest.mark.parametrize(
    ("corner", "expected"),
    [
        ("top-left", Coordinate(3, 4)),
        ("top-right", Coordinate(3, 2)),
    ],
)
def test_east_direction_depends_on_horizontal_origin(corner: str, expected: Coordinate) -> None:
    board = Board(grid_size=7, axis_start_index=0, axis_origin_corner=corner)
    assert destination(board, Coordinate(3, 3), Action.EAST) == expected


def test_unsupported_origin_corner_is_rejected() -> None:
    board = Board(grid_size=7, axis_start_index=0, axis_origin_corner="middle-left")
    with pytest.raises(MovementError, match="unsupported axis_origin_corner"):
        destination(board, Coordinate(3, 3), Action.STAY)


def test_interior_cell_allows_every_action() -> None:
    assert legal_moves(top_left_board(), Coordinate(3, 3)) == (
        Action.NORTH,
        Action.SOUTH,
        Action.EAST,
        Action.WEST,
        Action.STAY,
    )


def test_corner_cell_only_allows_inward_moves_and_stay() -> None:
    assert legal_moves(top_left_board(), Coordinate(0, 0)) == (
        Action.SOUTH,
        Action.EAST,
        Action.STAY,
    )


def test_stay_is_always_legal_on_board() -> None:
    assert is_legal_move(top_left_board(), Coordinate(0, 0), Action.STAY) is True


def test_apply_move_returns_destination_when_legal() -> None:
    assert apply_move(top_left_board(), Coordinate(0, 0), Action.SOUTH) == Coordinate(1, 0)


def test_apply_move_rejects_move_off_board() -> None:
    with pytest.raises(MovementError, match=r"N from \(0, 0\) leaves the board"):
        apply_move(top_left_board(), Coordinate(0, 0), Action.NORTH)
