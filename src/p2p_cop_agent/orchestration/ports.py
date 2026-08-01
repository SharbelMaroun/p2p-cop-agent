"""The five subsystem ports the orchestrator coordinates (M5-08a).

Appendix E rule 3 names one coordinator that initialises MCP, activates the decision
module, and owns the log manager, deadline tracker, and watchdog -- and forbids any
subsystem referencing another directly. Expressing each subsystem as a ``Protocol``
here is what makes that enforceable: the gateway depends on these interfaces, every
concrete subsystem satisfies one structurally, and none needs to import a sibling.

The MCP connector's port already exists as ``peer.PeerTransport`` (M5-01), so it is
re-exported here rather than duplicated; the other four are defined below. The log
manager and deadline tracker ports are intentionally small -- their full subsystems
are M5-12 and M5-13 -- but the seams are fixed now so the gateway can be built
against them `[book §9]`.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from p2p_cop_agent.peer import PeerTransport as MCPConnector
from p2p_cop_agent.shared.config import JsonObject

__all__ = [
    "MCPConnector",
    "DecisionModule",
    "LogManager",
    "DeadlineTracker",
    "LivenessWatchdog",
]


@runtime_checkable
class DecisionModule(Protocol):
    """Decides this peer's turn. The gateway calls it; the gateway never decides."""

    def decide(self, incoming: JsonObject | None) -> tuple[JsonObject, JsonObject]:
        """Return the private payload to seal and the public fields to publish."""
        ...


@runtime_checkable
class LogManager(Protocol):
    """Records what happened, in enough detail to reconstruct the match (M5-12)."""

    def record(self, event: str, detail: JsonObject | None = None) -> None:
        """Append one structured event to the match log."""
        ...


@runtime_checkable
class DeadlineTracker(Protocol):
    """Bounds every wait, so a request past its expiry is a decision, not patience."""

    def deadline(self, now: float) -> object:
        """Open one request's deadline at ``now`` (M5-13)."""
        ...


@runtime_checkable
class LivenessWatchdog(Protocol):
    """Trips when the peer goes silent past the agreed timeout (M5-06)."""

    def heartbeat(self, now: float) -> None:
        """Record a sign of life."""
        ...

    def check(self, now: float) -> bool:
        """Return whether silence has now tripped the watchdog."""
        ...
