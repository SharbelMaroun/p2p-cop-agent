"""M5-17f: the whole match, sequenced autonomously from negotiation to a played sub-game.

The three preamble pieces (agreement, attestation, declaration lock) and the play loop
each have their own tests; this proves ``play_match`` runs them in the book's order --
negotiate, lock the declaration, then play -- with nothing fed in by hand. The opponent
answers only through the wire shape: its offer and its turns land in our mailbox.
"""

from __future__ import annotations

import queue
from pathlib import Path

from p2p_cop_agent import CopSDK
from p2p_cop_agent.adapters import PeerInboxes, take_turn
from p2p_cop_agent.domain.scoring import Outcome
from p2p_cop_agent.orchestration.match import play_match
from p2p_cop_agent.peer import InboundPeer
from p2p_cop_agent.protocol.declaration import lock_declaration
from p2p_cop_agent.protocol.negotiation import build_offer
from tests.unit.test_negotiation_handshake import _identity
from tests.unit.test_polling import FakeClock
from tests.unit.test_turn_loop import decide

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = ROOT / "config" / "rate_limits.json"


def reply(step: int, **extra: object) -> dict:
    return {"step": step, "sender": "thief", "hint": "somewhere", "smell_grid": {"3,3": 0.9},
            "commit": "a" * 64, "timestamp": f"t{step}", **extra}


def _drain(box: queue.Queue) -> dict | None:
    try:
        return box.get_nowait()
    except queue.Empty:
        return None


class MatchPeer:
    """Answers negotiate with its offer and each turn with the next, via our mailbox."""

    def __init__(self, inboxes: PeerInboxes, offer: dict | None, *turns: dict) -> None:
        self.inboxes = inboxes
        self.offer = offer
        self.turns = list(turns)
        self.sent: list[dict] = []
        self.audits: list[dict] = []

    def negotiate(self, message: dict) -> dict:
        if self.offer is not None:
            self.inboxes.agreements.put(self.offer)
        if self.turns:  # the Thief opens once the match is agreed
            self.inboxes.turns.put(self.turns.pop(0))
        return {"ok": True}

    def receive_turn(self, message: dict) -> dict:
        self.sent.append(message)
        if self.turns:
            self.inboxes.turns.put(self.turns.pop(0))
        return {"ok": True}

    def submit_audit(self, payload: dict) -> dict:
        self.audits.append(payload)
        return {"ok": True}


def _run(*replies: dict, agree: bool = True, artifacts_dir=None):
    sdk = CopSDK.from_repository(ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    offer = build_offer(dict(sdk.game_config), _identity("neutral-group-beta")) if agree else None
    inboxes = PeerInboxes()
    peer = MatchPeer(inboxes, offer, *replies)
    ipeer = InboundPeer(sdk)
    clock = FakeClock()
    result = play_match(
        sdk=sdk, transport=peer,
        take_offer=lambda: _drain(inboxes.agreements),
        take_turn=lambda: take_turn(inboxes, ipeer),
        decide=decide, identity=_identity("neutral-group-alpha"),
        game_id="g1", game_uid="u1", started_at="2026-08-03T10:00:00Z",
        max_tokens_per_game=200000, clock=clock.time, sleep=clock.sleep,
        artifacts_dir=artifacts_dir,
    )
    return result, peer


def test_a_match_negotiates_locks_the_declaration_then_plays() -> None:
    result, peer = _run(reply(1), reply(2, claim_response={"claim": [3, 3], "caught": True}))
    assert result.played
    assert result.agreement is not None
    assert result.outcome.outcome is Outcome.CAPTURE
    assert result.declaration["game_id"] == "g1"
    # The confirming claim decides the game before our second turn exists (`M9-021a`).
    assert len(peer.sent) == 1 and peer.audits, "one turn, the claim decided, audit sent"


def test_the_declaration_is_locked_and_reproduces() -> None:
    """The lock is written before play and is a canonical hash of the declaration."""
    result, _ = _run(reply(1, claim_response={"claim": [3, 3], "caught": True}))
    assert result.declaration_lock == lock_declaration(result.declaration)
    assert len(result.declaration_lock) == 64


def test_no_agreement_means_no_declaration_and_no_play() -> None:
    """A silent opponent stops before the declaration: no lie is locked, no move made."""
    result, peer = _run(agree=False)
    assert not result.played
    assert result.agreement is None
    assert result.declaration is None and result.declaration_lock is None
    assert peer.sent == [], "no turn was ever sent"


def test_the_declaration_is_on_disk_before_the_first_move(tmp_path) -> None:
    """`M7-22`: "the pre-game declaration is signed and fixed **before play begins**".

    Proven by timing, not by presence at the end. The peer records the sends it received;
    the declaration file must already exist by the time the first one arrives, because a
    declaration written afterwards could have been edited to suit the result — which is
    exactly what locking it beforehand exists to rule out.
    """
    import json

    seen: list[bool] = []
    original = MatchPeer.receive_turn

    def spy(self, message):
        seen.append((tmp_path / "declaration_g1.json").exists())
        return original(self, message)

    MatchPeer.receive_turn = spy
    try:
        result, _ = _run(reply(1), reply(2, claim_response={"claim": [3, 3], "caught": True}),
                         artifacts_dir=tmp_path)
    finally:
        MatchPeer.receive_turn = original

    assert seen and all(seen), "a turn was sent before the declaration reached disk"
    written = json.loads((tmp_path / "declaration_g1.json").read_text("utf-8"))
    assert written["declaration_lock"] == result.declaration_lock
    assert (tmp_path / "config_g1_g01.json").exists()


def test_no_artifacts_dir_means_no_files_and_no_error(tmp_path) -> None:
    """Emission is opt-in: the unit harness and the local rules harness play without a
    directory, and a match that writes nothing must still be a valid match."""
    result, _ = _run(reply(1), reply(2, claim_response={"claim": [3, 3], "caught": True}))
    assert result.played
    assert not list(tmp_path.iterdir())
