"""Tests for barrier inventory, placement legality, and disclosure."""

import pytest

from p2p_cop_agent.domain import BarrierError, BarrierField, Board, Coordinate


def board() -> Board:
    """Return a 7x7 top-left-origin board."""
    return Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def test_empty_field_reports_quota_and_remaining() -> None:
    field = BarrierField(max_barriers=14)
    assert field.count == 0
    assert field.remaining == 14
    assert field.cells == frozenset()


def test_place_discloses_barrier_in_order() -> None:
    field = BarrierField(max_barriers=14)
    first = field.place(board(), Coordinate(1, 1))
    second = first.place(board(), Coordinate(2, 2))

    assert second.placements == (Coordinate(1, 1), Coordinate(2, 2))
    assert second.count == 2
    assert second.remaining == 12
    assert second.has_barrier(Coordinate(1, 1))


def test_place_returns_new_field_and_leaves_original_unchanged() -> None:
    field = BarrierField(max_barriers=14)
    field.place(board(), Coordinate(1, 1))
    assert field.count == 0


def test_place_rejects_off_board_cell() -> None:
    with pytest.raises(BarrierError, match="outside board bounds"):
        BarrierField(max_barriers=14).place(board(), Coordinate(7, 0))


def test_place_rejects_duplicate_cell() -> None:
    field = BarrierField(max_barriers=14).place(board(), Coordinate(3, 3))
    with pytest.raises(BarrierError, match="already placed at"):
        field.place(board(), Coordinate(3, 3))


def test_place_rejects_when_quota_exhausted() -> None:
    field = BarrierField(max_barriers=1).place(board(), Coordinate(0, 0))
    assert field.remaining == 0
    with pytest.raises(BarrierError, match="quota 1 is exhausted"):
        field.place(board(), Coordinate(0, 1))


@pytest.mark.parametrize("quota", [None, True, 1.0, "14", -1])
def test_constructor_rejects_bad_quota(quota: object) -> None:
    with pytest.raises(BarrierError, match="max_barriers must"):
        BarrierField(max_barriers=quota)  # type: ignore[arg-type]


def test_constructor_rejects_duplicate_placements() -> None:
    with pytest.raises(BarrierError, match="duplicate barrier"):
        BarrierField(max_barriers=14, placements=(Coordinate(1, 1), Coordinate(1, 1)))


def test_constructor_rejects_placements_over_quota() -> None:
    with pytest.raises(BarrierError, match="exceeds quota"):
        BarrierField(max_barriers=1, placements=(Coordinate(0, 0), Coordinate(0, 1)))


def test_constructor_rejects_non_coordinate_placement() -> None:
    with pytest.raises(BarrierError, match="must be a Coordinate"):
        BarrierField(max_barriers=14, placements=((1, 1),))  # type: ignore[arg-type]


def test_from_config_reads_quota() -> None:
    config = {"movement_and_barriers": {"max_barriers": 14}}
    assert BarrierField.from_config(config).max_barriers == 14


def test_from_config_rejects_missing_section() -> None:
    with pytest.raises(BarrierError, match="missing a movement_and_barriers object"):
        BarrierField.from_config({"world": {}})
