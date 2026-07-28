"""Tests for Police-turn barrier placement legality (one orthogonal step)."""

import pytest

from p2p_cop_agent.domain import BarrierError, BarrierField, Board, Coordinate


def board() -> Board:
    """Return a 7x7 top-left-origin board."""
    return Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def field() -> BarrierField:
    """Return an empty barrier field with a workable quota."""
    return BarrierField(max_barriers=14)


@pytest.mark.parametrize(
    "target",
    [Coordinate(2, 3), Coordinate(4, 3), Coordinate(3, 2), Coordinate(3, 4)],
)
def test_places_on_any_orthogonal_neighbour(target: Coordinate) -> None:
    police = Coordinate(3, 3)
    result = field().place_adjacent(board(), police, target)
    assert result.has_barrier(target)
    assert result.count == 1


def test_rejects_placement_on_police_own_cell() -> None:
    police = Coordinate(3, 3)
    with pytest.raises(BarrierError, match="Police's own cell"):
        field().place_adjacent(board(), police, police)


@pytest.mark.parametrize(
    "target",
    [Coordinate(2, 2), Coordinate(4, 4), Coordinate(3, 5), Coordinate(5, 3), Coordinate(1, 3)],
)
def test_rejects_non_adjacent_or_diagonal_targets(target: Coordinate) -> None:
    police = Coordinate(3, 3)
    with pytest.raises(BarrierError, match="one orthogonal step"):
        field().place_adjacent(board(), police, target)


def test_rejects_off_board_neighbour() -> None:
    police = Coordinate(0, 0)
    with pytest.raises(BarrierError, match="outside board bounds"):
        field().place_adjacent(board(), police, Coordinate(-1, 0))


def test_allows_barrier_on_thief_cell_when_adjacent() -> None:
    police = Coordinate(3, 2)
    thief = Coordinate(3, 3)
    result = field().place_adjacent(board(), police, thief)
    assert result.has_barrier(thief)


def test_respects_quota_and_uniqueness_through_adjacent_path() -> None:
    police = Coordinate(3, 3)
    once = field().place_adjacent(board(), police, Coordinate(2, 3))
    with pytest.raises(BarrierError, match="already placed"):
        once.place_adjacent(board(), police, Coordinate(2, 3))
