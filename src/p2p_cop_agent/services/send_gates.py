"""The three gates every outgoing report passes before Gmail (`M7-08`).

`inst/police_thief_p2p_Summary.md:2096` fixes the order and it is not ours to rearrange:

    Outgoing report -> Quota Manager -> Token Bucket -> DOS Detector -> Gmail API

with a distinct outcome at each (`:2098`): "Rejected (quota full)", "Blocked (no token)",
"LOCKED (anomaly)". Three names, because they mean three different things to whoever
reads the log afterwards — *try tomorrow*, *try shortly*, and *something is wrong with
the code*.

**Quota Manager** (`:2083`) — "A counter that tracks the number of operations performed
in a given day and prevents crossing the daily threshold. This is the **final line before
account blocking**: if the quota is exhausted, no further requests are sent."

**Token Bucket** (`:2085`, rule 28 Mandatory) — "Every report requires a 'token' valid
for a defined time window; the absence of a token blocks the transmission. This prevents
**bursts** that could trigger an immediate block from the provider." The burst clause is
why this had to be a bucket and not the sliding window already in `services/gatekeeper`:
a window caps a rate, a bucket caps a *burst* and then refills. The book is explicit that
`token` here never means a language-model token.

**DOS Detector** (`:2087`, rule 29 Mandatory) — "Identifies patterns of excessive sending
that indicate **a bug or an infinite loop in the agent's code**. Upon identifying such a
pattern, the Gatekeeper **completely locks access** to the API." Rule 29's sanction is
"locking of the interface to prevent account blocking". Note what it is *for*: not a
hostile peer, but our own runaway loop. So its lock is deliberately **not** self-clearing
— a detector that reset itself would let the same loop resume the moment it looked calm.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

# Appendix F table 19 `Minimum` values, and the only numbers here with book authority.
DEFAULT_REQUESTS_PER_MINUTE = 30
# Not in Appendix F: the book names a "daily threshold" without fixing it (`:2083`), and
# Gmail's own free-tier ceiling is the real constraint. Ours, and configurable.
DEFAULT_DAILY_QUOTA = 100
# Likewise ours: "excessive sending that indicates a bug or an infinite loop" is a
# behaviour, not a number.
DEFAULT_BURST_WINDOW_SECONDS = 10.0
DEFAULT_BURST_LIMIT = 12


class SendVerdict(StrEnum):
    """Why a send did or did not go out. Three refusals, because they differ in remedy."""

    ALLOWED = "allowed"
    REJECTED_QUOTA = "rejected_quota"      # try tomorrow
    BLOCKED_NO_TOKEN = "blocked_no_token"  # try shortly
    LOCKED_ANOMALY = "locked_anomaly"      # the code is wrong; a human must look


class GateLockedError(RuntimeError):
    """Raised when the pipeline is locked. Deliberately not catchable-and-ignorable."""


@dataclass
class QuotaManager:
    """`M7-08a`: a per-day counter, the last line before the provider blocks the account."""

    daily_quota: int = DEFAULT_DAILY_QUOTA
    _used: int = 0
    _day: int | None = None

    def _roll(self, now: float) -> None:
        day = int(now // 86_400)
        if self._day != day:
            self._day, self._used = day, 0

    def remaining(self, now: float) -> int:
        self._roll(now)
        return max(0, self.daily_quota - self._used)

    def allow(self, now: float) -> bool:
        return self.remaining(now) > 0

    def record(self, now: float) -> None:
        self._roll(now)
        self._used += 1


@dataclass
class TokenBucket:
    """`M7-04b`: `tokens <- min(C, tokens + r*dt)`, allow iff `tokens >= 1` `[AE-28]`.

    Capacity is what makes this a bucket rather than a rate: it permits a burst up to
    `capacity` and then refills at `rate_per_minute`, which is precisely the shape
    `:2085` describes preventing at the provider.
    """

    rate_per_minute: float = DEFAULT_REQUESTS_PER_MINUTE
    capacity: float = DEFAULT_REQUESTS_PER_MINUTE
    _tokens: float | None = None
    _last: float | None = None

    def tokens(self, now: float) -> float:
        if self._tokens is None or self._last is None:
            self._tokens, self._last = self.capacity, now
            return self._tokens
        elapsed = max(0.0, now - self._last)
        self._tokens = min(self.capacity, self._tokens + (self.rate_per_minute / 60.0) * elapsed)
        self._last = now
        return self._tokens

    def allow(self, now: float) -> bool:
        return self.tokens(now) >= 1.0

    def take(self, now: float) -> None:
        if not self.allow(now):
            raise GateLockedError("no token available")
        self._tokens = (self._tokens or 0.0) - 1.0


@dataclass
class DosDetector:
    """`M7-08b`: catches our own runaway loop and locks the pipeline `[AE-29]`."""

    window_seconds: float = DEFAULT_BURST_WINDOW_SECONDS
    burst_limit: int = DEFAULT_BURST_LIMIT
    _sends: list[float] = field(default_factory=list)
    locked: bool = False

    def record(self, now: float) -> None:
        self._sends = [t for t in self._sends if now - t < self.window_seconds]
        self._sends.append(now)
        if len(self._sends) > self.burst_limit:
            self.locked = True

    def allow(self, now: float) -> bool:
        """Locked stays locked. A self-clearing detector would let the same infinite loop
        resume the moment it briefly looked calm, which is the failure it exists to stop."""
        del now
        return not self.locked
