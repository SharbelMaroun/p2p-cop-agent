"""Autonomous pre-play negotiation: agree before the first move (M5-17f).

The reference's runtime **waits for the opponent's counter-signature before step 1**
-- "play starts only after both verifications pass". ``build_offer``/``verify_offer``
are the primitives (M5-04); this module *sequences* them over the live mailbox so a
peer negotiates unattended: send our signed offer, wait (bounded) for the opponent's,
verify it against our own terms, and only then hand back an :class:`Agreement` the
caller may start play on. Nothing here starts a turn -- keeping "have we agreed?"
separate from "whose move is it?" is the point, so a match cannot begin half-agreed.

**Symmetric, so start order does not matter.** Both peers send and both poll, so by
the time either looks its opponent's offer is already sitting in its agreements
mailbox -- exactly as the Thief's opening turn is for the play loop. The same
bounded-wait primitive the turn loop uses (``poll_for_turn``) does the waiting, so a
silent opponent here is bounded by the same rule-6 discipline as everywhere else.

**Three outcomes, deliberately distinct:**

* an :class:`Agreement`, when the opponent's offer arrived and verified;
* a ``NegotiationError`` (refusal), when an offer arrived but disagrees -- rule 11
  refuses to play on any mismatch, and the caller must not start;
* ``None``, when no counter-offer arrived before the deadline -- a silent opponent is
  not a refusal but is equally not a game, so the caller aborts rather than plays.

Time and the offer source are injected, so the whole handshake runs in-memory with no
socket, the same object that runs over one.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from p2p_cop_agent.adapters.fastmcp_client import PeerRejectionError, TransportError
from p2p_cop_agent.orchestration.polling import (
    DEFAULT_POLL_INTERVAL,
    Clock,
    Heartbeat,
    Sleep,
    poll_for_turn,
)
from p2p_cop_agent.protocol.attestation import AttestationError, review_opponent_attestation
from p2p_cop_agent.protocol.messages import ProtocolError, is_acknowledgement, validate_message
from p2p_cop_agent.protocol.negotiation import NegotiationError, build_offer, terms_from_config
from p2p_cop_agent.protocol.offer_review import verify_offer
from p2p_cop_agent.shared.config import JsonObject
from p2p_cop_agent.shared.contracts import shared_config_sha256

# Pull the opponent's next queued offer, or None if none has arrived yet. Never
# blocks: the waiting is poll_for_turn's job, the same as the turn source.
TakeOffer = Callable[[], "JsonObject | None"]


class HandshakeError(RuntimeError):
    """Raised when our own offer could not be delivered to the opponent.

    Distinct from ``NegotiationError`` (the opponent's offer disagreed) because a
    carrier fault sending *our* offer is not the opponent refusing *us*; conflating
    them would let a lost connection read as a rule-11 mismatch.
    """


@dataclass(frozen=True, slots=True)
class Agreement:
    """A verified mutual agreement: the terms both peers signed, and who we agreed with.

    ``opponent_step_zero`` is the peer's verified Step-0 attestation when it sent one,
    or ``None`` when it omitted it (tolerated, `U-029`) -- kept so the caller can carry
    it into the emitted artifacts without re-reading the offer.
    """

    terms: JsonObject
    opponent_identity: JsonObject
    our_offer: JsonObject
    opponent_step_zero: JsonObject | None = None


def negotiate_match(
    *,
    game: Mapping[str, object],
    identity: Mapping[str, object],
    transport: object,
    take_offer: TakeOffer,
    clock: Clock,
    sleep: Sleep,
    timeout: float,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    heartbeat: Heartbeat | None = None,
    our_nonce: str | None = None,
    step_zero: Mapping[str, object] | None = None,
) -> Agreement | None:
    """Send our offer, await the opponent's, and return an Agreement iff both verify.

    ``build_offer`` validates *our* side up front (Appendix F, participants, complete
    identity), so an offer that leaves here is already well-formed; the opponent's is
    checked with ``verify_offer`` once it arrives. A return of ``None`` means no
    counter-offer came in time, and the caller must not start play.

    ``step_zero`` is our sealed Step-0 attestation (``protocol.attestation_wire``);
    when given it rides on the offer and the opponent's is verified on receipt --
    tolerating omission, refusing a present-but-tampered seal (M5-17f-ii, `U-029`).
    """
    our_offer = build_offer(game, identity, nonce=our_nonce)
    if step_zero is not None:
        our_offer = {**our_offer, "step_zero": dict(step_zero)}
    _send_offer(transport, our_offer)
    their_offer = poll_for_turn(
        take_offer,
        clock=clock,
        sleep=sleep,
        timeout=timeout,
        poll_interval=poll_interval,
        heartbeat=heartbeat,
    )
    if their_offer is None:
        return None
    agreed = _verify_incoming(their_offer, game)
    return Agreement(
        agreed,
        _opponent_identity(their_offer),
        our_offer,
        _review_attestation(their_offer.get("step_zero")),
    )


def _opponent_identity(their_offer: Mapping[str, object]) -> JsonObject:
    """Their identity block, backfilled from a top-level ``group_id`` (`C-047`).

    Third site of the same defect, and the one that survived the first two fixes. The
    schema stopped requiring ``identity`` and ``InboundPeer.negotiate`` learned to read the
    group id from either home -- but this is a *different path*: `InboundPeer` serves the
    inbound mailbox, while this runs on the outbound handshake and is what actually feeds
    ``build_declaration``. A peer sending ``group_id`` top-level therefore got all the way
    to `DeclarationError: each group needs a non-empty group_id`, one stage later and with
    the negotiation already agreed.

    The declaration genuinely needs a non-empty id per group, so the fix is to find the one
    they sent rather than to relax that -- an anonymous group in a signed artifact would be
    a real gap, unlike a missing wire member we had already agreed to tolerate.
    """
    block = their_offer.get("identity")
    identity: JsonObject = dict(block) if isinstance(block, Mapping) else {}
    if not identity.get("group_id"):
        top_level = their_offer.get("group_id")
        if isinstance(top_level, str) and top_level.strip():
            identity["group_id"] = top_level
    return identity


def _send_offer(transport: object, offer: JsonObject) -> None:
    """Deliver our offer and require the opponent acknowledged receiving it."""
    send = getattr(transport, "negotiate", None)
    if send is None:
        raise HandshakeError("transport does not expose negotiate")
    try:
        ack = send(offer)
    except (TransportError, PeerRejectionError) as exc:
        raise HandshakeError(f"our offer could not be delivered: {exc}") from exc
    if not is_acknowledgement(ack):
        raise HandshakeError(f"opponent did not acknowledge our offer: {ack!r}")


def _review_attestation(step_zero: object) -> JsonObject | None:
    """Verify the opponent's Step-0 if present; a tampered one refuses the match."""
    try:
        return review_opponent_attestation(step_zero)
    except AttestationError as exc:
        raise NegotiationError(f"opponent attestation refused: {exc}") from exc


def _verify_incoming(offer: JsonObject, game: Mapping[str, object]) -> JsonObject:
    """Schema-check then deep-verify the opponent's offer against our own terms."""
    try:
        validate_message("negotiate", offer)
    except ProtocolError as exc:
        raise NegotiationError(f"opponent offer is not a valid negotiate message: {exc}") from exc
    return verify_offer(
        offer,
        terms_from_config(game),
        expected_config_sha256=shared_config_sha256(dict(game)),
    )
