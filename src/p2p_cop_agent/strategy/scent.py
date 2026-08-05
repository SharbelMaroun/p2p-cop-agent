"""Multiplicative scent field: emission and decay (M6-01).

Book Ch. 4: ``τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ)``. Appendix F table 16 fixes the centre
intensity at ``0.9``, decay ``ρ = 0.10``, and a 5×5 field. The decay is
**multiplicative** -- the simulator's subtractive decay is a reference deviation the
book overrides (`C-009`, `ADR-005`), and a test distinguishes the two.

Two parts of the emission model are **not** fully source-fixed and are deliberately not
invented here, because the emitted field crosses the wire and the model is
cryptographically locked and agreed between peers (M6-07): a value we guessed would
refuse an opponent who chose differently.

* The 8 intermediate outer-ring cells ``(±2,±1)`` / ``(±1,±2)`` are undocumented
  (**U-030**): the book heatmap gives only the 17 cells below.
* Whether re-emission on an occupied cell caps at ``0.9`` or accumulates is unresolved
  (**U-031**): :func:`decay` implements the formula as written; no cap is applied.
"""

from __future__ import annotations

CENTER_INTENSITY = 0.9
DECAY_RATE = 0.10
FIELD_SIZE = 5

# Row/col offset from the agent -> emitted Δτ, for the 17 book-documented cells
# (Material/reference/police_thief_p2p_unverified_translation.md:962-970). The 8
# remaining outer-ring cells (±2,±1),(±1,±2) are U-030 and intentionally absent
# rather than guessed, because the locked, cross-peer model cannot carry a value we
# invented.
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


def decay(tau: float, delta_tau: float = 0.0, rho: float = DECAY_RATE) -> float:
    """One update: ``τ(t+1) = max(0, (1-ρ)·τ + Δτ)`` (M6-01b, M6-01d).

    Multiplicative, never subtractive (`C-009`): at ``ρ=0.10`` the retained fraction
    is ``0.90·τ``, not ``τ − 0.10``. A never-visited, never-emitting cell stays ``0``
    -- absence of information, clipped non-negative. The book mandates this runs once
    per full turn, after both sides act, never per half-turn. No re-emission cap is
    applied (U-031).
    """
    return max(0.0, (1.0 - rho) * tau + delta_tau)


def emission_field(center: tuple[int, int]) -> dict[tuple[int, int], float]:
    """Return the documented Δτ emission around ``center`` as ``{cell: Δτ}`` (M6-01a).

    Only the 17 source-documented cells are placed; the 8 intermediate outer-ring
    cells are U-030 and omitted rather than guessed. Cells are absolute board
    coordinates; the caller clips them to the negotiated board.
    """
    row, col = center
    return {(row + dr, col + dc): tau for (dr, dc), tau in DOCUMENTED_EMISSION.items()}
