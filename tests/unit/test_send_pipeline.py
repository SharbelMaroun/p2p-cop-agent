"""`M7-08c`: the three gates in the book's order, and why the order is load-bearing.

`:2096` fixes the flow — Quota Manager, Token Bucket, DOS Detector, Gmail — and the row
asks that it be **fail-fast**: "the first rejection stops the request".

That is a correctness requirement, not an optimisation. Each gate has a side effect, so
running a later one after an earlier refusal corrupts the very counters the gates exist to
protect. Most of this file tests that, not the happy path.

`test_send_gates.py` carries the individual gates.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.services.send_gates import (
    DosDetector,
    QuotaManager,
    SendVerdict,
    TokenBucket,
)
from p2p_cop_agent.services.send_pipeline import SendPipeline


def test_the_gates_run_in_the_books_order() -> None:
    """`:2096`: Quota Manager -> Token Bucket -> DOS Detector -> Gmail."""
    pipeline = SendPipeline(quota=QuotaManager(daily_quota=0))
    assert pipeline.attempt(0.0).gate == "quota"

    pipeline = SendPipeline(bucket=TokenBucket(rate_per_minute=1, capacity=0))
    assert pipeline.attempt(0.0).gate == "bucket"

    locked = DosDetector(window_seconds=1, burst_limit=0)
    locked.record(0.0)
    assert SendPipeline(detector=locked).attempt(0.0).gate == "detector"


def test_a_quota_rejection_does_not_consume_a_token() -> None:
    """The reason fail-fast is a correctness requirement and not an optimisation: a
    request refused on quota that still burned a token would throttle tomorrow's sends
    for something that never went out."""
    pipeline = SendPipeline(quota=QuotaManager(daily_quota=0))
    before = pipeline.bucket.tokens(0.0)
    pipeline.attempt(0.0)
    assert pipeline.bucket.tokens(0.0) == before


def test_a_blocked_send_does_not_register_in_the_dos_window() -> None:
    """Otherwise a legitimately throttled burst would look like a runaway loop and lock
    the pipeline for the wrong reason — a self-inflicted outage."""
    pipeline = SendPipeline(bucket=TokenBucket(rate_per_minute=1, capacity=0),
                            detector=DosDetector(window_seconds=10, burst_limit=1))
    for _ in range(5):
        pipeline.attempt(0.0)
    assert not pipeline.detector.locked


def test_an_allowed_send_transmits_and_consumes_from_every_gate() -> None:
    pipeline = SendPipeline(quota=QuotaManager(daily_quota=5))
    decision, result = pipeline.send(lambda: "sent", 0.0)
    assert decision.verdict is SendVerdict.ALLOWED and result == "sent"
    assert pipeline.quota.remaining(0.0) == 4


def test_a_refused_send_never_calls_the_transmitter() -> None:
    """`M7-04a`: nothing reaches the API except through the gates."""
    pipeline = SendPipeline(quota=QuotaManager(daily_quota=0))

    def explode() -> object:
        raise AssertionError("transmitted despite a refusal")

    decision, result = pipeline.send(explode, 0.0)
    assert decision.verdict is SendVerdict.REJECTED_QUOTA and result is None


def test_a_transmitter_that_raises_still_counts_against_the_gates() -> None:
    """A gate that only counted successes would let a failing loop retry without limit —
    exactly the runaway rule 29 exists to stop."""
    pipeline = SendPipeline(quota=QuotaManager(daily_quota=5))
    with pytest.raises(RuntimeError):
        pipeline.send(lambda: (_ for _ in ()).throw(RuntimeError("gmail down")), 0.0)
    assert pipeline.quota.remaining(0.0) == 4


def test_the_rate_comes_from_the_signed_match_object() -> None:
    """`M7-04d`: no hard-coded rate. Appendix F table 19 makes 30 a `Minimum`, so a
    negotiated higher value must be honoured rather than clamped back down."""
    pipeline = SendPipeline.from_match({"rate_limiter_gatekeeper": {"requests_per_minute": 45}})
    assert pipeline.bucket.rate_per_minute == 45
    assert SendPipeline.from_match({}).bucket.rate_per_minute == 30
