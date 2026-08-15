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

**One session per sub-game, not per call (`C-049`).** Until 2026-08-15 every call
opened and closed its own MCP session, on the stated rationale that "a turn cannot leak
context into the next one" (M5-03i). Group `yanell11` measured what that costs from the
only side that can see it -- their server log -- and it is **six HTTP requests per turn**
(POST initialize, POST 202, GET stream, POST call, POST, DELETE) where one would do.
Against an opponent behind a rate-limited tunnel that is fatal *deep* in a game, once the
per-minute cap is reached: two of our sub-games stalled at steps 20 and 30 with our calls
simply ceasing to arrive, which is exactly what a 502 above the cap looks like from here.

**The old rationale conflated two things.** The guarantee worth having is that no *game*
state crosses a turn boundary, and that comes from ``__slots__`` holding only the target
and timeout plus every ``call_tool`` taking explicit arguments -- none of which a reused
*transport* connection touches. We were paying six times the request rate for a property
we already had by construction.

**A dropped session is not a lost turn.** Any carrier failure closes the session and
clears it, so the next call reconnects; combined with `orchestration/delivery.py`'s
bounded re-send, a reconnect costs one retry rather than the sub-game. ``close()`` ends
the session deliberately at settlement, and ``reuse_session=False`` restores the old
behaviour for tests that need a cold connection each time.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping

from fastmcp import Client

from p2p_cop_agent.adapters.mcp_session import ReusableSession
from p2p_cop_agent.peer import TOOL_ARGUMENTS
from p2p_cop_agent.protocol import signals_refusal
from p2p_cop_agent.shared.config import JsonObject


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

    __slots__ = ("_target", "_timeout", "_reuse", "_session")

    def __init__(self, target: object, *, timeout: float | None = None,
                 reuse_session: bool = True) -> None:
        self._target = target
        self._timeout = timeout
        self._reuse = reuse_session
        # Lifetime lives in `mcp_session.ReusableSession`; this class keeps the tool
        # surface. Constructing one opens nothing.
        self._session = ReusableSession(target)

    def close(self) -> None:
        """End the session deliberately (settlement). Safe to call repeatedly."""
        self._session.close()

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
        if not self._reuse:
            try:
                return asyncio.run(self._invoke(tool, arguments))
            except Exception as exc:  # noqa: BLE001 - any carrier failure is one fault
                raise TransportError(f"{tool} failed in transport: {exc}") from exc
        try:
            return self._session.call(tool, arguments, self._timeout)
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

        **Liberal on the ack shape, strict on refusal.** The rule itself lives in
        :func:`~p2p_cop_agent.protocol.signals_refusal`, in the transport-neutral
        layer, so this adapter and the commit-reveal ledger cannot disagree about
        what counts as delivered.
        """
        data = getattr(result, "data", None)
        if not isinstance(data, Mapping):
            raise TransportError(f"{tool} returned no JSON object: {data!r}")
        response: JsonObject = dict(data)
        if signals_refusal(response):
            raise PeerRejectionError(f"{tool} was declined by the opponent: {response}")
        return response
