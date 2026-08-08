"""The replay board reconstruction: both trails, tolerant of both log shapes (`M8-15`).

Rule 9's objective-board ban binds the live interface; the replay is the book's
"Retrospective Witness" and may draw what really happened. These tests pin the data the
widget draws: our trail up to the cursor, the opponent's aligned by step, barriers read
from either repository's payload shape, and a viewer that renders rather than raises on
a strange record.
"""

from p2p_cop_agent.replay.board import board_frame
from p2p_cop_agent.replay.load import parse_log


def _our_record(step: int, position: list[int], barriers: list[list[int]]) -> dict:
    return {"commit": "c" * 64, "nonce": "n" * 32,
            "payload": {"step": step, "position": position, "barriers": barriers,
                        "state": "grid=7x7"}}


def _their_record(step: int, position: list[int]) -> dict:
    """The companion-shaped record: barriers embedded in the state string only."""
    return {"commit": "c" * 64, "nonce": "n" * 32,
            "payload": {"step": step, "position": position,
                        "state": f"grid=7x7;self={position};barriers=[[6, 6]]"}}


OURS = parse_log({"game_id": "g", "records": [
    _our_record(1, [0, 0], []),
    _our_record(2, [0, 1], []),
    _our_record(3, [0, 1], [[1, 1]]),
]}, origin="ours")

THEIRS = parse_log({"game_id": "g", "records": [
    _their_record(1, [3, 3]),
    _their_record(2, [3, 4]),
    _their_record(3, [3, 5]),
]}, origin="theirs")


def test_our_trail_grows_with_the_cursor() -> None:
    assert board_frame(OURS, 0).ours.cells == ((0, 0),)
    frame = board_frame(OURS, 2)
    assert frame.ours.cells == ((0, 0), (0, 1), (0, 1))
    assert frame.ours.current == (0, 1)


def test_barriers_are_read_from_both_log_shapes() -> None:
    """Ours carries a `barriers` list; the companion embeds them in the state string.
    The board shows the union, so the reconstruction matches what both sides knew."""
    frame = board_frame(OURS, 2, opponent=THEIRS)
    assert (1, 1) in frame.barriers, "the cop-shaped cumulative list"
    assert (6, 6) in frame.barriers, "parsed out of the thief-shaped state string"


def test_the_opponent_trail_aligns_by_step() -> None:
    frame = board_frame(OURS, 1, opponent=THEIRS)
    assert frame.theirs.cells == ((3, 3), (3, 4)), "steps 1..2 only, matching the cursor"
    assert board_frame(OURS, 1).theirs.cells == (), "no opponent log, no invented trail"


def test_grid_size_comes_from_the_state_string() -> None:
    assert board_frame(OURS, 0).grid_size == 7


def test_capture_rings_only_the_final_step() -> None:
    assert board_frame(OURS, 2, captured=True).capture_cell == (0, 1)
    assert board_frame(OURS, 1, captured=True).capture_cell is None


def test_a_damaged_record_renders_rather_than_raises() -> None:
    log = parse_log({"records": [
        {"commit": "c" * 64, "nonce": "n" * 32, "payload": {"step": 1}},
        _our_record(2, [4, 4], "not-a-list"),
    ]}, origin="damaged")
    frame = board_frame(log, 1)
    assert frame.ours.cells == ((4, 4),), "the positionless and malformed parts are skipped"
    assert frame.barriers == frozenset()
    assert frame.grid_size == 7


def test_the_caption_reports_what_is_actually_drawn() -> None:
    with_theirs = board_frame(OURS, 2, opponent=THEIRS).caption
    assert "thief trail 3 step(s)" in with_theirs
    assert "opponent log not loaded" in board_frame(OURS, 2).caption
