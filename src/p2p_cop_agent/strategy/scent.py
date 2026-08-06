"""Multiplicative scent field: emission and decay (M6-01, M6-07).

Book Ch. 4: ``τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ)``. Appendix F table 16 fixes the centre
intensity at ``0.9``, decay ``ρ = 0.10``, and a 5×5 field. The decay is
**multiplicative** -- the simulator's subtractive decay is a reference deviation the
book overrides (`C-009`, `ADR-005`), and a test distinguishes the two.

**The eight undocumented cells are now negotiated, not omitted (`U-030`).** Book
Figure 4 (`inst/police_thief_p2p_Summary.md:947-955`) names five radial classes --
centre ``0.90``, cross ``0.62``, diagonal ``0.20``, mid-side ``0.14``, corner
``0.04`` -- covering **17** of the 25 cells. The 8 cells at offsets ``(±1,±2)`` /
``(±2,±1)`` are named by no source, so no value for them can be *derived*; the book's
own boxed section (PDF p. 31) says what to do instead: the parties **agree** the
emission and decay model, verify they read it identically, and lock it with a SHA-256
hash. So the class is a parameter with a published default, and the whole model is
hash-locked at negotiation (:mod:`p2p_cop_agent.strategy.scent_lock`).

Emitting them is not optional for interoperability: the reference simulator's
``SmellField.snapshot()`` emits **all 25** cells and its own tests assert a length of
25, so a 17-cell field reads as 8 missing cells to a simulator-built opponent.

``DEFAULT_OUTER_RING_DELTA`` carries **no book authority** and is deliberately not
presented as if it did. It is a starting offer, and the lock is what makes a
disagreement visible before the first move rather than at the audit.

Re-emission on an occupied cell is still unresolved (**U-031**): :func:`decay`
implements the formula as written and applies no ``0.9`` cap.
"""

from __future__ import annotations

CENTER_INTENSITY = 0.9
DECAY_RATE = 0.10
FIELD_SIZE = 5

# Row/col offset from the agent -> emitted Δτ, for the 17 book-documented cells
# (`inst/police_thief_p2p_Summary.md:947-955`). This stays the record of what the
# book *states*; the negotiated outer ring is deliberately kept out of it so the two
# can never be confused for one another.
DOCUMENTED_EMISSION: dict[tuple[int, int], float] = {
    (0, 0): 0.90,  # centre -- the agent itself
    # cross: orthogonal neighbours, distance 1
    (-1, 0): 0.62, (1, 0): 0.62, (0, -1): 0.62, (0, 1): 0.62,
    # diagonal neighbours, distance 1 on each axis
    (-1, -1): 0.20, (-1, 1): 0.20, (1, -1): 0.20, (1, 1): 0.20,
    # mid-side edges, distance 2 orthogonal
    (-2, 0): 0.14, (2, 0): 0.14, (0, -2): 0.14, (0, 2): 0.14,
    # corners, distance 2 diagonal
    (-2, -2): 0.04, (-2, 2): 0.04, (2, -2): 0.04, (2, 2): 0.04,
}

# The 8 cells at squared distance 5 that Figure 4 leaves unnamed (`U-030`).
OUTER_RING_OFFSETS: tuple[tuple[int, int], ...] = (
    (-2, -1), (-2, 1), (2, -1), (2, 1),
    (-1, -2), (1, -2), (-1, 2), (1, 2),
)

# The negotiated default for that ring. NO BOOK AUTHORITY -- see the module docstring.
# It matches the corner class only because a residual is the least surprising opening
# offer, not because any source says so. Both peers lock whatever they agree.
DEFAULT_OUTER_RING_DELTA = 0.04


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
