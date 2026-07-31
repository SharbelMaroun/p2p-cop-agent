"""M5-03: the FastMCP client connector reaches an opponent and maps faults.

Driven against an in-memory ``build_server`` (M5-03d), so no external process,
port, or tunnel is involved. The transport-neutral core stays FastMCP-free; this
suite is the only place both sides meet.
"""

from pathlib import Path

import pytest
from fastmcp import FastMCP

from p2p_cop_agent import CopSDK
from p2p_cop_agent.adapters import (
    FastMCPClient,
    PeerInboxes,
    PeerRejectionError,
    TransportError,
    build_server,
    drain,
)
from p2p_cop_agent.peer import InboundPeer, PeerTransport

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = ROOT / "config" / "rate_limits.json"
SRC = ROOT / "src" / "p2p_cop_agent"

TURN = {"step": 1, "sender": "thief", "hint": "east", "smell_grid": {"3,3": 0.9},
        "commit": "a" * 64, "timestamp": "t"}


def _peer() -> InboundPeer:
    return InboundPeer(CopSDK.from_repository(ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS))


# --- M5-03a: it is a PeerTransport -----------------------------------------


def test_client_satisfies_the_transport_port() -> None:
    client = FastMCPClient(build_server(PeerInboxes()))
    assert isinstance(client, PeerTransport)
    transport: PeerTransport = client
    assert transport.receive_turn(TURN) == {"ok": True}


# --- M5-03b/d: argument shaping proven by where each message lands ----------


def test_each_tool_delivers_to_its_own_inbox_with_the_right_argument_name() -> None:
    """Wrong argument name would fail the call, so arrival proves the shape.

    ``submit_audit`` takes ``payload``; the other three take ``message``.
    """
    inboxes = PeerInboxes()
    client = FastMCPClient(build_server(inboxes))

    assert client.negotiate({"a": 1}) == {"ok": True}
    assert client.receive_turn({"b": 2}) == {"ok": True}
    assert client.submit_audit({"c": 3}) == {"ok": True}
    assert client.receive_control({"d": 4}) == {"ok": True}

    assert inboxes.agreements.get_nowait() == {"a": 1}
    assert inboxes.turns.get_nowait() == {"b": 2}
    assert inboxes.audits.get_nowait() == {"c": 3}
    assert inboxes.controls.get_nowait() == {"d": 4}


def test_a_sent_turn_survives_the_round_trip_and_validates_on_drain() -> None:
    """End-to-end: client sends, server mailboxes, drain validates through the SDK."""
    inboxes = PeerInboxes()
    FastMCPClient(build_server(inboxes)).receive_turn(TURN)
    results = drain(inboxes, _peer())
    assert [(d.tool, d.accepted) for d in results] == [("receive_turn", True)]


# --- M5-03c: transport fault vs game-level rejection ------------------------


def test_a_non_ok_response_is_a_peer_rejection_not_a_transport_fault() -> None:
    """A reached peer that declines is a game outcome (`ADR-002`), not a fault."""
    mcp: FastMCP = FastMCP("rejecting-peer")

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        return {"ok": False, "reason": "illegal move"}

    with pytest.raises(PeerRejectionError) as caught:
        FastMCPClient(mcp).receive_turn(TURN)
    assert not isinstance(caught.value, TransportError)
    assert "illegal move" in str(caught.value)
    # Neither inherits the other, so `except TransportError` can never swallow a
    # rejection and silently turn a lost game into a retry.
    assert not issubclass(PeerRejectionError, TransportError)
    assert not issubclass(TransportError, PeerRejectionError)


# --- M5-03g/h: unreachable and malformed peers ------------------------------


def test_an_unreachable_opponent_raises_a_transport_fault() -> None:
    client = FastMCPClient("http://127.0.0.1:1/mcp", timeout=5.0)
    with pytest.raises(TransportError):
        client.receive_turn(TURN)


def test_a_response_that_is_not_a_json_object_is_a_transport_fault() -> None:
    mcp: FastMCP = FastMCP("malformed-peer")

    @mcp.tool
    def receive_turn(message: dict) -> str:
        return "not-an-object"

    with pytest.raises(TransportError):
        FastMCPClient(mcp).receive_turn(TURN)


def test_an_unknown_tool_name_is_rejected_before_any_call() -> None:
    with pytest.raises(TransportError, match="unknown tool"):
        FastMCPClient(build_server(PeerInboxes())).call("not_a_tool", {})


# --- M5-03i: stateless between calls ----------------------------------------


def test_the_client_keeps_no_session_state_between_calls() -> None:
    """__slots__ makes hidden per-turn state impossible, not merely absent."""
    inboxes = PeerInboxes()
    client = FastMCPClient(build_server(inboxes))
    client.receive_turn(TURN)
    client.receive_turn(TURN | {"step": 2})

    assert not hasattr(client, "__dict__")
    assert set(FastMCPClient.__slots__) == {"_target", "_timeout"}
    assert inboxes.turns.qsize() == 2


# --- M5-03j: the guard -------------------------------------------------------


def test_only_the_adapters_package_imports_fastmcp() -> None:
    offenders = [
        path.relative_to(SRC)
        for path in SRC.rglob("*.py")
        if path.parent.name != "adapters"
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip().lower().startswith(("import fastmcp", "from fastmcp"))
    ]
    assert offenders == []
