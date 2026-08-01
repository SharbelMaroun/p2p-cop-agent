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
from p2p_cop_agent.protocol.negotiation import NegotiationError, check_appendix_f
from p2p_cop_agent.shared.config import JsonObject


def verify_offer(
    offer: Mapping[str, object],
    expected_terms: Mapping[str, object],
    *,
    expected_config_sha256: str | None = None,
) -> JsonObject:
    """Accept an opponent's offer, or raise naming exactly what disagrees.

    Order matters: structure, then signature, then Appendix F, then equality with
    our own terms. A peer learns *why* it was refused, which rule 11 requires.

    The ``config_sha256`` lock is handled the "populate ours, tolerate theirs" way
    (`U-029`): an offer that **omits** it still verifies, because a simulator-built
    peer keeps the lock in its artifacts rather than on the wire, and refusing it
    would lose an otherwise-valid match. But an offer that **carries** one which does
    not match ours is a config mismatch, and rule 11 requires refusing it.
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
    return dict(terms)


def _verify_config_lock(offered: object, expected: str | None) -> None:
    """Tolerate an omitted lock, but refuse a present-but-wrong one (`U-029`)."""
    if expected is None or offered is None:
        return  # we cannot check, or the peer did not lock -- tolerated
    if offered != expected:
        raise NegotiationError(
            f"config_sha256 lock mismatch: offer carries {offered!r}, expected {expected!r}"
        )
