"""Lock the scent model to a hash both peers must match before play (M6-07, `AE-23`).

Appendix E rule 23 is verbatim: *"Lock the cryptographic hash of the scent model
before the start of the game. Sanction: Deviation from the formula cancels the
game."* The book's boxed section (PDF p. 31,
`inst/police_thief_p2p_Summary.md:1043-1048`) gives the method: the parties agree the
emission and decay model, check they **interpret it identically** using a concrete
numerical example, and lock the agreement with a SHA-256 hash, so any later deviation
is immediately detectable. It further *recommends* -- not mandates -- exchanging the
scent mechanism's source code.

Comparing the three Appendix F constants is not enough. Two peers can hold identical
``smell_grid_size`` / ``decay_per_step`` / ``emit_intensity`` and still emit different
fields, because the **radial profile** and the **formula** never crossed the wire.
That is exactly the gap `U-030` sits in: the eight cells at squared distance 5 have no
book value, so each peer would otherwise pick one privately and discover the
disagreement at the audit, when it is worth zero to both sides.

So the whole model -- formula, constants, field size, and the complete 25-cell profile
including the negotiated ring -- canonicalises into one record and hashes with the
same canonical JSON the config lock and commitments use.

**The record shape is the interop contract.** Its member names and ordering are what
make two independently written peers produce the same digest; changing a key here is a
contract revision, not a refactor.

**Tolerate omission, refuse a mismatch** (the `U-029`/`C-031` pattern already settled
for ``config_sha256``). We always publish our lock. An opponent that sends none is
still played -- the reference simulator carries no standalone scent hash, folding the
pheromone terms into ``config_sha256`` instead, so requiring one would refuse every
simulator-built classmate. An opponent that sends a **different** lock is refused,
because that is the deviation rule 23 sanctions.
"""

from __future__ import annotations

from p2p_cop_agent.shared.contracts import shared_config_sha256
from p2p_cop_agent.strategy.scent import (
    CENTER_INTENSITY,
    DECAY_RATE,
    DEFAULT_OUTER_RING_DELTA,
    DOCUMENTED_EMISSION,
    FIELD_SIZE,
    require_outer_ring,
)

# The negotiation-message member the lock rides in, alongside ``config_sha256``.
SCENT_LOCK_FIELD = "scent_model_hash"
# The member naming the negotiated value that lock covers, so a mismatch is legible.
SCENT_OUTER_RING_FIELD = "scent_outer_ring_delta"


class ScentLockError(ValueError):
    """Raised when a peer's scent lock disagrees with ours (`AE-23`)."""


def _profile_by_squared_distance(outer_ring: float) -> dict[str, float]:
    """Return the 25-cell profile keyed by squared distance, as JSON string keys."""
    profile = {
        str(dr * dr + dc * dc): tau for (dr, dc), tau in DOCUMENTED_EMISSION.items()
    }
    profile["5"] = require_outer_ring(outer_ring)
    return profile


def scent_model_record(outer_ring: float = DEFAULT_OUTER_RING_DELTA) -> dict:
    """Return the canonical description of the scent model we will actually run.

    Keyed by squared distance rather than by offset, because the model is radially
    symmetric and a per-offset record would let two peers agree on physics yet
    disagree on a digest purely through key spelling.
    """
    return {
        "model": "multiplicative-decay",
        "update": "tau_next = max(0, (1 - decay_per_step) * tau + emission)",
        "center_intensity": CENTER_INTENSITY,
        "decay_per_step": DECAY_RATE,
        "field_size": FIELD_SIZE,
        "emission_profile_by_squared_distance": _profile_by_squared_distance(outer_ring),
    }


def scent_model_hash(outer_ring: float = DEFAULT_OUTER_RING_DELTA) -> str:
    """Return the SHA-256 lock over the canonical scent-model record."""
    return shared_config_sha256(scent_model_record(outer_ring))


def verify_peer_scent_lock(
    offered: object,
    *,
    outer_ring: float = DEFAULT_OUTER_RING_DELTA,
) -> None:
    """Accept an absent lock; refuse one that disagrees with ours (`AE-23`).

    ``None`` means the opponent published no lock, which is not a deviation -- it is
    silence, and the reference implementation is silent here. A present-but-different
    lock **is** a deviation from the agreed formula, and rule 23 cancels the game, so
    it is refused before the first move rather than discovered at the audit.
    """
    if offered is None:
        return
    expected = scent_model_hash(outer_ring)
    if offered != expected:
        raise ScentLockError(
            f"scent model lock mismatch: peer carries {offered!r}, expected {expected!r}; "
            "Appendix E rule 23 cancels a game on an emission-model deviation"
        )


def assert_scent_locked(agreed_hash: object, *, outer_ring: float) -> None:
    """Runtime check: the model we are about to run still matches what we locked.

    Recomputed from the code that will actually emit, so a later edit to the profile
    fails loudly here instead of silently emitting a field the opponent's audit would
    reject.
    """
    running = scent_model_hash(outer_ring)
    if running != agreed_hash:
        raise ScentLockError(
            f"running scent model {running} does not match the locked model {agreed_hash!r}"
        )
