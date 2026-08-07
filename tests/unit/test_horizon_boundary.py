"""`M3-07b`: the survival horizon is inclusive, pinned at the boundary.

`C-024` records a real defect in the source and `U-027` names both readings. Chapter 3
table 2 defines survival as surviving "the limit of valid moves", and Appendix F table 15
makes that limit **equal** to the survival threshold — so surviving *exactly* the threshold
is a Thief win, and the horizon is inclusive.

`M3-07` chose that reading from the book without needing an owner ruling. This is the test
that stops the choice drifting, and it is worth having because the two readings differ by one
turn and cost a whole sub-game. An off-by-one here does not crash or look wrong; it quietly
awards 20 points to the wrong side, and the score is the only place it shows.

Three points are asserted rather than one, because a single assertion at `threshold` cannot
tell an inclusive horizon from an exclusive one — both stop somewhere near it. Only
`threshold-1`, `threshold` and `threshold+1` together fix which.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.domain.scoring import Outcome
from tests.unit.test_sub_game import Opponent, play, turn

THRESHOLD = 5


def survives_for(turns: int):
    """Play a sub-game in which the Thief answers `turns` times and is never caught."""
    return play(Opponent(*(turn(n) for n in range(1, turns + 1))), threshold=THRESHOLD)


def test_one_turn_short_of_the_threshold_is_not_yet_survival() -> None:
    """`threshold-1`. Stopping here would mean the horizon is exclusive, and the Thief would
    be credited a win it has not finished earning."""
    result = survives_for(THRESHOLD - 1)
    assert result.outcome is not Outcome.SURVIVAL, (
        f"a Thief that lasted {THRESHOLD - 1} of {THRESHOLD} turns must not already have "
        "survived; the horizon would be exclusive")


def test_reaching_the_threshold_exactly_is_survival() -> None:
    """**The row.** Table 2 defines survival as surviving "the limit of valid moves" and
    table 15 makes that limit the threshold, so the boundary turn counts."""
    result = survives_for(THRESHOLD)
    assert result.outcome is Outcome.SURVIVAL
    assert result.steps == THRESHOLD


def test_the_loop_stops_at_the_threshold_rather_than_running_past_it() -> None:
    """`threshold+1`. An inclusive horizon that kept going would let the Cop capture on a
    turn the Thief had already won — the same off-by-one, costing the other side."""
    result = play(Opponent(*(turn(n) for n in range(1, THRESHOLD + 2))), threshold=THRESHOLD)
    assert result.steps == THRESHOLD, "the loop ran past an inclusive horizon"


@pytest.mark.parametrize("threshold", [1, 2, 35])
def test_the_boundary_holds_at_every_threshold_not_just_the_default(threshold: int) -> None:
    """Appendix F marks the threshold a `Minimum`: it may be raised by agreement, so the
    reading has to hold wherever it is set. A rule that is only right at 5 is a coincidence."""
    result = play(Opponent(*(turn(n) for n in range(1, threshold + 1))), threshold=threshold)
    assert result.outcome is Outcome.SURVIVAL
    assert result.steps == threshold
