"""Tests for the book-defined capture conditions."""

from p2p_cop_agent.domain import (
    Action,
    BarrierField,
    Board,
    CaptureReason,
    Coordinate,
    capture_reason,
    captured_by_barrier,
    captured_by_cop,
    is_captured,
    is_trapped,
    legal_moves,
)


def board() -> Board:
    """Return a 7x7 top-left-origin board."""
    return Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def barriers_at(*cells: Coordinate) -> BarrierField:
    """Return a barrier field with the given cells placed in order."""
    field = BarrierField(max_barriers=14)
    for cell in cells:
        field = field.place(board(), cell)
    return field


def test_captured_by_cop_only_when_cells_coincide() -> None:
    assert captured_by_cop(Coordinate(3, 3), Coordinate(3, 3)) is True
    assert captured_by_cop(Coordinate(0, 0), Coordinate(3, 3)) is False


def test_captured_by_barrier_reads_thief_cell() -> None:
    field = barriers_at(Coordinate(3, 3))
    assert captured_by_barrier(Coordinate(3, 3), field) is True
    assert captured_by_barrier(Coordinate(2, 3), field) is False


def test_interior_thief_is_not_trapped() -> None:
    assert is_trapped(board(), Coordinate(3, 3), BarrierField(max_barriers=14)) is False


def test_corner_thief_with_open_neighbours_is_not_trapped() -> None:
    assert is_trapped(board(), Coordinate(0, 0), BarrierField(max_barriers=14)) is False


def test_corner_thief_is_trapped_when_on_board_neighbours_are_barriered() -> None:
    field = barriers_at(Coordinate(1, 0), Coordinate(0, 1))
    assert is_trapped(board(), Coordinate(0, 0), field) is True


def test_interior_thief_is_trapped_when_all_four_neighbours_are_barriered() -> None:
    field = barriers_at(
        Coordinate(2, 3), Coordinate(4, 3), Coordinate(3, 2), Coordinate(3, 4)
    )
    assert is_trapped(board(), Coordinate(3, 3), field) is True


def test_capture_reason_prefers_cop_on_thief() -> None:
    field = barriers_at(Coordinate(1, 0), Coordinate(0, 1))
    reason = capture_reason(board(), Coordinate(0, 0), Coordinate(0, 0), field)
    assert reason is CaptureReason.COP_ON_THIEF


def test_capture_reason_reports_barrier_on_thief() -> None:
    field = barriers_at(Coordinate(3, 3))
    reason = capture_reason(board(), Coordinate(0, 0), Coordinate(3, 3), field)
    assert reason is CaptureReason.BARRIER_ON_THIEF


def test_capture_reason_reports_trapped_thief() -> None:
    field = barriers_at(Coordinate(1, 0), Coordinate(0, 1))
    reason = capture_reason(board(), Coordinate(6, 6), Coordinate(0, 0), field)
    assert reason is CaptureReason.THIEF_TRAPPED


def test_capture_reason_is_none_when_free() -> None:
    reason = capture_reason(
        board(), Coordinate(0, 0), Coordinate(3, 3), BarrierField(max_barriers=14)
    )
    assert reason is None


def test_is_captured_matches_capture_reason() -> None:
    empty = BarrierField(max_barriers=14)
    assert is_captured(board(), Coordinate(3, 3), Coordinate(3, 3), empty) is True
    assert is_captured(board(), Coordinate(0, 0), Coordinate(3, 3), empty) is False


def test_stay_availability_does_not_prevent_trapped_capture() -> None:
    """A trapped Thief still has STAY as a legal move but is captured anyway."""
    field = barriers_at(
        Coordinate(2, 3), Coordinate(4, 3), Coordinate(3, 2), Coordinate(3, 4)
    )
    thief = Coordinate(3, 3)
    assert Action.STAY in legal_moves(board(), thief, field.cells)
    assert is_trapped(board(), thief, field) is True
    assert capture_reason(board(), Coordinate(6, 6), thief, field) is CaptureReason.THIEF_TRAPPED
