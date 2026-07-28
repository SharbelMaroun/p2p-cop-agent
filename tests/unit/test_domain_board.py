"""Tests for board geometry and boundary validation."""

import pytest

from p2p_cop_agent.domain import Board, BoardError, Coordinate


def make_board(grid_size: int = 7, start: int = 0, corner: str = "top-left") -> Board:
    """Build a board for boundary tests."""
    return Board(grid_size=grid_size, axis_start_index=start, axis_origin_corner=corner)


def test_board_indices_span_grid_size_from_start() -> None:
    board = make_board(grid_size=7, start=0)
    assert board.min_index == 0
    assert board.max_index == 6


def test_board_honors_nonzero_axis_start_index() -> None:
    board = make_board(grid_size=5, start=1)
    assert board.min_index == 1
    assert board.max_index == 5


@pytest.mark.parametrize(
    "cell",
    [Coordinate(0, 0), Coordinate(6, 6), Coordinate(0, 6), Coordinate(3, 3)],
)
def test_board_contains_cells_on_the_grid(cell: Coordinate) -> None:
    assert make_board().contains(cell) is True


@pytest.mark.parametrize(
    "cell",
    [Coordinate(-1, 0), Coordinate(0, -1), Coordinate(7, 0), Coordinate(0, 7)],
)
def test_board_excludes_cells_off_the_grid(cell: Coordinate) -> None:
    assert make_board().contains(cell) is False


def test_require_on_board_returns_the_cell_when_valid() -> None:
    board = make_board()
    assert board.require_on_board(Coordinate(6, 6)) == Coordinate(6, 6)


def test_require_on_board_rejects_off_board_cell() -> None:
    with pytest.raises(BoardError, match=r"outside board bounds \[0, 6\]"):
        make_board().require_on_board(Coordinate(7, 0))


def test_board_from_config_reads_board_and_agents_section() -> None:
    config = {
        "board_and_agents": {
            "grid_size": 9,
            "axis_start_index": 0,
            "axis_origin_corner": "top-left",
        }
    }
    board = Board.from_config(config)
    assert (board.grid_size, board.max_index, board.axis_origin_corner) == (9, 8, "top-left")


def test_board_from_config_rejects_missing_section() -> None:
    with pytest.raises(BoardError, match="missing a board_and_agents object"):
        Board.from_config({"world": {}})


@pytest.mark.parametrize("grid_size", [None, True, 7.0, "7"])
def test_board_rejects_non_integer_grid_size(grid_size: object) -> None:
    with pytest.raises(BoardError, match="grid_size must be an integer"):
        Board(grid_size=grid_size, axis_start_index=0, axis_origin_corner="top-left")  # type: ignore[arg-type]


@pytest.mark.parametrize("grid_size", [0, -1])
def test_board_rejects_non_positive_grid_size(grid_size: int) -> None:
    with pytest.raises(BoardError, match="grid_size must be at least 1"):
        make_board(grid_size=grid_size)


@pytest.mark.parametrize("corner", ["", None, 4])
def test_board_rejects_bad_origin_corner(corner: object) -> None:
    with pytest.raises(BoardError, match="axis_origin_corner must be a non-empty string"):
        Board(grid_size=7, axis_start_index=0, axis_origin_corner=corner)  # type: ignore[arg-type]
