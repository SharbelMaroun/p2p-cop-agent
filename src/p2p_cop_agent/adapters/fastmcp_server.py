"""FastMCP server adapter (M5-02).

Each peer runs its OWN FastMCP server as a public mailbox: the four Option-B tools
enqueue the opponent's raw message and return the ``{"ok": true}`` transport
acknowledgement. They never validate content and never raise, so a content-based
rejection is never mistaken for a transport failure by a peer that retries on any
exception (and a tampered audit is still received, to be scored as a technical
loss rather than lost as a transport error).

**Deliberate divergence from the reference, corrected note 2026-07-31.** This
docstring previously claimed the always-ack behaviour *matched* the reference
implementation. It does not. The reference validates structurally inside the tool
-- instantiating its protocol dataclass from the input dict -- and a malformed
message raises, so the caller sees an MCP error rather than an acknowledgement.
Only game-state logic (legal move, in-bounds) is deferred to its drain.

The divergence is kept, because the stricter behaviour has a sharp edge: a
*tampered* audit is structurally well-formed but must be **scored** as a
technical loss under Appendix E rule 19, and a peer that raises risks the
opponent retrying it as a transport error instead of accepting the loss. Being
lenient inbound cannot break an opponent -- it only ever accepts more -- while
the reverse could lose a decided game. Recorded in ADR-002; the client is
correspondingly liberal about the opponent's acknowledgement shape.

Validation is decoupled: :func:`drain` feeds each queued message through the
transport-neutral :class:`~p2p_cop_agent.peer.InboundPeer` (M5-01), where a
schema/transition/audit failure is a recorded game-level outcome, not a transport
error (ADR-002). This module is the only place ``fastmcp`` enters.
"""

from __future__ import annotations

import queue
from dataclasses import dataclass, field

from fastmcp import FastMCP

from p2p_cop_agent.peer import InboundPeer
from p2p_cop_agent.protocol import ProtocolError
from p2p_cop_agent.shared.config import JsonObject


@dataclass(slots=True)
class PeerInboxes:
    """Thread-safe mailboxes filled by the MCP tools and drained by the runtime."""

    agreements: queue.Queue = field(default_factory=queue.Queue)
    turns: queue.Queue = field(default_factory=queue.Queue)
    audits: queue.Queue = field(default_factory=queue.Queue)
    controls: queue.Queue = field(default_factory=queue.Queue)


@dataclass(frozen=True, slots=True)
class Delivery:
    """The outcome of validating one drained inbox message.

    ``accepted`` is ``False`` when the peer rejected the message; ``reason`` then
    carries the deterministic ``ProtocolError`` text. A rejection is a game-level
    outcome, never a transport error: the tool already acknowledged receipt.
    """

    tool: str
    accepted: bool
    reason: str | None = None


# Inbox -> the InboundPeer tool that validates it, in drain order.
_ROUTES = (
    ("negotiate", "agreements"),
    ("receive_turn", "turns"),
    ("submit_audit", "audits"),
    ("receive_control", "controls"),
)


def build_server(inboxes: PeerInboxes, name: str = "p2p-cop") -> FastMCP:
    """Return a FastMCP server whose four tools enqueue and acknowledge."""
    mcp: FastMCP = FastMCP(name)

    @mcp.tool
    def negotiate(message: dict) -> dict:
        inboxes.agreements.put(message)
        return {"ok": True}

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        inboxes.turns.put(message)
        return {"ok": True}

    @mcp.tool
    def submit_audit(payload: dict) -> dict:
        inboxes.audits.put(payload)
        return {"ok": True}

    @mcp.tool
    def receive_control(message: dict) -> dict:
        inboxes.controls.put(message)
        return {"ok": True}

    return mcp


def _apply(peer: InboundPeer, tool: str, message: JsonObject) -> Delivery:
    try:
        peer.dispatch(tool, message)
        return Delivery(tool, accepted=True)
    except ProtocolError as exc:
        return Delivery(tool, accepted=False, reason=str(exc))


def _drain_box(box: queue.Queue, peer: InboundPeer, tool: str) -> list[Delivery]:
    """Validate every message queued in one mailbox, in arrival order."""
    results: list[Delivery] = []
    while True:
        try:
            message = box.get_nowait()
        except queue.Empty:
            return results
        results.append(_apply(peer, tool, message))


def drain(inboxes: PeerInboxes, peer: InboundPeer) -> list[Delivery]:
    """Drain every mailbox through the peer, recording accept/reject outcomes."""
    results: list[Delivery] = []
    for tool, box_name in _ROUTES:
        results.extend(_drain_box(getattr(inboxes, box_name), peer, tool))
    return results


def take_turn(inboxes: PeerInboxes, peer: InboundPeer) -> JsonObject | None:
    """Return the opponent's next *accepted* turn, or ``None`` if none is queued.

    This is the ``TakeTurn`` source the polling loop drives (M5-17). Three
    behaviours here are deliberate:

    * The other three mailboxes are drained first, so a negotiate, audit, or
      control message cannot sit behind the turn we are waiting for. Only a turn
      is returned, because only a turn advances the loop.
    * A rejected turn is **consumed and skipped**, not returned and not left in
      place. The rejection is already a recorded game outcome (ADR-002); leaving
      it queued would make the poller re-reject the same message every interval
      and starve the real turn behind it.
    * Turns are pulled one at a time and the loop **stops at the first accepted
      one**, leaving any later turns queued. A hostile peer can send several at
      once, and draining them all would discard the next step rather than play
      it.
    """
    for tool, box_name in _ROUTES:
        if box_name != "turns":
            _drain_box(getattr(inboxes, box_name), peer, tool)
    while True:
        try:
            message = inboxes.turns.get_nowait()
        except queue.Empty:
            return None
        if _apply(peer, "receive_turn", message).accepted:
            return message
