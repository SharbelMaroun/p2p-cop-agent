"""The tournament boundary: the interception stack must hold it, or be reverted (M6-25).

`M6-20` set the discipline — a strategy claim nobody re-checks is a claim, not
evidence — and the opponent grid set the boundary: the incumbent converts flee_greedy
and loses the mobility-aware archetypes 0/40, oracle included. This file makes the
new boundary enforceable at league stakes: the interception stack must convert the
strong-classmate shapes, and it must never surrender an archetype the incumbent
already converts. Ten seeds per cell keeps the suite fast; the forty-seed record
lives in `results/tournament_grid.json` and the two are the same paired design.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from experiment_arena import CONFIG, SEEDS  # noqa: E402
from experiment_tournament import ARMS, THIEVES, play_cell  # noqa: E402

TEN = SEEDS[:10]


@pytest.fixture(scope="module")
def grid() -> dict[str, dict[str, dict]]:
    """Play the ten-seed grid once for the whole module; every run is deterministic."""
    return {arm: {thief: play_cell(CONFIG, arm, thief, TEN) for thief in THIEVES}
            for arm in ARMS}


def test_the_interception_stack_converts_the_mobility_aware_archetypes(grid) -> None:
    """The tournament condition itself: the shapes a strong classmate actually ships —
    distance-plus-mobility, and the companion repository's dead-end refusal — must be
    captured, not survived against. The bound is deliberately loose (9 of 10) so a
    harmless retune cannot fail it; losing the boundary outright must."""
    assert grid["shrink_stack"]["flee_smart"]["captures"] >= 9
    assert grid["shrink_stack"]["flee_deadend"]["captures"] >= 9


def test_no_archetype_the_incumbent_converts_is_surrendered(grid) -> None:
    """The composition promise, paired seed for seed: everything the shipped stack
    captures, the interception stack captures too."""
    for thief in THIEVES:
        assert (grid["shrink_stack"][thief]["captures"]
                >= grid["barrier_stack"][thief]["captures"]), thief


def test_belief_matches_the_truth_fed_ceiling(grid) -> None:
    """The decoded belief must not lag the oracle-aimed stack anywhere: `M6-24`
    reached parity and the chase change must keep it. A cell where truth beats
    belief again means the estimator regressed, not the strategy."""
    for thief in THIEVES:
        assert (grid["shrink_stack"][thief]["captures"]
                == grid["oracle_shrink"][thief]["captures"]), thief


def test_captures_stay_inside_the_horizon_with_walls_to_spare(grid) -> None:
    """Converted cells must end decisively — mean turns well under the 35-step
    horizon — or the capture is a horizon artifact a longer game would undo."""
    for thief in ("flee_smart", "flee_deadend"):
        assert grid["shrink_stack"][thief]["mean_turns"] < 30


def test_the_measurement_is_reproducible(grid) -> None:
    """Fixed seeds, no floats, no randomness: replaying one cell reproduces it."""
    again = play_cell(CONFIG, "shrink_stack", "flee_smart", TEN)
    assert again == grid["shrink_stack"]["flee_smart"]
