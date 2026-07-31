"""Expose the neutral stub over a real FastMCP wire (M5-03e).

`test_conformance.py` calls :class:`NeutralPeer` directly in Python, which proves
the *rules* agree. This module puts the same stub behind an actual MCP server so
the **call shapes** can be proven too: tool names, argument names, and the JSON
that crosses the boundary.

That is the half `M5-03e` was missing. The in-memory loopback in
`tests/integration/` drives `FastMCPClient` against *our own* `build_server`, so
the two halves share `peer.TOOL_ARGUMENTS` and a typo in it would cancel out on
both sides. Here the argument names are written out independently and the
handlers come from code that imports nothing from ``p2p_cop_agent``, so agreement
means something.

Like the reference implementation, these tools **validate and raise** rather than
acknowledge-then-drain (see `ADR-002` for why this repository's own server does
the opposite), which also makes this the place where our client meets that
behaviour.
"""

from __future__ import annotations

from fastmcp import FastMCP

from tests.conformance.neutral_stub import NeutralPeer


def build_neutral_server(peer: NeutralPeer, name: str = "neutral-stub") -> FastMCP:
    """Return a FastMCP server exposing exactly the profile's four tools.

    The parameter names below are the wire argument names. They are typed out by
    hand, not imported from the runtime, which is the entire point.
    """
    mcp: FastMCP = FastMCP(name)

    @mcp.tool
    def negotiate(message: dict) -> dict:
        return peer.negotiate(message)

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        return peer.receive_turn(message)

    @mcp.tool
    def submit_audit(payload: dict) -> dict:
        return peer.submit_audit(payload)

    @mcp.tool
    def receive_control(message: dict) -> dict:
        return peer.receive_control(message)

    return mcp
