"""Transport-neutral outbound peer interface (M5-01).

``PeerTransport`` is the abstract contract an outbound transport must satisfy so a
peer can reach its opponent without knowing how the bytes travel. The FastMCP
client connector (M5-03) and any in-memory test double implement it; nothing here
imports FastMCP. The four methods mirror the exposed Option-B tools and each
returns the ``{"ok": true}`` transport acknowledgement (or raises).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from p2p_cop_agent.shared.config import JsonObject


@runtime_checkable
class PeerTransport(Protocol):
    """The outbound calls a transport exposes to reach the opponent peer."""

    def negotiate(self, message: Mapping[str, object]) -> JsonObject:
        """Send a per-match negotiation offer and return the peer's ack."""
        ...

    def receive_turn(self, message: Mapping[str, object]) -> JsonObject:
        """Deliver one public turn to the opponent and return its ack."""
        ...

    def submit_audit(self, payload: Mapping[str, object]) -> JsonObject:
        """Deliver the end-game audit to the opponent and return its ack."""
        ...

    def receive_control(self, message: Mapping[str, object]) -> JsonObject:
        """Deliver an optional control message and return its ack."""
        ...
