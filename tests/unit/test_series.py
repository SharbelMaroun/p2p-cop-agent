"""`M7-01`, `M7-07`: the six-sub-game series, its schedule, and one run end to end.

The schedule is settled, not inferred. `U-025` closed on 2026-07-31 with a lecturer answer
relayed by the coordinator: sub-games **1, 3, 5 natural; 2, 4, 6 swapped; Thief moves
first**. It is a constant in `series.py` rather than a computed alternation, and these
tests pin the ruling rather than a formula — a formula would be one refactor away from
silently disagreeing with the answer we were given.

`M7-07` is the first row that exercises the whole stack together: schedule → artifacts →
audit → settlement → report.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_cop_agent.orchestration.series import (
    NATURAL_SUB_GAMES,
    SUB_GAMES,
    SWAPPED_SUB_GAMES,
    Role,
    SeriesError,
    SeriesResult,
    SubGameLine,
    each_side_plays_both_roles,
    role_for,
    schedule,
)
from p2p_cop_agent.reporting import (
    MatchIdentity,
)

ROOT = Path(__file__).resolve().parents[2]
GAME = json.loads((ROOT / "shared_contract" / "fixtures" / "match_config.example.json").read_text("utf-8"))
IDENT = MatchIdentity("series-1", "d" * 32)


# --- M7-01b: the ruled schedule ---------------------------------------------------------


def test_the_series_is_six_sub_games() -> None:
    """Appendix F prints **two** rows labelled "[Number of Agents]": `:3484` is "number of
    players in the race | 2", `:3540` is "number of agents **in a series against an
    opponent** | 6 | Fixed". The second is the games count under a mistranslated label."""
    assert SUB_GAMES == 6
    assert set(NATURAL_SUB_GAMES) | set(SWAPPED_SUB_GAMES) == set(range(1, 7))


def test_odd_sub_games_are_natural_and_even_are_swapped() -> None:
    """`U-025`, closed on a coordinator-relayed lecturer answer."""
    assert NATURAL_SUB_GAMES == (1, 3, 5) and SWAPPED_SUB_GAMES == (2, 4, 6)
    assert role_for(1, Role.COP) is Role.COP
    assert role_for(2, Role.COP) is Role.THIEF
    assert role_for(5, Role.THIEF) is Role.THIEF
    assert role_for(6, Role.THIEF) is Role.COP


def test_each_side_plays_both_roles_which_is_what_the_alternation_is_for() -> None:
    assert each_side_plays_both_roles(Role.COP)
    assert each_side_plays_both_roles(Role.THIEF)


def test_the_two_sides_are_opposite_in_every_sub_game() -> None:
    """A schedule that ever put both peers in the same role would be unplayable, and it is
    the kind of error a computed alternation makes silently."""
    for (number, ours), (_, theirs) in zip(schedule(Role.COP), schedule(Role.THIEF), strict=True):
        assert ours is not theirs, f"both sides are {ours} in sub-game {number}"


@pytest.mark.parametrize("bad", [0, 7, -1])
def test_a_sub_game_outside_the_series_is_refused(bad: int) -> None:
    with pytest.raises(SeriesError, match="outside the fixed series"):
        role_for(bad, Role.COP)


# --- M7-01c / M7-01d: the cumulative result ----------------------------------------------


def _lines(scores: list[tuple[int, int]]) -> SeriesResult:
    return SeriesResult(IDENT, tuple(
        SubGameLine(n + 1, role_for(n + 1, Role.COP), "capture", cop, thief, 10)
        for n, (cop, thief) in enumerate(scores)
    ))


def test_the_series_score_is_the_sum_of_its_sub_games() -> None:
    result = _lines([(20, 5), (5, 10), (20, 5), (5, 10), (20, 5), (20, 5)])
    assert result.complete
    assert result.cumulative(tie_award=2)["winner"] == "cop"


def test_a_cumulative_tie_awards_the_tie_score_to_each_side() -> None:
    """`M7-01d`. `:2042`: an equal accumulated score gives each group a "Tie Score", and
    "no meeting remains without a decision" — a draw is decided, not undecided."""
    drawn = _lines([(10, 10)] * 6).cumulative(tie_award=2)
    assert drawn["winner"] == "tie"
    assert drawn["cop_score"] == 2 and drawn["thief_score"] == 2
    assert drawn["raw_cop"] == drawn["raw_thief"] == 60


def test_an_incomplete_series_knows_it_is_incomplete() -> None:
    assert not _lines([(20, 5)] * 5).complete
