"""M5-03: the FastMCP client connector reaches an opponent.

Tool surface, argument shaping, and the round trip. Fault behaviour lives in
`test_fastmcp_client_faults.py`.

Driven against an in-memory ``build_server`` (M5-03d), so no external process,
port, or tunnel is involved.
"""

from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.adapters import (
    FastMCPClient,
    PeerInboxes,
    TransportError,
    build_server,
    drain,
)
from p2p_cop_agent.peer import InboundPeer, PeerTransport

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = ROOT / "config" / "rate_limits.json"

TURN = {"step": 1, "sender": "thief", "hint": "east", "smell_grid": {"3,3": 0.9},
        "commit": "a" * 64, "timestamp": "t"}


def _peer() -> InboundPeer:
    return InboundPeer(CopSDK.from_repository(ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS))


def test_client_satisfies_the_transport_port() -> None:
    client = FastMCPClient(build_server(PeerInboxes()))
    assert isinstance(client, PeerTransport)
    transport: PeerTransport = client
    assert transport.receive_turn(TURN) == {"ok": True}


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


def test_receive_move_is_not_reachable() -> None:
    """The withdrawn Option-B name must stay unreachable in both directions."""
    with pytest.raises(TransportError, match="unknown tool"):
        FastMCPClient(build_server(PeerInboxes())).call("receive_move", TURN)


def test_an_unknown_tool_name_is_rejected_before_any_call() -> None:
    with pytest.raises(TransportError, match="unknown tool"):
        FastMCPClient(build_server(PeerInboxes())).call("not_a_tool", {})
