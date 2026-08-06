"""Reviewing an incoming negotiation offer (M5-04, M5-04h).

Split from ``negotiation`` -- which *builds* an offer -- so each file keeps to one
responsibility and within its length. Verifying an opponent's offer is a distinct
job: structure, the signature over the terms, Appendix F, equality with our own
terms, and the ``config_sha256`` lock.

The dependency runs one way (this module imports the build side, never the reverse),
so there is no import cycle.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_cop_agent.protocol.commit import verify_commit
from p2p_cop_agent.protocol.negotiation import (
    SCENT_LOCK_FIELD,
    NegotiationError,
    check_appendix_f,
)
from p2p_cop_agent.shared.config import JsonObject


def verify_offer(
    offer: Mapping[str, object],
    expected_terms: Mapping[str, object],
    *,
    expected_config_sha256: str | None = None,
    expected_scent_lock: str | None = None,
) -> JsonObject:
    """Accept an opponent's offer, or raise naming exactly what disagrees.

    Order matters: structure, then signature, then Appendix F, then equality with
    our own terms. A peer learns *why* it was refused, which rule 11 requires.

    The ``config_sha256`` lock is handled the "populate ours, tolerate theirs" way
    (`U-029`): an offer that **omits** it still verifies, because a simulator-built
    peer keeps the lock in its artifacts rather than on the wire, and refusing it
    would lose an otherwise-valid match. But an offer that **carries** one which does
    not match ours is a config mismatch, and rule 11 requires refusing it.

    ``expected_scent_lock`` applies the identical rule to the Appendix E rule 23
    scent-model hash (M6-07). Silence is tolerated -- the reference publishes no such
    hash, folding its pheromone terms into ``config_sha256`` -- while a **differing**
    lock is the emission-model deviation rule 23 cancels the game for, so it is
    refused here rather than discovered at an audit worth zero to both sides.
    """
    for field in ("terms", "nonce", "signature"):
        if field not in offer:
            raise NegotiationError(f"offer is missing {field!r}")
    terms = offer["terms"]
    if not isinstance(terms, Mapping):
        raise NegotiationError("offer terms must be an object")
    if not verify_commit(dict(terms), offer["nonce"], offer["signature"]):  # type: ignore[arg-type]
        raise NegotiationError("offer signature does not cover the offered terms")
    check_appendix_f(terms)
    differing = sorted(
        key
        for key in set(terms) | set(expected_terms)
        if terms.get(key) != expected_terms.get(key)
    )
    if differing:
        raise NegotiationError(f"negotiated terms differ on: {', '.join(differing)}")
    _verify_config_lock(offer.get("config_sha256"), expected_config_sha256)
    _verify_scent_lock(offer.get(SCENT_LOCK_FIELD), expected_scent_lock)
    return dict(terms)


def _verify_config_lock(offered: object, expected: str | None) -> None:
    """Tolerate an omitted lock, but refuse a present-but-wrong one (`U-029`)."""
    if expected is None or offered is None:
        return  # we cannot check, or the peer did not lock -- tolerated
    if offered != expected:
        raise NegotiationError(
            f"config_sha256 lock mismatch: offer carries {offered!r}, expected {expected!r}"
        )


def _verify_scent_lock(offered: object, expected: str | None) -> None:
    """Tolerate an omitted scent lock, but refuse a differing one (`AE-23`, M6-07).

    A differing lock means the two peers would emit different scent fields from the
    same position. That is precisely the deviation rule 23 sanctions, and it is
    invisible in the three Appendix F constants because the radial profile and the
    formula never cross the wire on their own.
    """
    if expected is None or offered is None:
        return  # we cannot check, or the peer published no scent lock -- tolerated
    if offered != expected:
        raise NegotiationError(
            f"scent_model_hash mismatch: offer carries {offered!r}, expected {expected!r}; "
            "Appendix E rule 23 cancels a game on an emission-model deviation"
        )
