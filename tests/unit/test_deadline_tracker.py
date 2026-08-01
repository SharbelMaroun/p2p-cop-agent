"""M5-13: the deadline tracker subsystem.

The `Deadline`/`RetryPolicy` primitives (M5-05) bound one request; this tracks the
*set* of outbound requests in flight, each with its own expiry. Two rules matter:
an expired request is **reaped**, not awaited -- past expiry is failure, never
patience `[book §9]` -- and on a declared technical loss the whole queue is cleared
so no orphaned pending request survives.
"""

import pytest

from p2p_cop_agent.orchestration.ports import DeadlineTracker as DeadlineTrackerPort
from p2p_cop_agent.services.deadline_tracker import DeadlineTracker
from p2p_cop_agent.services.deadlines import DeadlineError

GAME = {
    "network_and_league": {"response_timeout_sec": 30},
    "rate_limiter_gatekeeper": {"max_retries": 3, "retry_backoff_sec": 5},
}


def _tracker() -> DeadlineTracker:
    return DeadlineTracker.from_match(GAME)


def test_it_satisfies_the_deadline_tracker_port() -> None:
    assert isinstance(_tracker(), DeadlineTrackerPort)


def test_every_opened_request_carries_its_own_expiry() -> None:
    tracker = _tracker()
    deadline = tracker.open("req-1", now=100.0)
    assert deadline.expires == 130.0  # 30-second agreed timeout
    assert tracker.pending == ("req-1",)


def test_a_duplicate_request_id_is_refused() -> None:
    tracker = _tracker()
    tracker.open("req-1", now=0.0)
    with pytest.raises(DeadlineError, match="already pending"):
        tracker.open("req-1", now=0.0)


def test_expired_requests_are_reaped_rather_than_awaited() -> None:
    tracker = _tracker()
    tracker.open("slow", now=0.0)  # expires at 30
    tracker.open("fresh", now=100.0)  # expires at 130
    assert tracker.reap(now=100.0) == ("slow",)
    assert tracker.pending == ("fresh",)


def test_a_completed_request_is_closed_and_no_longer_pending() -> None:
    tracker = _tracker()
    tracker.open("req-1", now=0.0)
    tracker.close("req-1")
    assert tracker.pending == ()


def test_closing_an_unknown_request_is_a_harmless_no_op() -> None:
    tracker = _tracker()
    tracker.close("never-opened")  # must not raise
    assert tracker.pending == ()


def test_the_queue_is_cleared_cleanly_on_a_technical_loss() -> None:
    tracker = _tracker()
    tracker.open("a", now=0.0)
    tracker.open("b", now=0.0)
    tracker.clear()
    assert tracker.pending == ()


def test_the_port_method_opens_a_bare_deadline() -> None:
    assert _tracker().deadline(now=100.0).expires == 130.0
