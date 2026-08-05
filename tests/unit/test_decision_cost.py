"""M6-13a: the worst-case per-turn decision stays cheap and bounded.

These guard the `M6-03c` claim that a turn returns well inside the 30 s response timeout.
Two are deterministic structural checks of the `O(grid^2)` shape; the third is a single,
deliberately *loose* wall-clock ceiling -- a catastrophic-regression guard (it would fire
only on an accidental exponential blow-up), not a precise benchmark. The real measurement
across board sizes is `scripts/bench_decision.py`.
"""

from __future__ import annotations

from math import isfinite
from time import perf_counter

import pytest

from scripts.bench_decision import (
    RESPONSE_TIMEOUT_S,
    belief_update,
    benchmark,
    full_decision,
    saturated_field,
)


@pytest.mark.parametrize("grid", [7, 10, 25])
def test_belief_update_is_sized_to_the_board_and_normalised(grid: int) -> None:
    """Belief carries exactly grid^2 cells and stays a distribution -- the O(grid^2) shape."""
    belief = belief_update(saturated_field(grid), grid)
    assert len(belief.probabilities) == grid * grid
    assert sum(belief.probabilities.values()) == pytest.approx(1.0)


def test_benchmark_reports_positive_finite_costs() -> None:
    """The harness runs and every timing is a real, positive, finite number of seconds."""
    rows = benchmark(grids=(7, 10), repeats=3)
    assert [row[0] for row in rows] == [7, 10]
    for _grid, b_min, b_med, f_min, f_med in rows:
        for value in (b_min, b_med, f_min, f_med):
            assert isfinite(value) and value > 0.0
        # Belief update is one component of the whole decision, so it cannot cost more.
        assert b_min <= f_min


def test_worst_case_decision_stays_well_inside_the_timeout() -> None:
    """A loose ceiling that only a catastrophic (super-polynomial) regression could break.

    A 30x30 worst-case decision measures in tens of milliseconds; asserting it under a
    generous 5 s bound will not flake on a slow machine yet still catches an accidental
    exponential blow-up. The precise headroom table is the benchmark script's job.
    """
    start = perf_counter()
    full_decision(30)
    elapsed = perf_counter() - start
    assert elapsed < 5.0
    assert elapsed < RESPONSE_TIMEOUT_S  # the real contractual bound, with vast margin
