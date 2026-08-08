"""Multiplicative scent field: emission and decay (M6-01, M6-07).

Book Ch. 4: ``τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ)``. Appendix F table 16 fixes the centre
intensity at ``0.9``, decay ``ρ = 0.10``, and a 5×5 field. The decay is
**multiplicative** -- the simulator's subtractive decay is a reference deviation the
book overrides (`C-009`, `ADR-005`), and a test distinguishes the two.

**Figure 4 names all six radial classes, and this table was wrong until 2026-08-08
(`U-030`, reopened and re-closed).** The corrected profile, by squared distance from
the emitter: centre ``0.90``, cross ``0.62``, diagonal ``0.42``, mid-side ``0.20``,
the eight cells at squared distance 5 ``0.14``, corner ``0.04`` -- **25 of 25 cells**,
none unnamed.

**How the old table went wrong, because the shape of the error is the lesson.** The
translation in ``inst/police_thief_p2p_Summary.md:947-955`` lists only five classes and
assigns diagonal ``0.20`` and mid-side ``0.14`` -- which are the true values of the
*next two rings out*. The whole table was the right curve **shifted inward by one
radial class**, which is why the endpoints (``0.90``, ``0.62``, ``0.04``) matched
perfectly while the middle did not, and why eight cells appeared to have no value: the
shift had consumed the class that owns ``0.14``.

**What settles it.** Fit ``τ = 0.9·exp(−k·d²)`` using only the two values every reading
agrees on -- centre ``0.90`` and cross ``0.62`` -- and the rest follow with no free
parameter: ``0.427``, ``0.203``, ``0.140``, ``0.046``. That is the corrected table to
two decimals, four for four, and it is what Figure 4's own caption describes: a hill
that "decays radially from the center". The book PDF confirms it directly, and a
classmate team reproduced the same kernel independently.

The old reading was defended on 2026-08-05 against exactly these values on the grounds
that "a notebook answer is not a source" -- but the notebook holds the **PDF**, and the
file it was checked against is a *translation*. A restatement is not the source either,
and that is the rule that was applied backwards.

Emitting all 25 is also required for interoperability: the reference simulator's
``SmellField.snapshot()`` emits 25 cells and its tests assert that length, so a
17-cell field reads as 8 missing cells to a simulator-built opponent.

``DEFAULT_OUTER_RING_DELTA`` now carries book authority; the parameter survives only so
a peer that insists on a different ring can still be met and locked
(:mod:`p2p_cop_agent.strategy.scent_lock`).

Re-emission on an occupied cell is still unresolved (**U-031**): :func:`decay`
implements the formula as written and applies no ``0.9`` cap.
"""

from __future__ import annotations

CENTER_INTENSITY = 0.9
DECAY_RATE = 0.10
FIELD_SIZE = 5

# Row/col offset from the agent -> emitted Δτ, for the 17 cells outside the squared
# distance 5 ring. Corrected 2026-08-08 against the book PDF: the diagonal is 0.42 and
# the mid-side 0.20; the previous 0.20/0.14 were this curve shifted inward one class.
DOCUMENTED_EMISSION: dict[tuple[int, int], float] = {
    (0, 0): 0.90,  # centre -- the agent itself
    # cross: orthogonal neighbours, squared distance 1
    (-1, 0): 0.62, (1, 0): 0.62, (0, -1): 0.62, (0, 1): 0.62,
    # diagonal neighbours, squared distance 2
    (-1, -1): 0.42, (-1, 1): 0.42, (1, -1): 0.42, (1, 1): 0.42,
    # mid-side edges, squared distance 4
    (-2, 0): 0.20, (2, 0): 0.20, (0, -2): 0.20, (0, 2): 0.20,
    # corners, squared distance 8
    (-2, -2): 0.04, (-2, 2): 0.04, (2, -2): 0.04, (2, 2): 0.04,
}

# The 8 cells at squared distance 5. Figure 4 names them 0.14 (`U-030`, re-closed).
OUTER_RING_OFFSETS: tuple[tuple[int, int], ...] = (
    (-2, -1), (-2, 1), (2, -1), (2, 1),
    (-1, -2), (1, -2), (-1, 2), (1, 2),
)

# Figure 4's value for that ring. This was `0.04` and carried "NO BOOK AUTHORITY" until
# 2026-08-08, when the PDF showed the book names it -- the ring only looked unnamed
# because the rest of the table was shifted into it.
DEFAULT_OUTER_RING_DELTA = 0.14


class ScentModelError(ValueError):
    """Raised when a negotiated scent parameter is outside the model's range."""


def require_outer_ring(value: object) -> float:
    """Return a validated outer-ring Δτ, refusing a value outside ``[0, 0.9]``.

    The ring is negotiated, so an opponent supplies it; a value above the centre
    intensity would make the field non-decreasing with distance, which is not a
    radial emission at all, and a negative one contradicts "absence of information".
    """
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ScentModelError(f"outer-ring emission must be a number, got {value!r}")
    if not 0.0 <= float(value) <= CENTER_INTENSITY:
        raise ScentModelError(
            f"outer-ring emission must lie in [0, {CENTER_INTENSITY}], got {value!r}"
        )
    return float(value)


def emission_offsets(
    outer_ring: float = DEFAULT_OUTER_RING_DELTA,
) -> dict[tuple[int, int], float]:
    """Return the complete 25-cell offset -> Δτ profile for an agreed outer ring.

    The 17 documented cells come from the book; the 8 at squared distance 5 take the
    agreed value. Every cell of the 5×5 window is present, because a peer that omits
    cells is indistinguishable from one that emits zero there.
    """
    ring = require_outer_ring(outer_ring)
    return {**DOCUMENTED_EMISSION, **dict.fromkeys(OUTER_RING_OFFSETS, ring)}


def decay(tau: float, delta_tau: float = 0.0, rho: float = DECAY_RATE) -> float:
    """One update: ``τ(t+1) = max(0, (1-ρ)·τ + Δτ)`` (M6-01b, M6-01d).

    Multiplicative, never subtractive (`C-009`): at ``ρ=0.10`` the retained fraction
    is ``0.90·τ``, not ``τ − 0.10``. A never-visited, never-emitting cell stays ``0``
    -- absence of information, clipped non-negative. The book mandates this runs once
    per full turn, after both sides act, never per half-turn. No re-emission cap is
    applied (U-031).
    """
    return max(0.0, (1.0 - rho) * tau + delta_tau)


def emission_field(
    center: tuple[int, int],
    *,
    outer_ring: float = DEFAULT_OUTER_RING_DELTA,
) -> dict[tuple[int, int], float]:
    """Return the full 5×5 Δτ emission around ``center`` as ``{cell: Δτ}`` (M6-01a).

    All 25 cells are placed. Cells are absolute board coordinates; the caller clips
    them to the negotiated board. ``outer_ring`` is the agreed value for the 8 cells
    the book does not name, and defaults to our published opening offer.
    """
    row, col = center
    profile = emission_offsets(outer_ring)
    return {(row + dr, col + dc): tau for (dr, dc), tau in profile.items()}
