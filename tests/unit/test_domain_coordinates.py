"""Tests for the immutable board coordinate type."""

import dataclasses

import pytest

from p2p_cop_agent.domain import Coordinate, CoordinateError


def test_coordinate_stores_axes_in_config_order() -> None:
    cell = Coordinate(3, 5)
    assert cell.row == 3
    assert cell.col == 5
    assert cell.as_pair() == (3, 5)


def test_coordinate_is_hashable_and_value_equal() -> None:
    assert Coordinate(1, 2) == Coordinate(1, 2)
    assert len({Coordinate(1, 2), Coordinate(1, 2)}) == 1
    assert Coordinate(1, 2) != Coordinate(2, 1)


def test_coordinate_is_frozen() -> None:
    cell = Coordinate(0, 0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        cell.row = 1  # type: ignore[misc]


def test_coordinate_from_pair_parses_json_style_list() -> None:
    assert Coordinate.from_pair([3, 3]) == Coordinate(3, 3)
    assert Coordinate.from_pair((0, 0)) == Coordinate(0, 0)


def test_coordinate_allows_negative_axes_before_boundary_checks() -> None:
    assert Coordinate(-1, -2).as_pair() == (-1, -2)


@pytest.mark.parametrize("pair", [[1], [1, 2, 3], []])
def test_coordinate_from_pair_rejects_wrong_length(pair: list[int]) -> None:
    with pytest.raises(CoordinateError, match="must have 2 items"):
        Coordinate.from_pair(pair)


@pytest.mark.parametrize("pair", ["12", 12, None, {"row": 1}])
def test_coordinate_from_pair_rejects_non_sequence(pair: object) -> None:
    with pytest.raises(CoordinateError, match="must be a list or tuple"):
        Coordinate.from_pair(pair)


@pytest.mark.parametrize("value", [True, False, 1.0, "1", None])
def test_coordinate_rejects_non_integer_axes(value: object) -> None:
    with pytest.raises(CoordinateError, match="axis must be an integer"):
        Coordinate(value, 0)  # type: ignore[arg-type]
