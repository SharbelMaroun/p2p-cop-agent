"""M5-17f: agree before the first move, unattended.

``build_offer`` signs and ``verify_offer`` checks, but nothing sequenced them over
the mailbox, so a peer could not reach agreement on its own. These pin the join: the
opponent answers only through the wire shape (its offer lands in our agreements
mailbox), and play may begin only once it verifies. Time and the offer source are
injected, so a silent opponent is proven by advancing a number, not by sleeping.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_cop_agent.orchestration.negotiation_handshake import (
    Agreement,
    HandshakeError,
    negotiate_match,
)
from p2p_cop_agent.protocol.negotiation import NegotiationError, build_offer, terms_from_config
from tests.unit.test_polling import FakeClock

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"


def _game(**world: object) -> dict:
    game = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    if world:
        game["world"] = {**game["world"], **world}
    return game


def _identity(group_id: str) -> dict:
    return {
        "group_id": group_id,
        "group_name": group_id,
        "members": ["a", "b"],
        "repos": {"cop": "https://example.com/cop"},
        "mcp_servers": {"cop": "https://example.com/mcp"},
        "llm_model": "template-zero-token",
        "spec": {"os": "linux", "cpu": "x", "ram_gb": 8, "gpu": "none", "vram_gb": 0},
    }


class Counterparty:
    """A peer that answers our negotiate by seeding its own offer into our inbox.

    ``ack`` lets a test force an unacknowledged send; ``offer`` of ``None`` models a
    peer that receives ours but never sends its own.
    """

    def __init__(self, offer: dict | None, *, ack: dict | None = None) -> None:
        self.offer = offer
        self.ack = ack if ack is not None else {"ok": True}
        self.inbox: list[dict] = []
        self.sent: list[dict] = []

    def negotiate(self, message: dict) -> dict:
        self.sent.append(message)
        if self.offer is not None:
            self.inbox.append(self.offer)
        return self.ack

    def take(self) -> dict | None:
        return self.inbox.pop(0) if self.inbox else None


def _run(peer: Counterparty, game: dict, *, timeout: float = 5.0):
    clock = FakeClock()
    return negotiate_match(
        game=game,
        identity=_identity("neutral-group-alpha"),
        transport=peer,
        take_offer=peer.take,
        clock=clock.time,
        sleep=clock.sleep,
        timeout=timeout,
        poll_interval=0.5,
    ), clock


def test_agreement_is_reached_when_the_opponents_offer_verifies() -> None:
    game = _game()
    peer = Counterparty(build_offer(game, _identity("neutral-group-beta")))

    result, _ = _run(peer, game)

    assert isinstance(result, Agreement)
    assert result.terms == terms_from_config(game)
    assert result.opponent_identity["group_id"] == "neutral-group-beta"
    assert peer.sent and peer.sent[0]["identity"]["group_id"] == "neutral-group-alpha"


def test_a_mismatched_offer_refuses_the_match_by_name() -> None:
    ours = _game()  # rule 11: a term that disagrees names itself; play must not start
    theirs = build_offer(_game(map_area="London"), _identity("neutral-group-beta"))
    peer = Counterparty(theirs)

    with pytest.raises(NegotiationError, match="setting"):
        _run(peer, ours)


def test_no_counter_offer_before_the_deadline_is_no_match() -> None:
    """A silent opponent is not a refusal, but it is equally not a game: return None."""
    game = _game()
    peer = Counterparty(None)

    result, clock = _run(peer, game, timeout=2.0)

    assert result is None
    assert clock.now >= 2.0  # it really waited its budget before giving up
    assert peer.sent, "our offer still went out even though none came back"


def test_an_unacknowledged_offer_is_a_handshake_error_not_a_refusal() -> None:
    """A carrier that declines our send is a transport concern, never a rule-11 loss."""
    game = _game()
    peer = Counterparty(build_offer(game, _identity("neutral-group-beta")), ack={"ok": False})

    with pytest.raises(HandshakeError):
        _run(peer, game)


def test_a_transport_fault_sending_our_offer_is_a_handshake_error() -> None:
    from p2p_cop_agent.adapters import TransportError

    class Unreachable(Counterparty):
        def negotiate(self, message: dict) -> dict:
            raise TransportError("unreachable")

    with pytest.raises(HandshakeError):
        _run(Unreachable(None), _game())


def test_a_transport_missing_negotiate_is_a_handshake_error() -> None:
    clock = FakeClock()
    with pytest.raises(HandshakeError, match="negotiate"):
        negotiate_match(
            game=_game(), identity=_identity("neutral-group-alpha"),
            transport=object(), take_offer=lambda: None,
            clock=clock.time, sleep=clock.sleep, timeout=1.0,
        )

def test_a_malformed_incoming_offer_refuses_the_match() -> None:
    peer = Counterparty({"terms": {}, "nonce": "x", "signature": "y"})
    with pytest.raises(NegotiationError):
        _run(peer, _game())
