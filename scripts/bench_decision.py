"""Benchmark the worst-case per-turn decision cost (M6-13a).

The academic claim behind `M6-03c` is that a full turn's decision -- belief update plus
the pursuit policy -- returns well inside the negotiated 30 s response timeout `[AF-t19]`,
because every step is `O(grid^2)` with no I/O `[PARAMETERS_BASELINE table 19]`. This
script turns that *by-construction* argument into a *measurement*: it times the real
decision path at increasing board sizes and reports the headroom.

The worst case is built deliberately, not sampled:

* a **saturated** observed scent field -- every one of ``grid^2`` cells carries scent --
  so ``scent_likelihood`` and ``Belief.updated`` each do their maximum per-cell work and
  ``Belief.most_likely`` sorts the whole board;
* the belief's argmax lands on the **far corner** ``(grid-1, grid-1)`` (the row-major max
  of a uniform field), the cell furthest from the Cop at ``(0, 0)``;
* an **open board** (no barriers), which is the true worst case for the barrier-aware
  BFS: every cell is reachable, so ``step_distances`` floods all ``grid^2`` of them --
  barriers only ever *reduce* the reachable set, never enlarge it.

Run it directly (``python scripts/bench_decision.py``); it prints one row per board size.
Recording the numbers into the formal research evidence is `M6-13b`, deferred to `M9-06`.
"""

from __future__ import annotations

from collections.abc import Callable
from statistics import median
from time import perf_counter

from p2p_cop_agent.domain import Board, Coordinate
from p2p_cop_agent.strategy.belief import Belief, scent_likelihood
from p2p_cop_agent.strategy.belief_pursuit import pursue_belief

RESPONSE_TIMEOUT_S = 30.0
DEFAULT_GRIDS = (7, 10, 25, 50, 100)
DEFAULT_REPEATS = 20


def saturated_field(grid: int) -> dict[tuple[int, int], float]:
    """Return a scent reading with every cell at the emission centre (worst case)."""
    return {(row, col): 0.9 for row in range(grid) for col in range(grid)}


def belief_update(observed: dict[tuple[int, int], float], grid: int) -> Belief:
    """Run the full Cop-local belief update for one observation (M6-13a's subject)."""
    return Belief.uniform(grid).updated(scent_likelihood(observed, grid))


def full_decision(grid: int) -> None:
    """Run one whole per-turn decision at ``grid``: belief update, then pursuit."""
    board = Board(grid, 0, "top-left")
    belief = belief_update(saturated_field(grid), grid)
    pursue_belief(board, Coordinate(0, 0), belief)


def measure(work: Callable[[], object], repeats: int) -> tuple[float, float]:
    """Return the ``(min, median)`` seconds of ``repeats`` runs of ``work``.

    ``min`` is the least-noisy estimate of the operation's own cost; ``median`` reflects
    a typical run. Both are reported so a noisy machine does not hide a real regression.
    """
    samples = []
    for _ in range(repeats):
        start = perf_counter()
        work()
        samples.append(perf_counter() - start)
    return min(samples), median(samples)


def benchmark(
    grids: tuple[int, ...] = DEFAULT_GRIDS,
    repeats: int = DEFAULT_REPEATS,
) -> list[tuple[int, float, float, float, float]]:
    """Return ``(grid, belief_min, belief_med, full_min, full_med)`` per board size."""
    rows = []
    for grid in grids:
        observed = saturated_field(grid)
        b_min, b_med = measure(lambda o=observed, g=grid: belief_update(o, g), repeats)
        f_min, f_med = measure(lambda g=grid: full_decision(g), repeats)
        rows.append((grid, b_min, b_med, f_min, f_med))
    return rows


def _format(rows: list[tuple[int, float, float, float, float]]) -> str:
    """Render the benchmark rows as a millisecond table with timeout headroom."""
    header = f"{'grid':>6} {'cells':>7} {'belief ms':>11} {'decision ms':>13} {'headroom x':>12}"
    lines = [header, "-" * len(header)]
    for grid, _b_min, b_med, _f_min, f_med in rows:
        headroom = RESPONSE_TIMEOUT_S / f_med if f_med > 0 else float("inf")
        lines.append(
            f"{grid:>6} {grid * grid:>7} {b_med * 1e3:>11.3f} "
            f"{f_med * 1e3:>13.3f} {headroom:>12,.0f}"
        )
    lines.append(f"\nresponse timeout: {RESPONSE_TIMEOUT_S:.0f} s (Appendix F table 19)")
    return "\n".join(lines)


def main() -> int:
    """Print the worst-case decision-cost table across the default board sizes."""
    print(_format(benchmark()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
