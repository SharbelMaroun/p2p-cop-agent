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
        # Verified opponent audits, in arrival order (`C-051`). Evidence, not a verdict:
        # every revealed payload the opponent staked its commitments on.
        self.opponent_audits: list[JsonObject] = []
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

        **The group id is read from either home, and its absence is not fatal**
        (`C-047`). This line used to be ``message["identity"].get("group_id")`` -- a bare
        subscript behind a schema that made ``identity`` required, so a peer carrying its
        group id at the top level had the whole negotiate refused and, had the schema let
        it through, would have hit a ``KeyError`` one line later. Group `yanell11` sends
        ``group_id`` top-level and no ``identity`` object at all; the refusal cost a live
        friendly on 2026-08-15. Both spellings are accepted on receive and we still send
        the full identity, which is `C-031`'s "populate ours, tolerate theirs" actually
        implemented rather than only documented.

        The value is a label for our own logs, never an authorization: nothing downstream
        trusts it, and the peer's real claim to a group is the signed terms plus
        ``agreed_between``. So ``None`` is a legitimate outcome, not a reason to refuse.
        """
        validate_message("negotiate", message)
        identity = message.get("identity")
        if isinstance(identity, Mapping):
            self.opponent_group = identity.get("group_id") or message.get("group_id")
        else:
            self.opponent_group = message.get("group_id")
        return dict(OK_RESPONSE)

    def receive_turn(self, message: Mapping[str, object]) -> JsonObject:
        """Admit one public turn, deduplicating and rejecting replays/conflicts."""
        self._inbox.admit(message)
        return dict(OK_RESPONSE)

    def submit_audit(self, payload: Mapping[str, object]) -> JsonObject:
        """Accept an end-game audit only if it reproduces and is untampered.

        **The verified payload is KEPT (`C-051`).** It used to be checked and dropped, so
        this peer recorded that an opponent's audit passed and nothing about what it said.
        On 2026-08-15 against `yanell11` that cost us the ability to answer a question the
        cryptography had already settled: their Cop claimed a capture at ``[0,5]`` while
        our own record put us at ``[0,4]``, and their revealed positions -- which had just
        passed through this very method -- were the evidence. We had thrown them away.

        Rule 19's sanction is absolute and has no appeal, so the side that cannot produce
        evidence loses the argument regardless of who was right. Their records are the
        counterpart of the log they audit from us; keeping them costs one list and makes a
        dispute answerable from our own artifacts instead of by asking the opponent.
        """
        report = self._sdk.verify_opponent_audit(payload)
        if not report.verified:
            raise ProtocolError(f"audit rejected: {report.reason}")
        self.opponent_audits.append(dict(payload))
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
