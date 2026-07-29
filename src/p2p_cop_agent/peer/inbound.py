"""Transport-neutral inbound peer handler (M5-01).

``InboundPeer`` turns the four exposed Option-B tool calls into protocol-layer
actions with no transport code: the FastMCP server adapter (M5-02) will wrap it,
but all validation, deduplication, and audit checks live in the protocol/SDK
layers it delegates to (``PS-007``). Every handler returns ``OK_RESPONSE`` or
raises a ``ProtocolError`` the adapter maps to a transport error. Deep negotiation
mismatch refusal is M5-04; deadlines/retry/watchdog are M5-05/06.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from p2p_cop_agent.protocol import OK_RESPONSE, ProtocolError, validate_message
from p2p_cop_agent.sdk import CopSDK
from p2p_cop_agent.shared.config import JsonObject

# Exposed tool -> its single wire argument name (Option-B naming discipline).
TOOL_ARGUMENTS = {
    "negotiate": "message",
    "receive_turn": "message",
    "submit_audit": "payload",
    "receive_control": "message",
}


class InboundPeer:
    """Handle inbound Option-B tool calls for one configured sub-game session."""

    def __init__(self, sdk: CopSDK) -> None:
        self._sdk = sdk
        self._inbox = sdk.new_turn_inbox()
        self.opponent_group: str | None = None
        self._dispatch: dict[str, Callable[[Mapping[str, object]], JsonObject]] = {
            "negotiate": self.negotiate,
            "receive_turn": self.receive_turn,
            "submit_audit": self.submit_audit,
            "receive_control": self.receive_control,
        }

    def negotiate(self, message: Mapping[str, object]) -> JsonObject:
        """Validate a negotiation offer and record the opponent identity.

        Deep agreement/mismatch refusal (config hashes, participant checks) is
        M5-04; here the message must only be a schema-valid ``negotiate``.
        """
        validate_message("negotiate", message)
        self.opponent_group = message["identity"].get("group_id")  # type: ignore[union-attr]
        return dict(OK_RESPONSE)

    def receive_turn(self, message: Mapping[str, object]) -> JsonObject:
        """Admit one public turn, deduplicating and rejecting replays/conflicts."""
        self._inbox.admit(message)
        return dict(OK_RESPONSE)

    def submit_audit(self, payload: Mapping[str, object]) -> JsonObject:
        """Accept an end-game audit only if it reproduces and is untampered."""
        report = self._sdk.verify_opponent_audit(payload)
        if not report.verified:
            raise ProtocolError(f"audit rejected: {report.reason}")
        return dict(OK_RESPONSE)

    def receive_control(self, message: Mapping[str, object]) -> JsonObject:
        """Validate an optional out-of-band control message."""
        validate_message("control", message)
        return dict(OK_RESPONSE)

    def dispatch(self, tool_name: str, argument: Mapping[str, object]) -> JsonObject:
        """Route one inbound tool call to its handler, rejecting unknown tools."""
        handler = self._dispatch.get(tool_name)
        if handler is None:
            raise ProtocolError(f"unknown tool {tool_name!r}")
        return handler(argument)
