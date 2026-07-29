"""InboundPeer: transport-neutral routing of the four Option-B tools (M5-01)."""

import json
from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.peer import TOOL_ARGUMENTS, InboundPeer
from p2p_cop_agent.protocol import ProtocolError, TurnLedger

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = ROOT / "config" / "rate_limits.json"
CONTROL_VALID = ROOT / "shared_contract" / "fixtures" / "control_message.valid.json"


def peer() -> InboundPeer:
    return InboundPeer(CopSDK.from_repository(ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS))


def negotiate_msg(group_id: str = "group-beta") -> dict:
    terms = {
        "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.1,
        "emit_intensity": 0.9, "max_steps": 35, "barriers_max": 14,
        "setting": "New York", "hint_max_words": 15, "axis_origin_corner": "top-left",
        "axis_start_index": 0, "thief_start": [3, 3], "cop_start": [0, 0], "num_games": 6,
    }
    return {"terms": terms, "nonce": "0" * 32, "signature": "a" * 64,
            "identity": {"group_id": group_id}}


def turn_msg(step: int = 1, sender: str = "thief", digest: str = "a" * 64) -> dict:
    return {"step": step, "sender": sender, "hint": "x", "smell_grid": {"0,0": 0.9},
            "commit": digest, "timestamp": "t"}


def audit_msg(result: str = "capture") -> dict:
    ledger = TurnLedger("thief")
    public = {"hint": "x", "smell_grid": {"0,0": 0.1}, "timestamp": "t"}
    ledger.seal_turn(1, {"step": 1, "move": "N"}, public)
    return ledger.audit_payload(result)


def test_negotiate_records_opponent_and_acks() -> None:
    p = peer()
    assert p.negotiate(negotiate_msg("group-beta")) == {"ok": True}
    assert p.opponent_group == "group-beta"


def test_receive_turn_dedups_and_rejects_replay_and_conflict() -> None:
    p = peer()
    assert p.receive_turn(turn_msg(step=2)) == {"ok": True}
    assert p.receive_turn(turn_msg(step=2)) == {"ok": True}  # idempotent redelivery
    with pytest.raises(ProtocolError):
        p.receive_turn(turn_msg(step=2, digest="b" * 64))  # same step, different commit
    with pytest.raises(ProtocolError):
        p.receive_turn(turn_msg(step=1))  # does not advance past step 2


def test_submit_audit_accepts_honest_and_rejects_tamper() -> None:
    p = peer()
    audit = audit_msg("capture")
    assert p.submit_audit(audit) == {"ok": True}
    audit["records"][0]["payload"]["move"] = "S"  # field mutation breaks the commit
    with pytest.raises(ProtocolError):
        p.submit_audit(audit)


def test_receive_control_accepts_valid_and_rejects_invalid() -> None:
    p = peer()
    valid = json.loads(CONTROL_VALID.read_text(encoding="utf-8"))
    assert p.receive_control(valid) == {"ok": True}
    with pytest.raises(ProtocolError):
        p.receive_control({"not": "a-control-message"})


def test_dispatch_routes_each_tool_and_rejects_unknown() -> None:
    p = peer()
    assert p.dispatch("negotiate", negotiate_msg()) == {"ok": True}
    assert p.dispatch("receive_turn", turn_msg()) == {"ok": True}
    assert p.dispatch("submit_audit", audit_msg()) == {"ok": True}
    with pytest.raises(ProtocolError):
        p.dispatch("receive_move", {})  # not part of the Option-B profile


def test_invalid_message_is_rejected() -> None:
    with pytest.raises(ProtocolError):
        peer().negotiate({"identity": {"group_id": "x"}})  # missing terms/nonce/signature


def test_tool_arguments_match_the_profile() -> None:
    assert TOOL_ARGUMENTS == {
        "negotiate": "message", "receive_turn": "message",
        "submit_audit": "payload", "receive_control": "message",
    }
