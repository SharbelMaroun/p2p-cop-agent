"""`M7-19b`: leaving before the opponent's audit turns a played game into 0/0.

The companion Thief did exactly that against `uoh-ay26` on 2026-08-11 — survived 35 steps,
wrote its log, exited, and their `submit_audit` met a 502. Their artifact said
`technical_loss`, ours said `survival`, and rule 35 scores that 0/0 for both. This side had
the identical shape and had simply never been punished for it, because every Police-role game
so far ended with *us* submitting. In the six-sub-game series this side is Police in 2/4/6.

Every case drives the window to both outcomes: a wait that can only succeed proves nothing.
"""

from __future__ import annotations

from dataclasses import dataclass

from p2p_cop_agent.adapters.post_match import (
    DEFAULT_AUDIT_WINDOW,
    audit_window_seconds,
    await_opponent_audit,
)


@dataclass(frozen=True)
class _Delivery:
    """The shape `drain` returns — only `tool` and `accepted` are read."""

    tool: str
    accepted: bool


class _Clock:
    """A clock the test advances, so nothing sleeps in real time."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += max(seconds, 0.01)


def test_an_audit_that_arrives_is_waited_for() -> None:
    clock = _Clock()

    def drain() -> list[_Delivery]:
        # Lands a little after the horizon, as a real opponent's would.
        return [_Delivery("submit_audit", True)] if clock.now > 1.0 else []

    assert await_opponent_audit(
        drain=drain, clock=clock, sleep=clock.sleep, timeout=30.0) is True


def test_a_silent_opponent_closes_the_window_rather_than_hanging() -> None:
    """Rule 6: their silence must not become our freeze."""
    clock = _Clock()
    assert await_opponent_audit(
        drain=list, clock=clock, sleep=clock.sleep, timeout=5.0) is False
    assert clock.now >= 5.0


def test_a_rejected_audit_does_not_count_as_received() -> None:
    """A tampered audit is a scored outcome, not an agreement — rule 19, not rule 36."""
    clock = _Clock()
    assert await_opponent_audit(
        drain=lambda: [_Delivery("submit_audit", False)],
        clock=clock, sleep=clock.sleep, timeout=2.0) is False


def test_other_traffic_does_not_end_the_wait() -> None:
    """A late turn or control message is not the audit we are waiting for."""
    clock = _Clock()
    assert await_opponent_audit(
        drain=lambda: [_Delivery("receive_turn", True), _Delivery("receive_control", True)],
        clock=clock, sleep=clock.sleep, timeout=2.0) is False


def test_a_zero_window_still_reports_an_audit_already_in_hand() -> None:
    assert await_opponent_audit(
        drain=lambda: [_Delivery("submit_audit", True)],
        clock=_Clock(), sleep=lambda _s: None, timeout=0.0) is True
    assert await_opponent_audit(
        drain=list, clock=_Clock(), sleep=lambda _s: None, timeout=0.0) is False


def test_the_window_comes_from_the_private_toml() -> None:
    assert audit_window_seconds({"network": {"audit_send_timeout_seconds": 90}}) == 90.0
    assert audit_window_seconds({"network": {}}) == DEFAULT_AUDIT_WINDOW
    assert audit_window_seconds({}) == DEFAULT_AUDIT_WINDOW
    assert audit_window_seconds(None) == DEFAULT_AUDIT_WINDOW


def test_a_boolean_is_not_a_timeout() -> None:
    """`True` is an `int` in Python, and a one-second window silently restores the bug."""
    assert audit_window_seconds({"network": {"audit_send_timeout_seconds": True}}) == \
        DEFAULT_AUDIT_WINDOW
