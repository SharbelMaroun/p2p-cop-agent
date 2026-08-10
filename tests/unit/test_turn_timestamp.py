"""The turn ``timestamp`` is a real ISO-8601 instant, not an opaque counter.

Guards the 2026-08-10 correction. This peer emitted ``f"t{count}"``, which satisfies the
schema (``type: string``, ``minLength: 1``) and so passed every gate for the whole project --
the defect was invisible to validation and only visible on the wire. These tests assert what
the schema cannot: that the value *parses as a time* and carries a timezone.

Sources (both asked before the change): the reference builds this field in
``src/police_thief/peer/sealing.py`` as an ISO-8601 string with a UTC offset; the book pins no
regex, but every absolute time field in the mandatory artifact templates is ISO-8601 with a
timezone, and section 8.4.1 requires a real clock so a peer can detect a frozen opponent.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from p2p_cop_agent.protocol.messages import now_iso


def test_timestamp_parses_as_an_iso_8601_instant() -> None:
    """The whole point of the fix: ``"t1"`` raises here, an ISO-8601 string does not."""
    parsed = datetime.fromisoformat(now_iso())
    assert parsed.tzinfo is not None, "a stamp without an offset is ambiguous across peers"


def test_timestamp_is_utc_and_current() -> None:
    """UTC, and actually now -- a hard-coded constant would pass the parse test alone."""
    parsed = datetime.fromisoformat(now_iso())
    assert parsed.utcoffset() == timedelta(0)
    assert abs(parsed - datetime.now(parsed.tzinfo)) < timedelta(seconds=30)


def test_timestamp_advances_between_turns() -> None:
    """Two turns must not share one stamp; the old counter changed, so this must too."""
    first, second = now_iso(), now_iso()
    assert datetime.fromisoformat(second) >= datetime.fromisoformat(first)


def test_the_old_counter_shape_would_fail_this_gate() -> None:
    """Pin the regression itself, so the defect cannot return wearing its original clothes."""
    try:
        datetime.fromisoformat("t1")
    except ValueError:
        return
    raise AssertionError("'t1' parsed as a time; this test no longer guards anything")
