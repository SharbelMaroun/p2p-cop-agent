"""The two shortcuts `evaluate` takes, measured against what each one replaced.

Both are arguments about graph structure that the evaluation then trusts absolutely, and
neither fails loudly when it is wrong: a bad separation verdict is worth -500 points to the
search, and a bad component count silently shifts every leaf's cycle term and mis-prices
the barrier quota. Each is therefore checked over the same sweep of random positions rather
than argued for in a comment and left there.

Kept apart from `test_bitboard.py` because these are claims about the *evaluator*, not about
the primitives -- and because adding the second one pushed that file past the 150-line gate,
which is split by responsibility rather than answered by trimming the reasoning (`M9-21`).
"""

from __future__ import annotations

import random
from collections.abc import Iterator

from p2p_cop_agent.strategy.bitboard import (
    components,
    cycle_rank,
    distance_between,
    popcount,
    spread,
)
from p2p_cop_agent.strategy.engine_eval import bit_of, free_mask, thief_region

SIZE = 7


def positions(count: int = 3_000) -> Iterator[tuple[int, int, int]]:
    """Yield ``(cop, thief, free)`` over randomly barriered boards, seeded and reproducible.

    Up to twenty barriers on a 7x7 board, which is the quota a real game may spend, so the
    sample reaches genuinely partitioned boards rather than only lightly obstructed ones.
    """
    rng = random.Random(20260813)
    for _ in range(count):
        walls = frozenset((rng.randrange(SIZE), rng.randrange(SIZE))
                          for _ in range(rng.randrange(0, 20)))
        free = free_mask(SIZE, walls)
        cells = [index for index in range(SIZE * SIZE) if free & (1 << index)]
        if len(cells) < 2:
            continue
        cop, thief = rng.sample(cells, 2)
        yield cop, thief, free


def test_the_cheap_separation_test_agrees_with_a_real_search() -> None:
    """`evaluate` decides "am I sealed off?" with one spread instead of a BFS.

    The argument is that `thief_region` is the Thief's component of the board with the Cop's
    own cell removed, so a path from the Thief to the Cop exists exactly when some cell of
    that component is adjacent to the Cop -- the step before the last one on any such path
    is in the component by construction. The argument is sound; this checks it anyway.
    """
    separated = 0
    for cop, thief, free in positions():
        region = thief_region(cop, thief, free, SIZE)
        cheap = bool(spread(region, SIZE) & bit_of(cop, SIZE))
        searched = distance_between(bit_of(cop, SIZE), bit_of(thief, SIZE), free, SIZE) >= 0
        assert cheap is searched
        separated += not searched
    assert separated > 100, "the sample must actually contain sealed-off positions"


def test_the_regions_the_search_evaluates_are_always_one_component() -> None:
    """`evaluate` hands `cycle_rank` a `parts=1` that nothing downstream verifies.

    `thief_region` returns a `flood`, which is connected by construction -- load-bearing
    rather than obvious, since an over-count would inflate the cycle term on exactly the
    positions the barrier quota is meant to price. The region is never empty either: the
    Thief stands on a free cell and removing the Cop's cell cannot take it away, so the
    supplied count is reached on every position the search can actually build.
    """
    confined = 0
    for cop, thief, free in positions():
        region = thief_region(cop, thief, free, SIZE)
        assert components(region, SIZE) == 1
        assert cycle_rank(region, SIZE, parts=1) == cycle_rank(region, SIZE)
        confined += popcount(region) < popcount(free) - 1
    assert confined > 100, "the sample must actually contain regions the Cop cuts down"
