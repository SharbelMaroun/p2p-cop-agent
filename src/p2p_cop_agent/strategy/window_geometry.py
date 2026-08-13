"""Locate the emitter from the *shape* of its scent window, not its values (M11-01).

Every published `smell_grid` is a fixed-size square window **centred on the emitter**,
clipped to the board, with its zero cells kept (`strategy/scent_field.py:94`, and the
reference does the same -- `protocol/scent_wire.py:5-11` records it). So the set of keys
alone pins the emitter exactly, and it does so without knowing one thing about the
peer's physics: not its decay rate, not its deposit ordering, not its emission profile,
not its rounding, not whether it clamps re-emission. Those are precisely the details
`emitter_decoder` has to assume, and precisely the ones a classmate's implementation is
free to differ on.

**Why this module exists.** In the counted `amireman` series (`G008`) and the
`uoh-ay26` friendlies before it, our Cop played a near-identical move sequence in every
sub-game -- the same opening, the same barrier cells -- against opponents behaving
differently. A belief-steered Cop cannot do that. The belief never localised, so
`patrol.needs_sweep` was true on every turn and the Cop toured fixed waypoints while
`denial` spent ten barriers on fixed geometry. The intensities we received were either
unreadable under our decoder or carried no evidence at all; a window of honest zeros is
*zero evidence* to a likelihood and a *complete position fix* to this module.

Recovering the centre is elementary. A window of half-width ``h`` centred on row ``r``
spans rows ``[r-h, r+h]`` clipped to ``[min_index, max_index]``. If the low side is not
clipped the centre is ``min_row + h``; if the high side is not clipped it is
``max_row - h``. Both sides can only clip at once when the window is wider than the
board, which the 5x5-on-7x7 floor cannot produce -- and that case returns ``None``
rather than a guess.

The guess is what this module refuses to make. Every result is *verified*: the
reconstructed clipped window must equal the observed key set exactly. A peer that omits
its zero cells, sends a ragged grid, or transmits something that is not a window at all
fails that check and gets ``None``, and the caller falls back to the likelihood decoder.
A wrong fix would be worse than none, because this one is trusted absolutely.
"""

from __future__ import annotations

from collections.abc import Iterable

from p2p_cop_agent.strategy.scent import FIELD_SIZE

Cell = tuple[int, int]

# The half-width assumed when the observed window is clipped on one side of both axes,
# so no axis reveals the sender's window size. Our own emission is 5x5 and the reference
# transmits the same, so 2 is the agreed shape rather than a guess about a stranger.
DEFAULT_HALF = FIELD_SIZE // 2


def _contiguous(values: Iterable[int]) -> bool:
    """Return whether the sorted values form an unbroken run of integers."""
    ordered = sorted(values)
    return all(b - a == 1 for a, b in zip(ordered, ordered[1:], strict=False))


def _axis_centre(low: int, high: int, half: int, min_index: int, max_index: int) -> int | None:
    """Return the centre of a clipped span, or ``None`` when both sides are clipped."""
    if low > min_index:
        return low + half
    if high < max_index:
        return high - half
    return None


def _inferred_half(low: int, high: int, min_index: int, max_index: int) -> int | None:
    """Return the half-width an axis reveals, or ``None`` when the axis is clipped."""
    if low > min_index and high < max_index:
        return (high - low) // 2
    return None


def window_centre(
    cells: Iterable[Cell],
    *,
    min_index: int,
    max_index: int,
    half: int | None = None,
) -> Cell | None:
    """Return the cell an observed scent window is centred on, or ``None``.

    ``None`` means "this key set is not a board-clipped square window centred
    somewhere", which is the only honest answer for a grid whose shape does not
    determine a centre. It is never a degraded or approximate fix.
    """
    observed = set(cells)
    if not observed:
        return None
    rows = {row for row, _ in observed}
    cols = {col for _, col in observed}
    if not (_contiguous(rows) and _contiguous(cols)):
        return None
    low_row, high_row = min(rows), max(rows)
    low_col, high_col = min(cols), max(cols)
    if len(observed) != len(rows) * len(cols):
        return None  # ragged: a full window is the complete rectangle of its own span

    if half is None:
        half = _inferred_half(low_row, high_row, min_index, max_index)
        if half is None:
            half = _inferred_half(low_col, high_col, min_index, max_index)
        if half is None:
            half = DEFAULT_HALF
    if half < 0:
        return None

    row = _axis_centre(low_row, high_row, half, min_index, max_index)
    col = _axis_centre(low_col, high_col, half, min_index, max_index)
    if row is None or col is None:
        return None
    if not (min_index <= row <= max_index and min_index <= col <= max_index):
        return None
    if expected_window(row, col, half=half, min_index=min_index, max_index=max_index) != observed:
        return None
    return row, col


def expected_window(
    row: int,
    col: int,
    *,
    half: int = DEFAULT_HALF,
    min_index: int,
    max_index: int,
) -> set[Cell]:
    """Return the exact key set a window of ``half`` centred on ``(row, col)`` produces."""
    return {
        (r, c)
        for r in range(max(min_index, row - half), min(max_index, row + half) + 1)
        for c in range(max(min_index, col - half), min(max_index, col + half) + 1)
    }


def certainty_likelihood(
    cell: Cell, *, grid_size: int, start: int = 0, floor: float = 0.0
) -> dict[Cell, float]:
    """Return a likelihood that puts all its evidence on one located cell.

    The default ``floor`` of zero is deliberate: the geometric fix is verified, not
    inferred, so hedging it would only dilute a certainty into the flat prior the whole
    module exists to escape.
    """
    return {
        (r, c): (1.0 if (r, c) == cell else floor)
        for r in range(start, start + grid_size)
        for c in range(start, start + grid_size)
    }
