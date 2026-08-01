"""The liveness watchdog (M5-06a, M5-06b).

Book section 8.4.1 is blunt about this: an unfed watchdog is the direct path to a
hang, so overall silence past the agreed timeout must become a *decision*, never
patience. This is deliberately **not** the per-request ``Deadline`` of M5-05 --
that bounds one outbound call, while this bounds how long the whole peer may go
without a sign of life. Keeping them separate is what stops a peer that is quietly
stalled between requests from looking healthy.

The timeout is the shared, signed ``network_and_league.watchdog_timeout_sec``
(Appendix F table 19, default 60), read through the same helper the deadlines use,
so neither peer can give itself a longer rope. Time is injected: ``now`` is always a
parameter, so a trip is proven by passing a number rather than by sleeping.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from p2p_cop_agent.services.deadlines import WATCHDOG_TIMEOUT, read_limit


class WatchdogError(RuntimeError):
    """Raised when the watchdog is misconfigured or fed after it has tripped."""


@dataclass(slots=True)
class Watchdog:
    """A single liveness timer: fed by heartbeats, tripped by silence.

    ``tripped`` is sticky. Once silence has crossed the timeout the outcome is
    decided, so a late heartbeat cannot revive it -- that would let a stalled peer
    pretend nothing happened `[AE-7]`.
    """

    timeout_sec: float
    last_beat: float
    tripped: bool = field(default=False)

    @classmethod
    def started_at(cls, now: float, timeout_sec: float) -> Watchdog:
        """Open a watchdog whose clock starts at ``now``."""
        if timeout_sec <= 0:
            raise WatchdogError(f"timeout must be positive, got {timeout_sec!r}")
        return cls(timeout_sec=timeout_sec, last_beat=now)

    @classmethod
    def from_match(cls, game: Mapping[str, object], now: float) -> Watchdog:
        """Read the agreed watchdog timeout out of the shared, signed match object."""
        return cls.started_at(now, read_limit(game, *WATCHDOG_TIMEOUT))

    def heartbeat(self, now: float) -> None:
        """Record a sign of life, or refuse if the watchdog has already tripped."""
        if self.tripped:
            raise WatchdogError("cannot feed a watchdog that has already tripped")
        self.last_beat = now

    def silent_for(self, now: float) -> float:
        """Return how long it has been since the last heartbeat, never negative."""
        return max(0.0, now - self.last_beat)

    def expired(self, now: float) -> bool:
        """Return whether silence has reached the timeout. The boundary is expired."""
        return self.silent_for(now) >= self.timeout_sec

    def check(self, now: float) -> bool:
        """Trip on first expiry and report whether the watchdog is now tripped."""
        if not self.tripped and self.expired(now):
            self.tripped = True
        return self.tripped
