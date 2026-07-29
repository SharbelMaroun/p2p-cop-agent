"""M5-02: the FastMCP server mailboxes inbound calls; drain validates them."""

import asyncio
import json
from pathlib import Path

from fastmcp import Client

from p2p_cop_agent import CopSDK
from p2p_cop_agent.adapters import PeerInboxes, build_server, drain
from p2p_cop_agent.peer import InboundPeer
from p2p_cop_agent.protocol import TurnLedger

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = ROOT / "config" / "rate_limits.json"
CONTROL_VALID = ROOT / "shared_contract" / "fixtures" / "control_message.valid.json"


def _peer() -> InboundPeer:
    return InboundPeer(CopSDK.from_repository(ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS))


def negotiate_msg() -> dict:
    terms = {
        "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.1,
        "emit_intensity": 0.9, "max_steps": 35, "barriers_max": 14,
        "setting": "New York", "hint_max_words": 15, "axis_origin_corner": "top-left",
        "axis_start_index": 0, "thief_start": [3, 3], "cop_start": [0, 0], "num_games": 6,
    }
    return {"terms": terms, "nonce": "0" * 32, "signature": "a" * 64,
            "identity": {"group_id": "group-beta"}}


def turn_msg(step: int = 1) -> dict:
    return {"step": step, "sender": "thief", "hint": "x", "smell_grid": {"0,0": 0.9},
            "commit": "a" * 64, "timestamp": "t"}


def audit_msg(tamper: bool = False) -> dict:
    ledger = TurnLedger("thief")
    ledger.seal_turn(1, {"step": 1, "move": "N"},
                     {"hint": "x", "smell_grid": {"0,0": 0.1}, "timestamp": "t"})
    payload = ledger.audit_payload("capture")
    if tamper:
        payload["records"][0]["payload"]["move"] = "S"
    return payload


async def _call_all(mcp, calls: list) -> list:
    out = []
    async with Client(mcp) as client:
        for tool, args in calls:
            out.append((await client.call_tool(tool, args)).data)
    return out


def test_every_tool_enqueues_and_acknowledges_without_validating() -> None:
    inboxes = PeerInboxes()
    acks = asyncio.run(_call_all(build_server(inboxes), [
        ("negotiate", {"message": negotiate_msg()}),
        ("receive_turn", {"message": turn_msg()}),
        ("submit_audit", {"payload": {"not": "a-real-audit"}}),  # junk still accepted
        ("receive_control", {"message": {"anything": True}}),
    ]))
    assert acks == [{"ok": True}] * 4  # a mailbox always acks
    assert (inboxes.agreements.qsize(), inboxes.turns.qsize()) == (1, 1)
    assert (inboxes.audits.qsize(), inboxes.controls.qsize()) == (1, 1)


def test_drain_validates_each_queued_message_through_the_peer() -> None:
    inboxes = PeerInboxes()
    inboxes.agreements.put(negotiate_msg())
    inboxes.turns.put(turn_msg(step=1))
    inboxes.turns.put({"bad": "turn"})  # schema-invalid
    inboxes.controls.put(json.loads(CONTROL_VALID.read_text(encoding="utf-8")))
    results = drain(inboxes, _peer())
    assert [(d.tool, d.accepted) for d in results] == [
        ("negotiate", True), ("receive_turn", True),
        ("receive_turn", False), ("receive_control", True),
    ]
    assert results[2].reason is not None


def test_tampered_audit_drains_to_a_rejection_not_a_transport_error() -> None:
    inboxes = PeerInboxes()
    inboxes.audits.put(audit_msg(tamper=True))
    results = drain(inboxes, _peer())
    assert len(results) == 1
    assert results[0].tool == "submit_audit"
    assert results[0].accepted is False and results[0].reason is not None
