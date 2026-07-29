"""Tests for end-game reveal verification and the technical-loss sanction (M4-05)."""

from pathlib import Path

from p2p_cop_agent import CopSDK
from p2p_cop_agent.protocol import (
    AuditVerdict,
    TurnInbox,
    TurnLedger,
    audit_reveal,
)
from tests.conformance.neutral_stub import NeutralPeer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"


def public(hint: str = "closing in") -> dict:
    """Return the schema-required public turn fields."""
    return {
        "hint": hint,
        "smell_grid": {"0,0": 0.1, "1,0": 0.2, "1,1": 0.9},
        "timestamp": "2026-07-28T00:00:00Z",
    }


def hidden(step: int) -> dict:
    """Return a private commitment payload for a turn."""
    return {"step": step, "position": [step, step], "move": "N", "intent": "flee"}


def played_ledger(steps: int = 2) -> TurnLedger:
    """Return a ledger that has sealed ``steps`` turns for the thief role."""
    ledger = TurnLedger("thief")
    for step in range(1, steps + 1):
        ledger.seal_turn(step, hidden(step), public())
    return ledger


def test_honest_reveal_is_verified() -> None:
    audit = played_ledger().audit_payload("survival")
    report = audit_reveal(audit)
    assert report.verified is True
    assert report.verdict is AuditVerdict.VERIFIED
    assert report.sender == "thief"


def test_mutated_payload_field_is_tamper() -> None:
    audit = played_ledger().audit_payload("survival")
    audit["records"][0]["payload"]["move"] = "S"  # byte/field mutation
    report = audit_reveal(audit)
    assert report.verdict is AuditVerdict.TAMPERED
    assert report.tampered_index == 0
    assert "reproduce" in report.reason


def test_mutated_commitment_nonce_is_tamper() -> None:
    audit = played_ledger().audit_payload("survival")
    audit["records"][1]["nonce"] = "b" * 32  # nonce mutation, still schema-valid
    report = audit_reveal(audit)
    assert report.verdict is AuditVerdict.TAMPERED
    assert report.tampered_index == 1


def test_swapped_commit_byte_is_tamper() -> None:
    audit = played_ledger().audit_payload("survival")
    audit["records"][0]["commit"] = "f" * 64  # commit byte mutation
    assert audit_reveal(audit).verdict is AuditVerdict.TAMPERED


def test_malformed_payload_is_tamper_not_a_crash() -> None:
    report = audit_reveal({"not": "an-audit"})
    assert report.verdict is AuditVerdict.TAMPERED
    assert report.sender is None
    assert "malformed" in report.reason


def test_reveal_must_match_the_commits_received_live() -> None:
    ledger = played_ledger()
    inbox = TurnInbox()
    for message in _wire_turns(ledger):
        inbox.admit(message)
    live = inbox.commits_for("thief")

    honest = ledger.audit_payload("survival")
    assert audit_reveal(honest, live).verified is True

    # A reveal that self-reproduces but substitutes a different sealed record for
    # step 1 is caught only by the live cross-check.
    forged = _forged_reveal_for_step_one()
    self_consistent = audit_reveal(forged)
    assert self_consistent.verdict is AuditVerdict.VERIFIED  # each record reproduces itself
    against_live = audit_reveal(forged, live)
    assert against_live.verdict is AuditVerdict.TAMPERED
    assert against_live.tampered_index == 0


def test_reveal_with_an_extra_record_is_tamper_against_live() -> None:
    ledger = played_ledger(3)  # seals steps 1..3
    inbox = TurnInbox()
    for message in _wire_turns(ledger)[:2]:  # only steps 1..2 ever arrived live
        inbox.admit(message)
    live = inbox.commits_for("thief")

    reveal = ledger.audit_payload("survival")  # discloses all three
    report = audit_reveal(reveal, live)
    assert report.verdict is AuditVerdict.TAMPERED  # overlap matches, but a record was added
    assert report.tampered_index is None


def test_sdk_scores_a_tampered_reveal_as_zero_and_leaves_counterpart_open() -> None:
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    audit = played_ledger().audit_payload("survival")
    audit["records"][0]["nonce"] = "c" * 32

    report = sdk.verify_opponent_audit(audit)
    assert report.verdict is AuditVerdict.TAMPERED
    assert sdk.score_after_audit(report) == 0  # zero-point technical loss

    honest = played_ledger().audit_payload("survival")
    assert sdk.score_after_audit(sdk.verify_opponent_audit(honest)) is None


def test_independent_peer_also_rejects_the_tampered_reveal() -> None:
    peer = NeutralPeer("police", "team-b")
    audit = played_ledger().audit_payload("survival")
    assert peer.submit_audit(audit) == {"ok": True}  # honest reveal accepted
    audit["records"][0]["payload"]["intent"] = "pursue"
    try:
        peer.submit_audit(audit)
    except Exception as exc:  # ConformanceError: does not reproduce
        assert "reproduce" in str(exc)
    else:  # pragma: no cover - the peer must reject a tampered reveal
        raise AssertionError("neutral peer accepted a tampered reveal")


def _wire_turns(ledger: TurnLedger) -> list[dict]:
    """Rebuild the public wire messages the ledger emitted, in order."""
    return [
        {"step": record.step, "sender": ledger.sender, "commit": record.commit, **public()}
        for record in ledger.records
    ]


def _forged_reveal_for_step_one() -> dict:
    """Return a self-consistent reveal whose step-1 record is a different move."""
    ledger = TurnLedger("thief")
    ledger.seal_turn(1, {"step": 1, "position": [9, 9], "move": "S", "intent": "pursue"}, public())
    ledger.seal_turn(2, hidden(2), public())
    return ledger.audit_payload("survival")
