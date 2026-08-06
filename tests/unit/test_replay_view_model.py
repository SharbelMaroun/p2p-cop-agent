"""`M8-06` / `M8-06a` / `M8-08b`: the screen as data, so it can be asserted.

A Tk window cannot be checked in CI, so the screenshot in the README would otherwise rest
on someone having looked at it once. Everything the picture claims is decided here instead:
the stamp text, the stamp colour, which row is marked bad, and what the detail panel shows.

That the stored images stay regenerable is `test_replay_screenshots.py` (`M8-05d`).
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from p2p_cop_agent.replay import Replay, Verdict, load_log, parse_log
from p2p_cop_agent.replay.view_model import (
    frame_of,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "replay"


def _replay(name: str) -> Replay:
    return Replay(load_log(FIXTURES / name))


# --- M8-06 / M8-06a: a read-only snapshot of display-ready values ------------------------


def test_the_frame_is_frozen_so_rendering_cannot_write_back() -> None:
    """`M8-06a`: "the view cannot mutate game state". Guaranteed by the type, not by
    convention — a widget that tried would raise rather than corrupt a replay."""
    frame = frame_of(_replay("log_verified_ok.json"))
    with pytest.raises(dataclasses.FrozenInstanceError):
        frame.stamp = "Verified OK"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        frame.rows[0].move = "N"  # type: ignore[misc]


def test_every_field_a_widget_reads_is_a_string_or_a_primitive() -> None:
    """`M8-06`: "no widget touches domain or protocol code directly". If a domain object
    leaked into the frame a widget could reach through it, so the frame carries none."""
    frame = frame_of(_replay("log_verified_ok.json"))
    for row in frame.rows:
        for field in dataclasses.fields(row):
            assert isinstance(getattr(row, field.name), (str, int, bool)), field.name


def test_the_screen_carries_the_nonce_move_and_commit_the_book_requires() -> None:
    """Asked directly: the viewer must display "the nonce, move, and the original commit
    hash from the log entry" (p.56/142). In full, not abbreviated — the short forms are
    for the list, and a screenshot has to be checkable."""
    row = frame_of(_replay("log_verified_ok.json")).current
    assert len(row.commit) == 64 and len(row.nonce) == 32
    assert row.move in {"N", "S", "E", "W"}
    assert row.commit_short.endswith("…") and len(row.commit_short) < len(row.commit)


def test_a_record_missing_its_fields_still_renders_rather_than_crashing() -> None:
    """`M8-08c` at the view layer: the malformed log must be *displayable*, because a
    viewer that dies on it shows nothing at all where it should show `TAMPERED`."""
    log = parse_log({"records": [{"step": 1, "nonce": "a" * 32}, {"nonce": "b" * 32}]})
    frame = frame_of(Replay(log))
    assert frame.stamp == Verdict.TAMPERED.value
    assert frame.rows[1].commit == "—" and frame.rows[1].move == "—"


def test_a_record_that_is_not_an_object_at_all_still_renders() -> None:
    """The row still has to appear, marked bad, rather than taking the window down. A
    viewer that crashes on a forged log shows nothing where it should show `TAMPERED`."""
    log = parse_log({"records": [{"step": 1, "nonce": "a" * 32}, "not a record"]})
    frame = frame_of(Replay(log))
    assert len(frame.rows) == 2 and not frame.rows[1].ok
    assert frame.rows[1].step == "?" and frame.rows[1].commit == "—"


# --- M8-08b: the per-step verdict beside the match verdict ------------------------------


def test_each_row_carries_its_own_verdict_and_reason() -> None:
    """"Operator sees where a match failed" — a match-level banner alone cannot say which
    step, and that is the only question left once `:1769` has decided the match."""
    replay = _replay("log_tampered.json")
    rows = frame_of(replay).rows
    bad = next(row for row in rows if not row.ok)
    assert bad.verdict == "TAMPERED"
    assert "does not match" in bad.reason
    assert all("matches commit" in row.reason for row in rows if row.ok)


def test_the_cursor_row_is_flagged_and_follows_navigation() -> None:
    replay = _replay("log_verified_ok.json")
    replay.go_to(3)
    frame = frame_of(replay)
    assert [row.is_current for row in frame.rows].count(True) == 1
    assert frame.current.index == 3
    assert frame.position_label == "step 4 of 8"


def test_the_frame_reports_the_sequence_summary_alongside_the_verdict() -> None:
    """The structural finding rides on the same screen but in its own line, matching the
    decision in `U-032` that it is reported rather than folded into the stamp."""
    frame = frame_of(_replay("log_verified_ok.json"))
    assert frame.sequence_ok and "sequence intact" in frame.sequence_summary


def test_the_frame_names_the_file_it_came_from() -> None:
    """A verification screenshot that does not say *which log* was verified is evidence of
    nothing in particular — and rule 36's audit is over two of them."""
    frame = frame_of(_replay("log_verified_ok.json"))
    assert frame.origin.endswith("log_verified_ok.json")
    assert frame.game_id == "demo-vs-rival" and frame.sub_game == "1"
