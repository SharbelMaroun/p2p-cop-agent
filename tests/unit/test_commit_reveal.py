"""Tests for the transport-neutral commit-reveal ledger (M4-03)."""

from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.protocol import (
    CommitRevealError,
    TurnLedger,
    validate_message,
    verify_audit,
)
from tests.conformance.neutral_stub import NeutralPeer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"
CHALLENGE = "0123456789abcdef0123456789abcdef"
SECRET_KEYS = ("payload", "nonce", "position", "move", "intent", "verdict")


def public(hint: str = "closing in") -> dict:
    """Return the schema-required public turn fields."""
    return {
        "hint": hint,
        "smell_grid": {"0,0": 0.1, "1,0": 0.2, "1,1": 0.9},
        "timestamp": "2026-07-28T00:00:00Z",
    }


def hidden(step: int) -> dict:
    """Return a private commitment payload for a turn."""
    return {"step": step, "position": [step, step], "move": "N", "intent": "pursue"}


def test_full_commit_ack_reveal_audit_round_trip() -> None:
    ledger = TurnLedger("police", public_challenge=CHALLENGE)
    first = ledger.seal_turn(1, hidden(1), public("north"))
    ledger.acknowledge({"ok": True})
    second = ledger.seal_turn(2, hidden(2), public("east"))
    ledger.acknowledge({"ok": True})

    for message in (first, second):
        validate_message("turn", message)
        assert not any(key in message for key in SECRET_KEYS)

    audit = ledger.audit_payload("survival")
    assert verify_audit(audit) is True
    # An independent implementation reproduces and accepts the reveal.
    assert NeutralPeer("thief", "team-b").submit_audit(audit) == {"ok": True}


def test_public_message_hides_payload_move_and_nonce() -> None:
    ledger = TurnLedger("thief")
    message = ledger.seal_turn(0, hidden(0), public())
    assert set(message) == {"step", "sender", "commit", "hint", "smell_grid", "timestamp"}
    assert message["sender"] == "thief"
    assert ledger.records[0].payload == hidden(0)  # kept privately


def test_each_turn_uses_a_fresh_distinct_nonce() -> None:
    ledger = TurnLedger("police")
    ledger.seal_turn(1, hidden(1), public())
    ledger.seal_turn(2, hidden(2), public())
    nonces = [record.nonce for record in ledger.records]
    assert nonces[0] != nonces[1]
    assert all(len(n) == 32 for n in nonces)


def test_reused_commitment_nonce_is_rejected() -> None:
    ledger = TurnLedger("police")
    ledger.seal_turn(1, hidden(1), public(), nonce="a" * 32)
    with pytest.raises(CommitRevealError, match="reuse"):
        ledger.seal_turn(2, hidden(2), public(), nonce="a" * 32)


def test_commitment_nonce_must_not_equal_public_challenge() -> None:
    ledger = TurnLedger("police", public_challenge=CHALLENGE)
    with pytest.raises(CommitRevealError, match="public challenge"):
        ledger.seal_turn(1, hidden(1), public(), nonce=CHALLENGE)


@pytest.mark.parametrize("bad_step", [-1, True, 1.0, "1"])
def test_step_must_be_a_non_negative_integer(bad_step: object) -> None:
    with pytest.raises(CommitRevealError, match="non-negative integer"):
        TurnLedger("police").seal_turn(bad_step, hidden(1), public())


def test_step_must_strictly_advance() -> None:
    ledger = TurnLedger("police")
    ledger.seal_turn(2, hidden(2), public())
    with pytest.raises(CommitRevealError, match="strictly advance"):
        ledger.seal_turn(2, hidden(2), public())


def test_public_fields_may_not_carry_secret_keys() -> None:
    ledger = TurnLedger("police")
    with pytest.raises(CommitRevealError, match="must not include secrets"):
        ledger.seal_turn(1, hidden(1), {**public(), "nonce": "x"})


def test_acknowledge_requires_ok_response() -> None:
    ledger = TurnLedger("police")
    ledger.acknowledge({"ok": True})
    with pytest.raises(CommitRevealError, match="acknowledgement"):
        ledger.acknowledge({"ok": False})


def test_sender_must_be_a_wire_role() -> None:
    with pytest.raises(Exception, match="wire role"):
        TurnLedger("cop")


def test_verify_audit_rejects_non_reproducing_or_malformed() -> None:
    ledger = TurnLedger("police")
    ledger.seal_turn(1, hidden(1), public())
    audit = ledger.audit_payload("capture")
    audit["records"][0]["commit"] = "f" * 64
    assert verify_audit(audit) is False
    assert verify_audit({"not": "an-audit"}) is False


def test_sdk_exposes_a_turn_ledger() -> None:
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    ledger = sdk.new_turn_ledger("police", public_challenge=CHALLENGE)
    assert isinstance(ledger, TurnLedger)
    ledger.seal_turn(1, hidden(1), public())
    assert ledger.records[0].step == 1
