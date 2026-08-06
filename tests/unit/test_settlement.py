"""`M7-06`, `M7-18`: audit first, then agree — and never report a result we do not hold.

Rule 36 (Mandatory) does not merely require an audit, it fixes its **position**: "Perform
a comprehensive mutual audit log at the end of every game. Sanction: **Mandatory condition
before agreement on the JSON result**."

The subtle part is that two sanctions punish different people, and conflating them is
expensive. Rule 19: a technical mismatch at audit is an "iron rule" scoring 0 for **the
falsifying group** — one side. Rule 35: a conflicting report scores 0 for **both teams**.
So catching an opponent's forgery is not a reason to race them to the lecturer with our
own number; that converts their loss into a shared one.
"""

from __future__ import annotations

import hashlib

import pytest

from p2p_cop_agent.orchestration.settlement import (
    Settled,
    SettlementError,
    agree,
    audit_series,
    require_reportable,
    settlement_record,
)
from p2p_cop_agent.protocol.commit import canonical_payload_bytes


def _sealed(step: int, move: str, nonce: str) -> dict:
    payload = {"step": step, "move": move}
    commit = hashlib.sha256(canonical_payload_bytes(payload) + b"|" + nonce.encode()).hexdigest()
    return {"payload": payload, "nonce": nonce, "commit": commit}


def _reveal(sub_game: int, *, tamper: bool = False) -> dict:
    records = [_sealed(1, "N", "a" * 32), _sealed(2, "E", "b" * 32)]
    if tamper:
        records[1] = {**records[1], "payload": {"step": 2, "move": "S"}}
    return {
        "sub_game": sub_game,
        "payload": {"sender": "thief", "records": records, "result_claim": "capture"},
    }


# --- M7-06a: the audit runs over every sub-game -----------------------------------------


def test_a_clean_series_passes_and_names_its_sub_games() -> None:
    audit = audit_series([_reveal(1), _reveal(2)])
    assert audit.passed and audit.sub_games == (1, 2)


def test_a_tampered_sub_game_fails_the_series_and_is_named() -> None:
    """Rule 19: "reject any game technical mismatch during the audit phase. Sanction: iron
    rule; score of 0 for the falsifying group"."""
    audit = audit_series([_reveal(1), _reveal(2, tamper=True)])
    assert not audit.passed and audit.failed_at == 2


def test_an_empty_series_does_not_pass_by_default() -> None:
    """Auditing nothing must not read as auditing successfully — the commonest way an
    audit gate is bypassed is by never running it."""
    assert not audit_series([]).passed


# --- M7-18a: agreement follows the audit, structurally ----------------------------------


def test_agreement_is_refused_when_the_audit_did_not_pass() -> None:
    """Rule 36 makes the audit "a mandatory condition before agreement", so an unpassed
    audit is refused *here* rather than checked by the caller. A precondition a caller can
    forget is not a precondition."""
    failed = audit_series([_reveal(1, tamper=True)])
    assert agree(failed, "capture", "capture").state is Settled.AUDIT_FAILED


def test_two_matching_outcomes_agree() -> None:
    passed = audit_series([_reveal(1)])
    settled = agree(passed, "capture", "capture")
    assert settled.state is Settled.AGREED and settled.reportable


# --- M7-18b: a disagreement is recorded, not smoothed over -------------------------------


def test_two_different_outcomes_are_a_conflict_and_both_are_kept() -> None:
    """The temptation is to adopt their number to keep the peace. That files a result we
    do not believe; keeping both visible is what an auditor needs afterwards."""
    settled = agree(audit_series([_reveal(1)]), "capture", "survival")
    assert settled.state is Settled.CONFLICT
    assert settled.ours == "capture" and settled.theirs == "survival"


def test_a_silent_peer_is_its_own_state_not_an_agreement() -> None:
    """Silence is not consent. Treating a missing reply as agreement would let a peer that
    crashed decide our report for us."""
    assert agree(audit_series([_reveal(1)]), "capture", None).state is Settled.UNANSWERED


def test_the_record_keeps_both_claims_for_the_log() -> None:
    record = settlement_record(agree(audit_series([_reveal(1)]), "capture", "survival"))
    assert record["our_outcome"] == "capture" and record["their_outcome"] == "survival"
    assert record["state"] == "conflict" and record["audit_passed"] is True


# --- M7-18c / M7-06c: only an agreed result may be reported ------------------------------


def test_only_an_agreed_settlement_is_reportable() -> None:
    passed = audit_series([_reveal(1)])
    require_reportable(agree(passed, "capture", "capture"))


def test_reporting_a_conflict_is_refused_and_says_why() -> None:
    """`M7-06c`. Rule 35: a conflicting report scores 0 for **both** teams, so sending
    ours is not a way to win the argument — it is how the argument costs us the game."""
    settled = agree(audit_series([_reveal(1)]), "capture", "survival")
    with pytest.raises(SettlementError, match="0 for BOTH teams"):
        require_reportable(settled)


def test_reporting_after_a_failed_audit_is_refused_for_a_different_reason() -> None:
    """The distinction that matters. Their forgery is *their* rule 19 loss; firing off our
    own contradicting report would turn it into a shared rule 35 loss."""
    settled = agree(audit_series([_reveal(1, tamper=True)]), "capture", "survival")
    with pytest.raises(SettlementError, match="shared one"):
        require_reportable(settled)


def test_reporting_an_unanswered_settlement_is_refused() -> None:
    settled = agree(audit_series([_reveal(1)]), "capture", None)
    with pytest.raises(SettlementError, match="nothing agreed to report"):
        require_reportable(settled)


def test_each_refusal_gives_a_different_remedy() -> None:
    """Three states, three actions: a conflict needs a human and the lecturer, an audit
    failure needs the evidence preserved, silence needs the *exchange* retried — not the
    report. One generic message would send all three down the same wrong path."""
    passed, failed = audit_series([_reveal(1)]), audit_series([_reveal(1, tamper=True)])
    messages = set()
    for settled in (agree(passed, "a", "b"), agree(failed, "a", "b"), agree(passed, "a", None)):
        with pytest.raises(SettlementError) as raised:
            require_reportable(settled)
        messages.add(str(raised.value))
    assert len(messages) == 3
