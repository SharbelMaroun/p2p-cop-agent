"""Tests for the receive-side turn intake guards (M4-04)."""

from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.protocol import (
    ConflictError,
    Intake,
    ReplayError,
    TurnInbox,
    TurnLedger,
)
from tests.conformance.neutral_stub import NeutralPeer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"


def public(hint: str = "closing in") -> dict:
    """Return the schema-required public turn fields."""
    return {"hint": hint, "smell_grid": [[0.0, 0.1], [0.2, 0.9]], "timestamp": "2026-07-28T00:00:00Z"}


def hidden(step: int) -> dict:
    """Return a private commitment payload for a turn."""
    return {"step": step, "position": [step, step], "move": "N", "intent": "flee"}


def sealed(ledger: TurnLedger, step: int) -> dict:
    """Seal one turn and return its public wire message."""
    return ledger.seal_turn(step, hidden(step), public())


def test_first_delivery_is_admitted_as_fresh() -> None:
    inbox = TurnInbox()
    message = sealed(TurnLedger("thief"), 1)
    result = inbox.admit(message)
    assert isinstance(result, Intake)
    assert (result.sender, result.step, result.fresh) == ("thief", 1, True)
    assert result.commit == message["commit"]


def test_identical_redelivery_is_idempotent_and_not_reapplied() -> None:
    inbox = TurnInbox()
    message = sealed(TurnLedger("thief"), 1)
    first = inbox.admit(message)
    second = inbox.admit(dict(message))
    assert first.fresh is True
    assert second.fresh is False
    assert second.commit == first.commit


def test_same_step_different_commit_is_a_conflict() -> None:
    inbox = TurnInbox()
    ledger = TurnLedger("thief")
    inbox.admit(sealed(ledger, 1))
    forged = {**sealed(TurnLedger("thief"), 1), "commit": "f" * 64}
    with pytest.raises(ConflictError, match="conflicting commit"):
        inbox.admit(forged)


def test_non_advancing_step_is_a_replay() -> None:
    inbox = TurnInbox()
    ledger = TurnLedger("thief")
    inbox.admit(sealed(ledger, 1))
    inbox.admit(sealed(ledger, 3))
    stale = sealed(TurnLedger("thief"), 2)  # 2 <= last seen (3)
    with pytest.raises(ReplayError, match="does not advance"):
        inbox.admit(stale)


def test_seen_step_conflict_is_checked_before_replay() -> None:
    inbox = TurnInbox()
    ledger = TurnLedger("thief")
    inbox.admit(sealed(ledger, 2))
    # Same step (also non-advancing) but a different commit: a conflict wins over
    # the replay guard because the exact key was already recorded.
    forged = {**sealed(TurnLedger("thief"), 2), "commit": "a" * 64}
    with pytest.raises(ConflictError, match="conflicting commit"):
        inbox.admit(forged)


def test_two_senders_advance_independently() -> None:
    inbox = TurnInbox()
    inbox.admit(sealed(TurnLedger("police"), 5))
    # A fresh sender starting at step 1 is not a replay of the other sender.
    result = inbox.admit(sealed(TurnLedger("thief"), 1))
    assert result.fresh is True


def test_malformed_message_is_rejected_before_intake() -> None:
    inbox = TurnInbox()
    with pytest.raises(ValueError):  # ProtocolError from schema validation
        inbox.admit({"step": 1, "sender": "thief"})  # missing commit + public fields


def test_inbox_matches_the_independent_peer_semantics() -> None:
    inbox = TurnInbox()
    peer = NeutralPeer("police", "team-b")
    ledger = TurnLedger("thief")
    first = sealed(ledger, 1)
    assert inbox.admit(first).fresh is True
    assert peer.receive_turn(dict(first)) == {"ok": True}
    # Both accept an identical redelivery.
    assert inbox.admit(dict(first)).fresh is False
    assert peer.receive_turn(dict(first)) == {"ok": True}


def test_sdk_exposes_a_turn_inbox() -> None:
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    inbox = sdk.new_turn_inbox()
    assert isinstance(inbox, TurnInbox)
    result = inbox.admit(sealed(TurnLedger("thief"), 0))
    assert result.step == 0 and result.fresh is True
