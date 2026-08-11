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
transport-neutral :class:`~p2p_cop_agent.peer.InboundPeer` (M5-01), where a failure is a
game-level outcome (ADR-002). Only `services.wire_log` records what arrived.
"""

from __future__ import annotations

import queue
from dataclasses import dataclass, field

from fastmcp import FastMCP

from p2p_cop_agent.peer import InboundPeer
from p2p_cop_agent.protocol import ProtocolError
from p2p_cop_agent.services import wire_log
from p2p_cop_agent.shared.config import JsonObject

# Appendix F table 19 sets `queue_depth` to 100 with status **Minimum** — "may be raised by
# agreement but never lowered". Unbounded is not "raised": a queue with no ceiling is a peer
# that a flood can drive out of memory, and rule 29 (Mandatory) requires DOS detectors
# precisely "to protect network resources".
#
# The reference leaves its inbound queues unbounded and bounds only its outbound gatekeeper.
# We bound both directions, because the inbound side is the one an opponent controls.
QUEUE_DEPTH_MINIMUM = 100


def _bounded() -> queue.Queue:
    return queue.Queue(maxsize=QUEUE_DEPTH_MINIMUM)


@dataclass(slots=True)
class PeerInboxes:
    """Thread-safe mailboxes filled by the MCP tools and drained by the runtime.

    Every mailbox is **bounded** (`M8-04c`). A full mailbox refuses the message rather than
    growing: dropping the oldest would silently discard a turn the opponent believes we
    received, and growing without limit turns a flood into an out-of-memory kill, which is a
    technical loss scored 0/0 under Table 2.
    """

    agreements: queue.Queue = field(default_factory=_bounded)
    turns: queue.Queue = field(default_factory=_bounded)
    audits: queue.Queue = field(default_factory=_bounded)
    controls: queue.Queue = field(default_factory=_bounded)

    def depths(self) -> dict[str, int]:
        """Current occupancy per mailbox — what an endurance test watches."""
        return {name: getattr(self, name).qsize()
                for name in ("agreements", "turns", "audits", "controls")}


@dataclass(frozen=True, slots=True)
class Delivery:
    """The outcome of validating one drained inbox message.

    ``accepted`` is ``False`` when the peer rejected it and ``reason`` carries the
    ``ProtocolError`` text -- a game-level outcome, never a transport error, since the tool
    already acknowledged receipt. `wire_log.delivery` records every one of these.
    """

    tool: str
    accepted: bool
    reason: str | None = None


def _enqueue(inbox: queue.Queue, message: object) -> bool:
    """Enqueue without blocking; report refusal rather than waiting.

    `put_nowait` and not `put`: a blocking put on a full mailbox would hold the MCP request
    thread until the runtime drained it, which converts a flood into a hang — and rule 6
    makes a freeze while awaiting a response a "system deadlock and loss due to timeout".
    Refusing is visible; hanging is not.
    """
    try:
        inbox.put_nowait(message)
    except queue.Full:
        return False
    return True


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
        queued = _enqueue(inboxes.agreements, message)
        wire_log.received("negotiate", message, queued=queued)
        return {"ok": True} if queued else {"ok": False, "reason": "inbox full"}

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        queued = _enqueue(inboxes.turns, message)
        wire_log.received("receive_turn", message, queued=queued)
        return {"ok": True} if queued else {"ok": False, "reason": "inbox full"}

    @mcp.tool
    def submit_audit(payload: dict) -> dict:
        queued = _enqueue(inboxes.audits, payload)
        wire_log.received("submit_audit", payload, queued=queued)
        return {"ok": True} if queued else {"ok": False, "reason": "inbox full"}

    @mcp.tool
    def receive_control(message: dict) -> dict:
        queued = _enqueue(inboxes.controls, message)
        wire_log.received("receive_control", message, queued=queued)
        return {"ok": True} if queued else {"ok": False, "reason": "inbox full"}

    return mcp


def _apply(peer: InboundPeer, tool: str, message: JsonObject) -> Delivery:
    # `wire_log.delivery` records the verdict and returns its argument. This is the only
    # place the rejection reason exists -- callers keep the verdict and drop the text, which
    # is how a refused message became indistinguishable from silence on 2026-08-11.
    try:
        peer.dispatch(tool, message)
    except ProtocolError as exc:
        return wire_log.delivery(Delivery(tool, accepted=False, reason=str(exc)))
    return wire_log.delivery(Delivery(tool, accepted=True))


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
