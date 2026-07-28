"""Tests for start-coordinate semantic validation."""

import pytest

from p2p_cop_agent.domain import BoardError, Coordinate, validate_start_coordinates


def make_config(cop: list[int], thief: list[int], grid: int = 7, start: int = 0) -> dict:
    """Return a minimal board_and_agents config for start validation."""
    return {
        "board_and_agents": {
            "grid_size": grid,
            "axis_start_index": start,
            "axis_origin_corner": "top-left",
            "cop_start": cop,
            "thief_start": thief,
        }
    }


def test_valid_starts_return_coordinates() -> None:
    cop, thief = validate_start_coordinates(make_config([0, 0], [3, 3]))
    assert cop == Coordinate(0, 0)
    assert thief == Coordinate(3, 3)


def test_rejects_start_off_board() -> None:
    with pytest.raises(BoardError, match="outside board bounds"):
        validate_start_coordinates(make_config([0, 0], [7, 0]))


def test_rejects_identical_starts() -> None:
    with pytest.raises(BoardError, match="must be different cells"):
        validate_start_coordinates(make_config([2, 2], [2, 2]))


def test_respects_nonzero_axis_start_index() -> None:
    cop, thief = validate_start_coordinates(make_config([1, 1], [5, 5], grid=5, start=1))
    assert (cop, thief) == (Coordinate(1, 1), Coordinate(5, 5))


def test_rejects_start_below_nonzero_start_index() -> None:
    with pytest.raises(BoardError, match="outside board bounds"):
        validate_start_coordinates(make_config([0, 0], [5, 5], grid=5, start=1))


def test_rejects_missing_board_section() -> None:
    with pytest.raises(BoardError, match="missing a board_and_agents object"):
        validate_start_coordinates({"world": {}})
