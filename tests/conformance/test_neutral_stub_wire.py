"""M5-03e: our client's calls, proven against an implementation sharing no code.

The loopback in `tests/integration/` drives `FastMCPClient` against our own
`build_server`; both halves read `peer.TOOL_ARGUMENTS`, so a wrong name there
would agree with itself. These tests drive the same client against the neutral
stub, whose tool and argument names are written out independently and whose
canonicalization and hashing are reimplemented from the profile.

If our client and the stub agree here, the call shapes are right for real.
"""

import asyncio
import json
from pathlib import Path

import pytest
from fastmcp import Client

from p2p_cop_agent.adapters import FastMCPClient, PeerRejectionError, TransportError
from p2p_cop_agent.protocol import TurnLedger, build_offer, terms_from_config
from tests.conformance.neutral_stub import TOOLS, NeutralPeer, commit
from tests.conformance.neutral_stub_server import build_neutral_server

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
CHALLENGE = "0123456789abcdef0123456789abcdef"
# Complete per the book-mandated pre-game content `build_offer` now enforces on our
# side (M5-04h); neutral test values, not the real team's.
IDENTITY = {
    "group_id": "neutral-group-alpha", "group_name": "Alpha", "members": ["a", "b"],
    "repos": {"cop": "https://example.test/cop", "thief": "https://example.test/thief"},
    "mcp_servers": {"cop": "https://cop.example.test/mcp"}, "llm_model": "cli-default",
    "spec": {"os": "Example OS", "cpu_type": "Example CPU", "cpu_freq_mhz": 3600, "cpu_cores": 8, "ram_gb": 32, "gpu_model": "none", "vram_gb": 0},
}


def game() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def client(peer: NeutralPeer | None = None) -> FastMCPClient:
    return FastMCPClient(build_neutral_server(peer or NeutralPeer("thief", "neutral-group-beta")))


def sealed_turn(ledger: TurnLedger, step: int) -> dict:
    public = {"hint": "near the park", "smell_grid": {"3,3": 0.9}, "timestamp": f"t{step}"}
    return ledger.seal_turn(step, {"step": step, "move": "MOVE:N", "intent": "truth"}, public)


# --- the advertised surface ---------------------------------------------------


async def _advertised(server: object) -> dict[str, list[str]]:
    async with Client(server) as session:
        tools = await session.list_tools()
    return {tool.name: list(tool.inputSchema.get("properties", {})) for tool in tools}


def test_the_wire_advertises_exactly_the_four_tools_and_their_argument_names() -> None:
    """Read the surface the way an opponent would: from the server itself."""
    server = build_neutral_server(NeutralPeer("thief", "neutral-group-beta"))
    assert asyncio.run(_advertised(server)) == {name: [arg] for name, arg in TOOLS.items()}


# --- the four calls, end to end -----------------------------------------------


def test_our_offer_is_accepted_by_a_peer_that_shares_no_code_with_us() -> None:
    peer = NeutralPeer("thief", "neutral-group-beta")
    assert client(peer).negotiate(build_offer(game(), IDENTITY)) == {"ok": True}
    assert peer.opponent_group == "neutral-group-alpha"


def test_the_stub_independently_reproduces_our_negotiation_signature() -> None:
    """Cross-implementation agreement on the signed bytes, not just the schema.

    The stub reimplements canonicalization and hashing from the profile text, so a
    match proves our construction, not a shared helper.
    """
    offer = build_offer(game(), IDENTITY, nonce=CHALLENGE)
    assert commit(offer["terms"], CHALLENGE) == offer["signature"]
    assert offer["terms"] == terms_from_config(game())


def test_our_sealed_turn_crosses_the_wire_and_is_accepted() -> None:
    ledger = TurnLedger("police", public_challenge=CHALLENGE)
    ledger.acknowledge(client().receive_turn(sealed_turn(ledger, 1)))


def test_our_audit_records_reproduce_under_the_stubs_own_hashing() -> None:
    """The end-game claim an opponent will actually recompute `[AE-19]`."""
    ledger = TurnLedger("police", public_challenge=CHALLENGE)
    for step in (1, 2, 3):
        sealed_turn(ledger, step)
    assert client().submit_audit(ledger.audit_payload("capture")) == {"ok": True}


def test_a_control_message_crosses_the_wire() -> None:
    control = {"kind": "resign", "sender": "police", "timestamp": "t1"}
    assert client().receive_control(control) == {"ok": True}


# --- the stub really is checking ----------------------------------------------


def test_a_tampered_audit_record_is_refused_by_the_stub() -> None:
    """If this passed, every test above would be proving nothing."""
    ledger = TurnLedger("police", public_challenge=CHALLENGE)
    sealed_turn(ledger, 1)
    payload = ledger.audit_payload("capture")
    payload["records"][0]["payload"]["move"] = "MOVE:S"
    with pytest.raises(TransportError, match="does not reproduce"):
        client().submit_audit(payload)


def test_a_turn_that_does_not_advance_is_refused_by_the_stub() -> None:
    peer = NeutralPeer("thief", "neutral-group-beta")
    reachable = client(peer)
    ledger = TurnLedger("police", public_challenge=CHALLENGE)
    reachable.receive_turn(sealed_turn(ledger, 2))
    replayed = {**sealed_turn(ledger, 3), "step": 2, "commit": "b" * 64}
    with pytest.raises(TransportError, match="illegal transition|protocol conflict"):
        reachable.receive_turn(replayed)


def test_receive_move_is_not_advertised_by_the_stub() -> None:
    """The withdrawn Option-B name must be absent from a neutral peer too."""
    assert "receive_move" not in TOOLS
    with pytest.raises(TransportError, match="unknown tool"):
        client().call("receive_move", {"step": 1})


def test_a_reference_style_rejection_reaches_us_as_a_transport_error() -> None:
    """Recorded, not endorsed: the classification gap `M5-14a` must close.

    The reference raises **inside** the tool on a malformed message, so its refusal
    arrives as an MCP error and our client can only read it as a transport fault --
    the retryable kind. Retrying a message the opponent will never accept burns the
    clock until the watchdog trips. `M5-14a` owns telling these apart; until then
    this test pins the behaviour honestly rather than pretending it is right.
    """
    with pytest.raises(TransportError) as caught:
        client().receive_turn({"step": 1})
    assert not isinstance(caught.value, PeerRejectionError)
