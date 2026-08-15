"""Model-matched emitter decoding: invert the locked scent physics (M6-24).

`scent_likelihood` weights cells by raw observed intensity, which discards everything
the agreed model says about how a trail decays and stacks — a twice-visited old cell
outshines a fresh stamp and the argmax lags the emitter. The companion repository
measured what that lag costs and what fixing it buys: its truth-fed exact planner is
perfect, its raw-argmax one collapses, and a model-matched decoder took its pursuer
grid from 23/8/5 escapes to 24/24/24. This is the same inversion built for this side
of the board, independently, from this repository's own scent module.

The physics is a shared, hash-locked contract and it is exactly invertible: the field
obeys ``τ' = max(0, (1-ρ)·τ + Δτ)`` with both terms non-negative, so the clip never
bites and consecutive observations satisfy, cell for cell:

    now(x) − (1−ρ)·before(x)  =  Δτ(x − emitter)

The left side is two public observations; the right side is the agreed 5×5 stamp.
Score every candidate cell by how badly the residual mismatches the stamp centred
there: the true emitter scores zero, and the best wrong candidate carries at least
the centre-versus-cross gap ``(0.9 − 0.62)²``, so a sharply decaying score separates
truth from neighbour by orders of magnitude.

Degraded modes are explicit: no previous observation (first turn, or a gap) matches
the single stamp against the whole field — exact on turn one, approximate after a
gap; a partial window restricts scoring to cells both observations covered; and a
field the model cannot explain anywhere yields the flat no-information likelihood
rather than a confident wrong answer (M6-02c) — which is also evidence of a rule-23
emission-model deviation. Inputs are the opponent's published observations and the
agreed constants, never a true position `[AE-8]`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from p2p_cop_agent.strategy.scent import (
    CENTER_INTENSITY,
    DECAY_RATE,
    DEFAULT_OUTER_RING_DELTA,
    emission_offsets,
)

Cell = tuple[int, int]

_RADIUS = 2  # the 5×5 stamp reaches two cells from its centre

# e^(−error/SHARPNESS): 0.01 gives the true cell over a thousand times the mass of
# its best rival (minimum wrong-centre error ≈ 0.078) while never hard-zeroing.
SHARPNESS = 0.01


def residual(
    now: Mapping[Cell, float],
    before: Mapping[Cell, float] | None,
    *,
    decay_rate: float = DECAY_RATE,
) -> dict[Cell, float]:
    """Return ``now − (1−ρ)·before`` per cell: the newest stamp, by the contract."""
    keep = 1.0 - decay_rate
    cells = set(now) | set(before or ())
    return {cell: now.get(cell, 0.0) - keep * (before or {}).get(cell, 0.0)
            for cell in cells}


def informative(
    now: Mapping[Cell, float],
    before: Mapping[Cell, float] | None,
    *,
    cap: float = CENTER_INTENSITY,
    tolerance: float = 1e-9,
) -> set[Cell]:
    """Cells whose residual still inverts the physics under the `C-048` clamp.

    This decoder's premise was that the update never clips, so ``now − (1−ρ)·before``
    recovers the stamp exactly. The upper clamp breaks that for **saturated** cells: the
    discarded amount is unrecoverable, and the resulting gap punishes the true emitter
    hardest, because its own cell is the one most likely to sit at the ceiling.

    ``before == 0`` is kept: nothing could have been clipped, so a fresh centre stamp
    reading the cap is legitimate and is the most informative cell in the window. With
    ``before > 0`` the unclipped sum exceeded the stamp, so a reading of exactly the cap
    is clipping or is indistinguishable from it, and the cell must not vote -- the same
    "unobserved is not zero" rule the partial-window case already uses.
    """
    previous = before or {}
    return {
        cell for cell in (set(now) | set(previous))
        if not (now.get(cell, 0.0) >= cap - tolerance
                and previous.get(cell, 0.0) > tolerance)
    }


def match_error(
    observed_residual: Mapping[Cell, float],
    centre: Cell,
    *,
    grid_size: int,
    start: int = 0,
    trusted: Iterable[Cell] | None = None,
    profile: Mapping[Cell, float] | None = None,
) -> float:
    """Return the squared mismatch between the residual and the stamp at ``centre``."""
    stamp = profile if profile is not None else emission_offsets(DEFAULT_OUTER_RING_DELTA)
    centre_row, centre_col = centre
    last = start + grid_size - 1
    cells = {
        (centre_row + dr, centre_col + dc)
        for dr in range(-_RADIUS, _RADIUS + 1) for dc in range(-_RADIUS, _RADIUS + 1)
        if start <= centre_row + dr <= last and start <= centre_col + dc <= last
    }
    cells |= set(observed_residual)
    if trusted is not None:
        cells &= set(trusted)
    error = 0.0
    for cell in sorted(cells):
        expected = stamp.get((cell[0] - centre_row, cell[1] - centre_col), 0.0)
        gap = observed_residual.get(cell, 0.0) - expected
        error += gap * gap
    return error


def emitter_likelihood(
    now: Mapping[Cell, float],
    before: Mapping[Cell, float] | None = None,
    *,
    grid_size: int,
    start: int = 0,
    trusted: Iterable[Cell] | None = None,
    sharpness: float = SHARPNESS,
) -> dict[Cell, float]:
    """Return the model-matched likelihood over emitter cells for `Belief.updated`.

    Drop-in where `scent_likelihood` goes; a cell's weight means "how well the whole
    observed change is explained by the emitter standing here", not "how much scent
    sits here". Empty or inexplicable observations return the flat no-information
    likelihood so the prior survives unchanged (M6-02c).
    """
    from math import exp  # noqa: PLC0415

    cells = [(row, col) for row in range(start, start + grid_size)
             for col in range(start, start + grid_size)]
    if not now:
        return dict.fromkeys(cells, 1.0)
    delta = residual(now, before)
    # `C-048`: a saturated cell cannot be inverted, so it is excluded rather than scored as
    # a mismatch. Intersected with any window restriction the caller supplied — both say
    # the same thing, that the cell's residual is not computable.
    usable = informative(now, before)
    trusted_cells = usable if trusted is None else usable & set(trusted)
    stamp = emission_offsets(DEFAULT_OUTER_RING_DELTA)
    likelihood = {
        cell: exp(-match_error(delta, cell, grid_size=grid_size, start=start,
                               trusted=trusted_cells, profile=stamp) / sharpness)
        for cell in cells
    }
    if not any(value > 0.0 for value in likelihood.values()):
        return dict.fromkeys(cells, 1.0)
    return likelihood
