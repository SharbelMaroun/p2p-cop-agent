"""The deadline tracker subsystem (M5-13).

The concrete subsystem behind the orchestrator's ``DeadlineTracker`` port. The
``Deadline`` and ``RetryPolicy`` primitives (M5-05) bound a single request; this
tracks the *set* of outbound requests in flight, each with its own expiry, and
enforces the two rules book §9 puts on them:

* an expired request is **reaped**, not awaited -- past its expiry it has failed, and
  the tracker drops it rather than leaving the peer waiting on it forever;
* on a declared technical loss the whole queue is **cleared**, so no orphaned pending
  request survives to be answered after the game is already lost.

It reads its expiry from the shared, signed match object (via ``RetryPolicy``), so
both peers are held to the same 30-second response bound.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from p2p_cop_agent.services.deadlines import Deadline, DeadlineError, RetryPolicy


@dataclass
class DeadlineTracker:
    """Track every outbound request under its own expiry, reaping the breached ones."""

    policy: RetryPolicy
    _pending: dict[str, Deadline] = field(default_factory=dict)

    @classmethod
    def from_match(cls, game: Mapping[str, object]) -> DeadlineTracker:
        """Read the agreed response timeout from the shared, signed match object."""
        return cls(RetryPolicy.from_match(game))

    def deadline(self, now: float) -> Deadline:
        """Open a bare deadline at ``now`` -- the ``DeadlineTracker`` port method."""
        return self.policy.deadline(now)

    def open(self, request_id: str, now: float) -> Deadline:
        """Register an outbound request under its own expiry, refusing a duplicate."""
        if request_id in self._pending:
            raise DeadlineError(f"request {request_id!r} is already pending")
        deadline = self.policy.deadline(now)
        self._pending[request_id] = deadline
        return deadline

    def close(self, request_id: str) -> None:
        """Retire a request that completed in time; unknown ids are a no-op."""
        self._pending.pop(request_id, None)

    def reap(self, now: float) -> tuple[str, ...]:
        """Return and drop every request past its expiry (M5-13a)."""
        expired = tuple(rid for rid, deadline in self._pending.items() if deadline.expired(now))
        for request_id in expired:
            del self._pending[request_id]
        return expired

    def clear(self) -> None:
        """Drop every pending request cleanly on a technical loss (M5-13b)."""
        self._pending.clear()

    @property
    def pending(self) -> tuple[str, ...]:
        """Return the ids of requests still in flight, in the order they opened."""
        return tuple(self._pending)
