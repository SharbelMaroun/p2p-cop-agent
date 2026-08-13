"""The board as one integer, so a search can afford to look several turns ahead (M11-02).

A 7x7 board is 49 cells, and Python integers are arbitrarily wide, so the whole free
space fits in a single int with one bit per cell. Every question the evaluation asks --
what can the Thief still reach, is that region a tree, how far apart are we -- becomes a
handful of shifts and masks instead of a dictionary walk over `Coordinate` objects.

That is the difference between a search that sees two turns ahead and one that sees
five. The shipped `pursuit.step_distances` builds a dict per call and is perfectly clear;
it is also about two orders of magnitude too slow to sit inside an alpha-beta inner loop
with a thirty-second turn deadline overhead.

Row-major bit order: cell ``(r, c)`` is bit ``r * size + c``. Direction shifts mask the
wrapping columns first, which is the only subtlety here -- moving west from column 0 must
leave the board, not reappear on the far edge of the row above.
"""

from __future__ import annotations

from functools import lru_cache

Cell = tuple[int, int]


@lru_cache(maxsize=8)
def masks(size: int) -> tuple[int, int, int]:
    """Return ``(full, not_first_column, not_last_column)`` for a ``size`` board."""
    full = (1 << (size * size)) - 1
    first = sum(1 << (row * size) for row in range(size))
    last = sum(1 << (row * size + size - 1) for row in range(size))
    return full, full ^ first, full ^ last


def bit(cell: Cell, size: int) -> int:
    """Return the single-bit mask for one cell."""
    return 1 << (cell[0] * size + cell[1])


def cell_of(index: int, size: int) -> Cell:
    """Return the ``(row, col)`` a bit index names."""
    return divmod(index, size)


def spread(region: int, size: int) -> int:
    """Return ``region`` plus every cell orthogonally adjacent to it (no board limits)."""
    _, not_first, not_last = masks(size)
    return (region
            | (region >> size)
            | (region << size)
            | ((region & not_first) >> 1)
            | ((region & not_last) << 1))


@lru_cache(maxsize=4096)
def neighbours(cell: Cell, size: int) -> int:
    """Return the mask of cells one orthogonal step from ``cell``, on-board only.

    Cached: the search asks this for the same handful of cells thousands of times per
    decision, and the answer depends on nothing that changes during a game.
    """
    full, _, _ = masks(size)
    single = bit(cell, size)
    return (spread(single, size) ^ single) & full


def flood(start: int, free: int, size: int) -> int:
    """Return every free cell reachable from ``start`` through ``free``.

    Standard bitwise flood fill: grow by one ring per iteration and stop when a round
    adds nothing. Bounded by the board's diameter, so it terminates in at most
    ``2 * size`` rounds.
    """
    region = start & free
    while True:
        grown = spread(region, size) & free
        if grown == region:
            return region
        region = grown


def popcount(mask: int) -> int:
    """Return the number of set bits."""
    return mask.bit_count()


def distances(start: int, free: int, size: int) -> list[int]:
    """Return the step distance from ``start`` to every cell, ``-1`` where unreachable.

    One ring per step, so the whole distance map costs a flood fill rather than a
    per-cell search.
    """
    result = [-1] * (size * size)
    seen = start & free
    frontier = seen
    step = 0
    while frontier:
        remaining = frontier
        while remaining:
            low = remaining & -remaining
            result[low.bit_length() - 1] = step
            remaining ^= low
        step += 1
        frontier = spread(seen, size) & free & ~seen
        seen |= frontier
    return result


def distance_between(start: int, target: int, free: int, size: int) -> int:
    """Return the step distance between two single-bit cells, or ``-1`` if unreachable.

    Stops the moment the target is reached, which is the whole point: the evaluation
    needs one number, and building the entire distance map to read one entry out of it
    was the single most expensive thing the search did.
    """
    if start & target:
        return 0
    seen = start & free
    if not seen:
        return -1
    step = 0
    while True:
        grown = spread(seen, size) & free
        if grown == seen:
            return -1
        step += 1
        if grown & target:
            return step
        seen = grown


def edge_count(region: int, size: int) -> int:
    """Return the number of orthogonally adjacent pairs inside ``region``."""
    _, _, not_last = masks(size)
    horizontal = popcount(region & (region & not_last) << 1)
    vertical = popcount(region & region << size)
    return horizontal + vertical


def cycle_rank(region: int, size: int) -> int:
    """Return the region's independent-cycle count, ``E - V + 1`` per component.

    Zero means the region is a forest, and a forest is the shape that decides this
    game: one pursuer catches an equal-speed evader on a tree, and cannot on a grid --
    a 7x7 grid needs two cops, which is precisely why every chase-only series ended in
    survival. Barriers are how a Cop turns the second into the first, so this is the
    quantity worth spending them on.
    """
    cells = popcount(region)
    if cells == 0:
        return 0
    return edge_count(region, size) - cells + components(region, size)


def components(region: int, size: int) -> int:
    """Return how many connected components ``region`` has."""
    remaining = region
    count = 0
    while remaining:
        low = remaining & -remaining
        remaining &= ~flood(low, region, size)
        count += 1
    return count
