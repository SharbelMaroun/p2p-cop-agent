"""M5-14b: a dropped request costs a re-send, not the sub-game.

Appendix F table 19 carries `max_retries` and `retry_backoff_sec` as minimums, and the
deadline rule is "retry or declare a technical loss" — this peer only ever did the
second half, so one blink of a free tunnel ended a game with three permitted retries
unused. What must *not* be retried matters just as much: a peer's rejection is a decided
outcome, and re-sending it appeals a lost game as though it were a network fault.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.adapters.fastmcp_client import PeerRejectionError, TransportError
from p2p_cop_agent.orchestration.delivery import DeliveryRetry, send_turn
from p2p_cop_agent.services.deadlines import DeadlineError, RetryPolicy

MESSAGE = {"step": 1, "commit": "0" * 64}
POLICY = RetryPolicy(max_retries=3, backoff_sec=5.0, response_timeout_sec=30.0)


def _retry(clock=None) -> DeliveryRetry:
    """A policy that never really sleeps; by default its clock never advances either,
    so only the attempt count can end the loop."""
    return DeliveryRetry(POLICY, clock=clock or (lambda: 0.0), sleep=lambda _s: None)


def test_without_a_policy_the_single_attempt_behaviour_is_unchanged() -> None:
    """Every existing caller passes None, and must keep sending exactly once."""
    calls: list[object] = []
    assert send_turn(lambda m: calls.append(m) or "ack", MESSAGE, None) == "ack"
    assert len(calls) == 1


def test_a_transient_carrier_fault_is_re_sent_and_recovers() -> None:
    """The tunnel blip that lost a game: fail twice, succeed on the third attempt."""
    attempts: list[int] = []

    def flaky(message: dict) -> str:
        attempts.append(1)
        if len(attempts) < 3:
            raise TransportError("502 from the tunnel")
        return "ack"

    assert send_turn(flaky, MESSAGE, _retry()) == "ack"
    assert len(attempts) == 3


def test_the_same_sealed_bytes_go_out_every_attempt() -> None:
    """A commitment is a promise: re-sending must never re-seal (M5-11b)."""
    seen: list[dict] = []

    def flaky(message: dict) -> str:
        seen.append(dict(message))
        if len(seen) < 3:
            raise TransportError("dropped")
        return "ack"

    send_turn(flaky, MESSAGE, _retry())
    assert seen == [MESSAGE] * 3


def test_a_peer_rejection_is_never_retried() -> None:
    """M5-14a: a decided loss is not a network fault, and appealing it is not ours."""
    attempts: list[int] = []

    def rejecting(message: dict) -> str:
        attempts.append(1)
        raise PeerRejectionError("illegal move")

    with pytest.raises(PeerRejectionError):
        send_turn(rejecting, MESSAGE, _retry())
    assert len(attempts) == 1, "a rejection must not be re-sent"


def test_exhausting_the_attempts_still_ends_the_turn() -> None:
    """Patience is bounded: a peer that never answers is a technical loss, later."""
    attempts: list[int] = []

    def dead(message: dict) -> str:
        attempts.append(1)
        raise TransportError("unreachable")

    with pytest.raises(DeadlineError):
        send_turn(dead, MESSAGE, _retry())
    assert len(attempts) == POLICY.max_retries + 1 == 4


def test_a_slow_failure_is_not_retried_at_all() -> None:
    """A request that hangs to its own expiry has already spent the turn's budget;
    retrying it is what would push past the opponent's watchdog."""
    ticks = iter([0.0, 31.0, 62.0, 93.0, 124.0])
    attempts: list[int] = []

    def slow(message: dict) -> str:
        attempts.append(1)
        raise TransportError("timed out")

    with pytest.raises(DeadlineError, match="expiry"):
        send_turn(slow, MESSAGE, _retry(clock=lambda: next(ticks)))
    assert len(attempts) == 1


def test_the_policy_is_read_from_the_signed_match_object() -> None:
    """Both peers hold the same limits, so neither can grant itself a longer rope."""
    retry = DeliveryRetry.from_match({
        "rate_limiter_gatekeeper": {"max_retries": 2, "retry_backoff_sec": 1},
        "network_and_league": {"response_timeout_sec": 30},
    })
    assert retry.policy.max_retries == 2
    assert retry.policy.attempts == 3
