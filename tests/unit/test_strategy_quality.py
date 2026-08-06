"""M6-20/M6-20b: the belief strategy must beat the blind baseline, or be reverted.

The row's condition is unusually sharp — "**must beat the blind baseline or be
reverted**" — so this file exists to make that condition enforceable rather than a claim
in a README that nobody re-checks. If a future change breaks belief-driven pursuit badly
enough to lose its advantage, the suite fails here and the claim in the report cannot
quietly become false.

`inst/police_thief_p2p_Summary.md:3115` requires "the empirical evidence for their
success" but specifies **no** run count, seed policy, significance test, or baseline, so
the protocol is ours; `scripts/compare_strategies.py` and `docs/PRD_strategy.md` state it
in full.

The bounds below are deliberately **loose**. Pinning 21-0 exactly would make the file a
change-detector that fails on any harmless retune; the assertions instead encode the
*claim* — a large, one-directional advantage — with room for the number to move.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from compare_strategies import ARMS, SEEDS, paired, run_arm, summarise  # noqa: E402


@pytest.fixture(scope="module")
def arms() -> dict[str, list[tuple[bool, int, int]]]:
    """Play every arm once for the whole module; the runs are pure and deterministic."""
    return {name: run_arm(name) for name in ARMS}


def test_belief_beats_the_blind_baseline_on_score(arms) -> None:
    """`M6-20`'s condition, on the book's own metric (Appendix F table 17)."""
    blind, belief = summarise(arms["blind"]), summarise(arms["belief"])
    assert belief["mean_cop_score"] > blind["mean_cop_score"]
    assert belief["capture_rate"] > blind["capture_rate"] * 2


def test_the_advantage_is_one_directional_across_seeds(arms) -> None:
    """The paired form, and the strongest claim the design supports.

    Every arm met the identical Thief trajectory on a given seed, so this compares
    matched pairs rather than two averages. Belief must never lose a seed the blind Cop
    won: a strategy that traded some seeds for others would be a different trade-off,
    not an improvement, and the report would have to say so.
    """
    result = paired(arms["belief"], arms["blind"])
    assert result["seeds_worse_captured_only"] == 0
    assert result["seeds_better_captured_only"] >= len(SEEDS) // 2


def test_belief_closes_most_of_the_gap_to_a_cheating_cop(arms) -> None:
    """The oracle arm is the reason the headline number means anything.

    Beating a random walk is a low bar. `oracle` — which reads the Thief's true cell and
    is therefore not a legal agent — is the ceiling, and belief must land near it rather
    than merely above the floor.
    """
    blind, belief, oracle = (summarise(arms[k]) for k in ("blind", "belief", "oracle"))
    gap = oracle["mean_cop_score"] - blind["mean_cop_score"]
    assert gap > 0, "the oracle must actually be better than random, or the arms are broken"
    assert (belief["mean_cop_score"] - blind["mean_cop_score"]) / gap > 0.75


def test_belief_catches_faster_than_the_blind_cop(arms) -> None:
    """Turn count is the reference's own recorded metric (`steps`), so it is reported
    alongside score rather than instead of it."""
    assert summarise(arms["belief"])["mean_turns"] < summarise(arms["blind"])["mean_turns"]


def test_the_oracle_never_loses_to_belief_on_a_seed(arms) -> None:
    """A sanity check on the harness, not on strategy. If belief ever beat a Cop that
    reads the true position, the arms would be mis-wired and every number above would be
    describing something other than what it claims."""
    assert paired(arms["belief"], arms["oracle"])["seeds_better_captured_only"] == 0


def test_the_measurement_is_reproducible(arms) -> None:
    """`M6-20a` requires fixed seeds. A number that moved between runs could not be put
    in a report at all."""
    assert run_arm("belief") == arms["belief"]
    assert run_arm("blind") == arms["blind"]
