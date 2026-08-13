"""What a Cop position is worth, in the terms that actually decide this game (M11-02).

The chase heuristics in this repo all rank a position by distance to the Thief. That is
the right instinct and the wrong quantity: on a clean 7x7 grid an equal-speed evader with
full information is *uncatchable* by distance alone -- the grid needs two pursuers, which
is the structural reason every chase-only series ended in survival rather than anything
either implementation did wrong.

What one Cop can do is change the graph. A pursuer catches an evader on a **forest**, so
the barrier quota is not fourteen chances to inconvenience the Thief; it is fourteen
chances to remove a cycle from the region the Thief is confined to. So the evaluation
leads with region size and cycle rank and treats distance as the tie-break it is.

Weights are the tunable part and live in `WEIGHTS`, one dataclass, so a sweep can search
them without touching the search itself. Every term is signed from the Cop's point of
view: larger is better for the Cop.
"""

from __future__ import annotations

from dataclasses import dataclass

from p2p_cop_agent.strategy.bitboard import (
    bit,
    cycle_rank,
    distance_between,
    flood,
    popcount,
    spread,
)


@dataclass(frozen=True, slots=True)
class Weights:
    """The evaluation's tunable coefficients, all from the Cop's point of view.

    Scale matters as much as sign. The first set tried gave region -3 and cycles -8,
    which sounds like the right priority and is not: across a 49-cell board those terms
    range over roughly 150 and 290 while distance ranges over 12, so closing the gap was
    worth less than any incidental change in shape and the Cop preferred to build walls
    it had no plan for. These are balanced so that pursuit leads and structure decides
    between pursuits of equal length.

    ``barrier_tempo`` is the price of the turn a placement costs, and it exists because
    of a measured pathology rather than a principle. Searching **deeper made the Cop
    worse** against the simplest evader -- 1 capture in 24 against `flee_greedy` where a
    shallower search took 15 -- and the reason is that minimax assumes a perfect evader.
    Against one, no chase is ever forcing, so every closing move looks equal and the
    positional terms decide; the Cop walls patiently while a greedy runner it could have
    caught walks away. A real opponent is not perfect, and a forfeited move against an
    imperfect one is a real loss. Charging placement its tempo restores the pressure
    without giving up the seals the search finds.

    Its **magnitude is a genuine trade**, and overshooting it was instructive: at -6 the
    greedy runner recovered (1/24 to 10/24 deep, 15/24 to 21/24 shallow) while the
    interior-hugging evader collapsed from 18/24 to **0/24**, because that archetype is
    catchable only by spending barriers on it. Barriers are the answer to one opponent and
    a distraction against another, which is why this coefficient is searched rather than
    argued about.
    """

    region: float = -1.0
    cycles: float = -2.0
    distance: float = -4.0
    barriers_left: float = 0.25
    separated: float = -500.0
    thief_mobility: float = -1.0
    barrier_tempo: float = -2.0


WEIGHTS = Weights()

# A capture is worth more than any positional term can reach, and an earlier one is worth
# more than a later one, so the search prefers a forced capture now to a better-looking
# board later.
CAPTURE = 10_000.0


def thief_region(cop: int, thief: int, free: int, size: int) -> int:
    """Return the free cells the Thief can still reach, with the Cop's cell as a wall.

    Treating the Cop as blocking is the honest model: stepping onto the Cop is capture,
    so the Thief will never do it, and counting that cell as escape space would flatter
    every position where the Cop stands in a doorway.
    """
    return flood(bit_of(thief, size), free & ~bit_of(cop, size), size)


def bit_of(index: int, size: int) -> int:
    """Return the single-bit mask for a bit index (the search's cell representation)."""
    return 1 << index


def evaluate(
    cop: int,
    thief: int,
    free: int,
    barriers_left: int,
    size: int,
    weights: Weights = WEIGHTS,
) -> float:
    """Return the static value of a position for the Cop.

    ``free`` is the mask of unbarriered on-board cells; ``cop`` and ``thief`` are bit
    indices. Cheap by construction -- four flood fills and a distance map -- because this
    runs at every leaf of the search.
    """
    thief_bit = bit_of(thief, size)
    region = thief_region(cop, thief, free, size)
    value = (weights.region * popcount(region)
             + weights.cycles * cycle_rank(region, size)
             + weights.barriers_left * barriers_left)

    reach = distance_between(bit_of(cop, size), thief_bit, free, size)
    if reach < 0:
        # Sealed away from the Thief: the barriers meant to trap it trapped us instead,
        # and no amount of shrinking matters from the wrong side of the wall.
        return value + weights.separated
    value += weights.distance * reach

    exits = popcount(region & spread_one(thief_bit, size))
    return value + weights.thief_mobility * exits


def spread_one(mask: int, size: int) -> int:
    """Return the cells one orthogonal step from ``mask`` (excluding it)."""
    return spread(mask, size) & ~mask


def free_mask(size: int, barriers: frozenset[tuple[int, int]]) -> int:
    """Return the mask of on-board cells no barrier occupies."""
    full = (1 << (size * size)) - 1
    for cell in barriers:
        full &= ~bit(cell, size)
    return full
