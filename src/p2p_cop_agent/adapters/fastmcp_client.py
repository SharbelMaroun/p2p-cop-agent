"""FastMCP client connector (M5-03).

The outbound half of the peer boundary: this implements
:class:`~p2p_cop_agent.peer.PeerTransport` over FastMCP so the runtime can reach
an opponent without knowing the carrier. With ``fastmcp_server`` it is one of the
only two modules that import ``fastmcp``; a guard test enforces that.

**Two failure kinds, deliberately separate (M5-03c).** ``TransportError`` means
the exchange itself failed -- unreachable host, timeout, or a reply that is not a
JSON object -- and the caller may retry or declare a technical loss.
``PeerRejectionError`` means the opponent was reached and answered, but declined the
message; that is a game-level outcome under ADR-002 and retrying it is wrong.
Collapsing the two would make a peer that legitimately refuses look like a flaky
network, which is exactly the confusion Appendix E rules 6/7 warn about.

**Stateless by construction (M5-03i).** Every call opens and closes its own
session, and ``__slots__`` leaves nowhere for per-turn state to hide, so a turn
cannot leak context into the next one.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping

from fastmcp import Client

from p2p_cop_agent.peer import TOOL_ARGUMENTS
from p2p_cop_agent.shared.config import JsonObject

# Values of a ``status`` field that an opponent uses to signal refusal.
_REFUSAL_WORDS = frozenset({"error", "failed", "failure", "rejected", "refused", "denied"})


class TransportError(RuntimeError):
    """The opponent could not be reached, or did not answer with a JSON object.

    A retryable/technical-loss condition, never a statement about game content.
    """


class PeerRejectionError(RuntimeError):
    """The opponent answered but declined the message: a game-level outcome."""


class FastMCPClient:
    """Outbound :class:`PeerTransport` over FastMCP.

    ``target`` is whatever ``fastmcp.Client`` accepts: an opponent URL in
    production, or an in-memory ``FastMCP`` server in tests. The URL comes from
    private configuration only and never from the shared match JSON (M5-03f,
    ADR-004) -- this class simply receives it and holds no opinion about where a
    caller found it.
    """

    __slots__ = ("_target", "_timeout")

    def __init__(self, target: object, *, timeout: float | None = None) -> None:
        self._target = target
        self._timeout = timeout

    # --- the four Option-B tools --------------------------------------------

    def negotiate(self, message: Mapping[str, object]) -> JsonObject:
        """Send a per-match negotiation offer and return the peer's ack."""
        return self.call("negotiate", message)

    def receive_turn(self, message: Mapping[str, object]) -> JsonObject:
        """Deliver one public turn to the opponent and return its ack."""
        return self.call("receive_turn", message)

    def submit_audit(self, payload: Mapping[str, object]) -> JsonObject:
        """Deliver the end-game audit to the opponent and return its ack."""
        return self.call("submit_audit", payload)

    def receive_control(self, message: Mapping[str, object]) -> JsonObject:
        """Deliver an optional control message and return its ack."""
        return self.call("receive_control", message)

    # --- one exchange --------------------------------------------------------

    def call(self, tool: str, argument: Mapping[str, object]) -> JsonObject:
        """Invoke one exposed tool, shaping its single wire argument (M5-03b).

        ``submit_audit`` takes ``payload``; the other three take ``message``.
        The names come from :data:`TOOL_ARGUMENTS`, so the inbound and outbound
        halves cannot drift apart.
        """
        keyword = TOOL_ARGUMENTS.get(tool)
        if keyword is None:
            raise TransportError(f"unknown tool {tool!r}")
        return self._unwrap(tool, self._exchange(tool, {keyword: dict(argument)}))

    def _exchange(self, tool: str, arguments: JsonObject) -> object:
        """Run one request/response, mapping every carrier failure to a fault."""
        try:
            return asyncio.run(self._invoke(tool, arguments))
        except Exception as exc:  # noqa: BLE001 - any carrier failure is one fault
            raise TransportError(f"{tool} failed in transport: {exc}") from exc

    async def _invoke(self, tool: str, arguments: JsonObject) -> object:
        """Open a session, call the tool, and close it again (M5-03i)."""
        request = self._request(tool, arguments)
        if self._timeout is None:
            return await request
        return await asyncio.wait_for(request, self._timeout)

    async def _request(self, tool: str, arguments: JsonObject) -> object:
        async with Client(self._target) as client:
            return await client.call_tool(tool, arguments)

    @staticmethod
    def _unwrap(tool: str, result: object) -> JsonObject:
        """Return the peer's acknowledgement, or raise the right failure kind.

        A reply that is not a JSON object is a transport fault (M5-03h): the peer
        did not speak the wire at all.

        **Liberal on the ack shape, strict on refusal.** This peer *sends*
        ``{"ok": true}``, but the wire profile never fixed what an opponent must
        send back, and the reference implementation's exact acknowledgement dict
        is not established -- it may be ``{"status": "ok"}`` or
        ``{"status": "delivered"}``. Demanding our own shape would read every
        successful delivery from such a peer as a refusal and abandon a game that
        was going fine. So any JSON object is accepted **unless** it explicitly
        signals failure, which is the only reading that is safe against an
        unknown classmate's agent.
        """
        data = getattr(result, "data", None)
        if not isinstance(data, Mapping):
            raise TransportError(f"{tool} returned no JSON object: {data!r}")
        response: JsonObject = dict(data)
        if _signals_refusal(response):
            raise PeerRejectionError(f"{tool} was declined by the opponent: {response}")
        return response


def _signals_refusal(response: Mapping[str, object]) -> bool:
    """Return whether a well-formed reply explicitly says the peer refused.

    Silence is not refusal: only an explicit ``ok: false``, a ``status`` naming a
    failure, or an ``error`` member counts.
    """
    if response.get("ok") is False:
        return True
    status = response.get("status")
    if isinstance(status, str) and status.strip().lower() in _REFUSAL_WORDS:
        return True
    return response.get("error") not in (None, "")
