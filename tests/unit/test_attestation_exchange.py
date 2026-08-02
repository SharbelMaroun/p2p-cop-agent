"""M5-17f-ii: exchange and mutually verify the Step-0 attestation before play.

Step-0 carries nothing secret, so it is exchanged *revealed* and verified on the
spot, riding on the negotiation offer (Option A). We always send ours; we verify a
peer's when present and tolerate its omission (`U-029`), refusing only a
present-but-tampered seal.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.orchestration.negotiation_handshake import negotiate_match
from p2p_cop_agent.protocol.attestation import (
    AttestationError,
    HostSpec,
    attestation_wire,
    build_step_zero,
    review_opponent_attestation,
    seal_step_zero,
)
from p2p_cop_agent.protocol.negotiation import NegotiationError, build_offer
from p2p_cop_agent.shared.contracts import shared_config_sha256
from tests.unit.test_negotiation_handshake import Counterparty, _game, _identity
from tests.unit.test_polling import FakeClock


def _sealed(game: dict):
    host = HostSpec(os="linux", cpu="x", ram_gb=8, gpu="none", vram_gb=1)
    payload = build_step_zero(
        host=host, model="template", group_id="neutral-group-beta",
        game_id="g1", git_commit="a" * 40, config_sha256=shared_config_sha256(game),
    )
    return seal_step_zero(payload)


def _wire(game: dict) -> dict:
    return attestation_wire(_sealed(game))


def _tampered(game: dict) -> dict:
    wire = _wire(game)
    return {**wire, "payload": {**wire["payload"], "model": "forged"}}


def _offer_with(game: dict, step_zero: dict) -> dict:
    return {**build_offer(game, _identity("neutral-group-beta")), "step_zero": step_zero}


def _run(peer: Counterparty, game: dict, *, step_zero: dict | None = None):
    clock = FakeClock()
    return negotiate_match(
        game=game, identity=_identity("neutral-group-alpha"),
        transport=peer, take_offer=peer.take,
        clock=clock.time, sleep=clock.sleep, timeout=5.0, poll_interval=0.5,
        step_zero=step_zero,
    )


def test_attestation_wire_serializes_the_seal() -> None:
    sealed = _sealed(_game())
    assert attestation_wire(sealed) == {
        "payload": sealed.payload, "nonce": sealed.nonce, "commit": sealed.commit,
    }


def test_an_omitted_attestation_is_tolerated() -> None:
    assert review_opponent_attestation(None) is None


def test_a_sound_attestation_is_returned_unchanged() -> None:
    wire = _wire(_game())
    assert review_opponent_attestation(wire) == wire


@pytest.mark.parametrize("bad", [
    "not-a-mapping",
    {"payload": {}, "nonce": "x"},                    # missing commit
    {"payload": "x", "nonce": "y", "commit": "z"},    # payload is not an object
])
def test_a_malformed_present_attestation_is_refused(bad: object) -> None:
    with pytest.raises(AttestationError):
        review_opponent_attestation(bad)


def test_a_tampered_attestation_is_refused() -> None:
    with pytest.raises(AttestationError, match="tampered"):
        review_opponent_attestation(_tampered(_game()))


def test_our_offer_carries_our_step_zero() -> None:
    game = _game()
    peer = Counterparty(build_offer(game, _identity("neutral-group-beta")))
    _run(peer, game, step_zero=_wire(game))
    assert "step_zero" in peer.sent[0]


def test_a_present_opponent_attestation_is_verified_into_the_agreement() -> None:
    game = _game()
    wire = _wire(game)
    agreement = _run(Counterparty(_offer_with(game, wire)), game, step_zero=_wire(game))
    assert agreement is not None
    assert agreement.opponent_step_zero == wire


def test_an_opponent_that_omits_attestation_still_agrees() -> None:
    game = _game()
    agreement = _run(Counterparty(build_offer(game, _identity("neutral-group-beta"))), game)
    assert agreement is not None
    assert agreement.opponent_step_zero is None


def test_a_tampered_opponent_attestation_refuses_the_match() -> None:
    game = _game()
    with pytest.raises(NegotiationError, match="attestation"):
        _run(Counterparty(_offer_with(game, _tampered(game))), game)
