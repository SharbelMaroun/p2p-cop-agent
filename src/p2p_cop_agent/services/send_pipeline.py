"""The one door every outgoing report goes through (`M7-08c`, `M7-04a`).

`:2096` gives the flow — Quota Manager, then Token Bucket, then DOS Detector, then Gmail —
and `M7-08c` asks that the ordering be **fail-fast**: "the first rejection stops the
request". That is not an efficiency note. Each gate has a side effect, and running a later
gate after an earlier one refused would corrupt exactly the counters the gates exist to
protect: a request rejected on quota must not consume a token, and a request with no token
must not register as a send in the DOS window, or a blocked burst would look like a
runaway loop and lock the pipeline for the wrong reason.

So `SendPipeline.attempt` returns at the first refusal and touches nothing after it.

`M7-04a` — "no service calls an external API directly" — is a property of the *call graph*,
not of this file, so `send` takes the transmitting callable rather than importing one. A
module that cannot name Gmail cannot bypass the gates to reach it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from p2p_cop_agent.services.send_gates import (
    DosDetector,
    QuotaManager,
    SendVerdict,
    TokenBucket,
)


@dataclass(frozen=True, slots=True)
class SendDecision:
    """Whether a send may proceed, and which gate refused it if not."""

    verdict: SendVerdict
    gate: str | None = None

    @property
    def allowed(self) -> bool:
        return self.verdict is SendVerdict.ALLOWED


@dataclass
class SendPipeline:
    """The three gates in the book's order, with the first refusal short-circuiting."""

    quota: QuotaManager = field(default_factory=QuotaManager)
    bucket: TokenBucket = field(default_factory=TokenBucket)
    detector: DosDetector = field(default_factory=DosDetector)

    @classmethod
    def from_match(cls, game: Mapping[str, object]) -> SendPipeline:
        """Read the rate from the signed match object (`M7-04d`) — no hard-coded limits.

        Only `requests_per_minute` has an Appendix F value (table 19, `Minimum` 30). The
        daily quota and the burst threshold are ours, so they keep their defaults rather
        than being read from a section the opponent never agreed to.
        """
        section = game.get("rate_limiter_gatekeeper")
        rate = 30
        if isinstance(section, Mapping):
            value = section.get("requests_per_minute")
            if isinstance(value, int) and not isinstance(value, bool) and value > 0:
                rate = value
        return cls(bucket=TokenBucket(rate_per_minute=rate, capacity=rate))

    def attempt(self, now: float) -> SendDecision:
        """Ask the gates, in order, stopping at the first refusal without touching the rest."""
        if not self.quota.allow(now):
            return SendDecision(SendVerdict.REJECTED_QUOTA, "quota")
        if not self.bucket.allow(now):
            return SendDecision(SendVerdict.BLOCKED_NO_TOKEN, "bucket")
        if not self.detector.allow(now):
            return SendDecision(SendVerdict.LOCKED_ANOMALY, "detector")
        return SendDecision(SendVerdict.ALLOWED)

    def send(self, transmit: Callable[[], object], now: float) -> tuple[SendDecision, object]:
        """Run the gates and, only if all three allow, transmit.

        `transmit` is injected rather than imported: this module has no way to name Gmail,
        so nothing here can reach the API except through the gates above (`M7-04a`).
        """
        decision = self.attempt(now)
        if not decision.allowed:
            return decision, None
        # Consume before transmitting. A send that raises still happened as far as the
        # provider is concerned, and a gate that only counted successes would let a
        # failing loop retry without limit — the exact runaway rule 29 is about.
        self.bucket.take(now)
        self.quota.record(now)
        self.detector.record(now)
        return decision, transmit()
