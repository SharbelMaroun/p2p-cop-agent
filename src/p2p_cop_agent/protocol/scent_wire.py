"""The `smell_grid` on the wire: encode ours, parse theirs defensively (M6-08).

The reference's shape, confirmed against its code: a JSON object whose keys are
``"row,col"`` strings -- **row first**, the same axis order as a position -- mapping to
numbers. It transmits a local window of its own accumulated trail, and it *includes*
zero cells rather than omitting them, so the receiver always sees a fixed-size window.

We match that on send. On receive we are deliberately more generous than the sender:
missing cells read as silent, so a peer that omits its zeros is read correctly too. That
is the same "strict in what we send, generous in what we accept" rule the rest of the
wire follows, and it costs nothing -- an absent cell and a zero cell mean the same thing.

**Precision is pinned on send (M6-08c).** Repeated decay produces values like
``0.7290000000000001``, whose textual form differs between languages and float
implementations. The reference rounds nothing, so this is our choice, not a shared
requirement -- which is why the wire is rounded and **parsing accepts any precision at
all**. Tightening what we emit cannot break a peer; tightening what we accept could.
Nothing here is inside the model hash: `scent_model_hash` locks the *model* (formula,
constants, profile), never the emitted numbers, so rounding cannot invalidate a lock.

**Parsing is hostile-input handling (M6-08b).** The grid arrives from an opponent, so a
malformed key, a non-numeric value, or a negative intensity is rejected before it can
reach belief. A rejected grid raises rather than silently degrading to empty: scent is
the one channel that cannot be faked, so quietly treating a corrupt one as "no evidence"
would discard the strongest signal we have.

An **off-board cell is the exception**: it is dropped, and the rest of the grid is kept.
A fixed-size window centred anywhere but the interior names cells that do not exist, so
refusing the grid for them refuses the sender's position, not their honesty. That
distinction is not academic -- see `decode_scent`, where treating it as corruption lost a
real game.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping

from p2p_cop_agent.strategy.scent import CENTER_INTENSITY, DECAY_RATE

Cell = tuple[int, int]

# Decimal places emitted. Six keeps every value the book names distinct and survives
# ~35 turns of decay without collapsing; it is a send-side choice only.
WIRE_PRECISION = 6
# A negative index is *well-formed* and simply off the board: a fixed-size window
# centred near the origin names cells like ``"-1,2"``. Matching them here lets
# `decode_scent` drop them as out-of-range rather than refusing the grid as malformed.
_KEY = re.compile(r"^(-?\d+),(-?\d+)$")


class ScentWireError(ValueError):
    """Raised when an opponent's `smell_grid` cannot be trusted to be a scent field."""


def saturation_limit(
    centre: float = CENTER_INTENSITY, decay: float = DECAY_RATE
) -> float:
    """Return the highest intensity the agreed model can ever produce: ``Δτ / ρ``.

    The book's update is **additive** -- ``τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ)`` -- so an
    agent that stands still keeps depositing onto a decayed prior and the cell climbs
    toward the fixed point of ``τ = (1-ρ)τ + Δτ``, which is ``Δτ/ρ`` (9.0 at the
    Appendix F constants). It never exceeds it.

    That bound is *derived*, which matters: an earlier version of this parser rejected
    anything above the **centre intensity** of 0.9, and our own two-turn trail already
    reaches 1.458 -- we would have refused our own emissions. Whether re-emission should
    instead be clamped at 0.9 is the open `U-031`; until it is answered the parser must
    not assume the clamp, because assuming it would refuse a peer that follows the
    formula as written.
    """
    if decay <= 0.0:
        raise ScentWireError("decay rate must be positive to bound a scent field")
    return centre / decay


def encode_scent(window: Mapping[Cell, float]) -> dict[str, float]:
    """Return the wire form of a scent window: ``{"row,col": intensity}``.

    Zero cells are kept, matching the reference, so the receiver sees the whole window.
    """
    return {
        f"{row},{col}": round(float(value), WIRE_PRECISION)
        for (row, col), value in sorted(window.items())
    }


def decode_scent(
    raw: object,
    *,
    min_index: int,
    max_index: int,
    max_intensity: float | None = None,
) -> dict[Cell, float]:
    """Return an opponent's scent grid as ``{(row, col): intensity}``, or raise.

    Every failure names what was wrong, so a refusal is actionable by the peer that
    caused it rather than an opaque "bad grid".

    **A cell outside the board is dropped, not fatal.** The reference transmits a
    *fixed-size* window and keeps its zero cells, so a peer standing anywhere but the
    board's interior necessarily names cells that do not exist -- at the 7×7 floor only
    the central 3×3, 9 of 49 cells, has a fully on-board 5×5 window. Refusing the whole
    grid for those cells cost us a played game: the opponent's every reading was
    discarded from the moment it left the centre, belief never updated again, and the
    Cop stood still on a uniform prior until the horizon. An out-of-range cell carries
    no information about *our* board, which is exactly what an omitted cell means, so
    the two are now treated alike -- the "generous in what we accept" half of this
    module's own rule, which had been implemented for absent cells but not extra ones.

    Everything that indicates a peer we cannot trust still raises: a non-string key, a
    key that is not an integer pair, a non-numeric, non-finite, negative, or
    above-saturation intensity. Dropping is for cells that are merely elsewhere.
    """
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise ScentWireError(f"smell_grid must be an object, got {type(raw).__name__}")
    ceiling = saturation_limit() if max_intensity is None else max_intensity
    grid: dict[Cell, float] = {}
    for key, value in raw.items():
        cell = _parse_key(key)
        if not (min_index <= cell[0] <= max_index and min_index <= cell[1] <= max_index):
            continue  # elsewhere, not wrong -- see the docstring
        grid[cell] = _parse_intensity(key, value, ceiling)
    return grid


def _parse_key(key: object) -> Cell:
    if not isinstance(key, str):
        raise ScentWireError(f"smell_grid keys must be strings, got {type(key).__name__}")
    match = _KEY.match(key)
    if match is None:
        raise ScentWireError(f"smell_grid key {key!r} is not \"row,col\"")
    return int(match.group(1)), int(match.group(2))


def _parse_intensity(key: object, value: object, max_intensity: float) -> float:
    """Return a validated intensity, refusing anything a scent field cannot hold."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ScentWireError(f"smell_grid[{key!r}] must be a number, got {value!r}")
    number = float(value)
    if math.isnan(number) or math.isinf(number):
        raise ScentWireError(f"smell_grid[{key!r}] must be finite, got {value!r}")
    if number < 0.0:
        raise ScentWireError(
            f"smell_grid[{key!r}] is negative ({value!r}); an empty cell is an absence "
            "of information, never a negative one"
        )
    if number > max_intensity:
        raise ScentWireError(
            f"smell_grid[{key!r}] is {value!r}, above the agreed model's saturation "
            f"limit of {max_intensity}; no cell can hold that much scent however long "
            "an agent stands on it"
        )
    return number
