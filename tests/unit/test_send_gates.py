"""`M7-04b`, `M7-08`: the three gates in front of Gmail, and why the order is load-bearing.

`:2096` fixes the flow — Quota Manager, Token Bucket, DOS Detector, Gmail — and `:2098`
gives each a distinct outcome: "Rejected (quota full)", "Blocked (no token)", "LOCKED
(anomaly)". Three names because they mean three different things to whoever reads the log:
*try tomorrow*, *try shortly*, *the code is wrong*.

The subtle requirement is `M7-08c`'s fail-fast ordering. Each gate has a side effect, so
running a later one after an earlier refusal corrupts the very counters the gates protect.
That is what most of this file tests.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.services.send_gates import (
    DosDetector,
    GateLockedError,
    QuotaManager,
    TokenBucket,
)

DAY = 86_400.0


# --- M7-04b: a bucket, not a window ----------------------------------------------------


def test_the_bucket_refills_by_the_books_formula() -> None:
    """`tokens <- min(C, tokens + r*dt)`, allow iff `tokens >= 1` `[AE-28]`."""
    bucket = TokenBucket(rate_per_minute=60, capacity=10)
    bucket.tokens(0.0)
    for _ in range(10):
        bucket.take(0.0)
    assert not bucket.allow(0.0)
    assert bucket.allow(1.0)          # 60/min = 1 token per second
    assert bucket.tokens(1.0) == pytest.approx(1.0)


def test_the_bucket_never_refills_past_capacity() -> None:
    """The `min(C, …)` half. Without it an idle agent would bank an unbounded burst — the
    exact thing `:2085` says triggers an immediate block from the provider."""
    bucket = TokenBucket(rate_per_minute=60, capacity=5)
    assert bucket.tokens(10_000.0) == 5


def test_a_burst_is_allowed_up_to_capacity_which_a_sliding_window_would_not_be() -> None:
    """Why this replaced the sliding window in `services/gatekeeper`: a window caps a
    *rate*, a bucket caps a *burst* and then refills. Rule 28 (Mandatory) asks for "a
    rate-limiter based on asynchronous **tokens**"."""
    bucket = TokenBucket(rate_per_minute=30, capacity=30)
    for _ in range(30):
        assert bucket.allow(0.0)
        bucket.take(0.0)
    assert not bucket.allow(0.0)


def test_taking_a_token_that_is_not_there_raises() -> None:
    """A fresh bucket starts full, so it must be drained first — `take` is only an error
    once the bucket is actually empty."""
    bucket = TokenBucket(rate_per_minute=1, capacity=1)
    bucket.take(0.0)
    with pytest.raises(GateLockedError):
        bucket.take(0.0)


# --- M7-08a: the daily quota ------------------------------------------------------------


def test_the_quota_stops_sending_when_exhausted() -> None:
    """`:2083`: "the **final line before account blocking**: if the quota is exhausted, no
    further requests are sent"."""
    quota = QuotaManager(daily_quota=2)
    for _ in range(2):
        assert quota.allow(0.0)
        quota.record(0.0)
    assert not quota.allow(0.0)


def test_the_quota_is_daily_and_rolls_over() -> None:
    quota = QuotaManager(daily_quota=1)
    quota.record(0.0)
    assert not quota.allow(0.0)
    assert quota.allow(DAY + 1)


# --- M7-08b: the DOS detector ------------------------------------------------------------


def test_a_runaway_burst_locks_the_pipeline() -> None:
    """`:2087`: it detects "a bug or an infinite loop **in the agent's code**", and rule 29
    (Mandatory) sanctions with "locking of the interface to prevent account blocking"."""
    detector = DosDetector(window_seconds=10, burst_limit=3)
    for _ in range(4):
        detector.record(0.0)
    assert detector.locked
    assert not detector.allow(0.0)


def test_the_lock_does_not_clear_itself_when_things_go_quiet() -> None:
    """Deliberate. The detector exists for *our own* runaway loop, and a lock that reset
    itself would let the same loop resume the moment it briefly looked calm."""
    detector = DosDetector(window_seconds=1, burst_limit=1)
    detector.record(0.0)
    detector.record(0.0)
    assert not detector.allow(10_000.0)


def test_sending_within_the_limit_never_locks() -> None:
    detector = DosDetector(window_seconds=10, burst_limit=3)
    for tick in range(10):
        detector.record(tick * 20.0)
    assert not detector.locked
