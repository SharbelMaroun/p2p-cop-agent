"""`M7-03b`–`M7-03d`, `M7-14`: the emailed report, and the gate in front of sending.

Three Mandatory rules meet in the result artifact — 49 (four repository links), 53 (the
per-game commit hash), 54 (tokens per game *and* in the sequence) — and a fourth governs
whether it may be sent at all. Rule 35: "a conflicting report causes disqualification of
the game and **a score of 0 for both teams**."

That asymmetry is why the checks here refuse rather than warn. `:2584` says a side that
does not report "will not be credited" — a cost to us alone. A *bad* report costs the
opponent too, so sending one is worse than sending nothing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_cop_agent.reporting import MatchIdentity
from p2p_cop_agent.reporting.result_artifact import ResultArtifactError, build_result

ROOT = Path(__file__).resolve().parents[2]
GAME = json.loads((ROOT / "shared_contract" / "fixtures" / "match_config.example.json").read_text("utf-8"))
IDENT = MatchIdentity("demo-series", "b" * 32)
GROUPS = [
    {"group_id": "alpha", "repos": {"cop": "https://x/a-cop", "thief": "https://x/a-thief"}},
    {"group_id": "beta", "repos": {"cop": "https://x/b-cop", "thief": "https://x/b-thief"}},
]
SUB_GAMES = [
    {"sub_game": 1, "outcome": "capture", "cop_score": 20, "thief_score": 5, "tokens": 120},
    {"sub_game": 2, "outcome": "survival", "cop_score": 5, "thief_score": 10, "tokens": 80},
]


def _result(**kw):
    kwargs = {"identity": IDENT, "groups": GROUPS, "sub_games": SUB_GAMES,
              "commit_hash": "abc1234", "mutual_agreement": True}
    kwargs.update(kw)
    return build_result(**kwargs)


# --- the emailed report ----------------------------------------------------------------


def test_it_carries_exactly_four_repository_links() -> None:
    """Rule 49 (Mandatory): "four links in the JSON files of the two teams"."""
    assert len(_result()["repositories"]) == 4


def test_a_group_short_of_its_two_repositories_is_refused() -> None:
    """Three links means one side's submission is wrong; better to fail here than to file
    a report the lecturer cannot follow back to the code."""
    thin = [GROUPS[0], {"group_id": "beta", "repos": {"cop": "https://x/b-cop"}}]
    with pytest.raises(ResultArtifactError, match="exactly 4 repository links"):
        _result(groups=thin)


def test_it_carries_the_commit_hash_that_played() -> None:
    """Rule 53 (Mandatory): code may change between games, so a result that does not say
    *which* code played it cannot be reproduced."""
    assert _result()["commit_hash"] == "abc1234"
    with pytest.raises(ResultArtifactError, match="identify the code that played"):
        _result(commit_hash="")


def test_tokens_are_reported_per_sub_game_and_for_the_series() -> None:
    """Rule 54 (Mandatory): "the total number of tokens required for the game **and in
    the sequence**" — two numbers, not one."""
    report = _result()
    assert [line["tokens"] for line in report["sub_games"]] == [120, 80]
    assert report["final_result"]["tokens_total"] == 200


def test_the_cumulative_result_sums_the_sub_games() -> None:
    assert _result()["final_result"] == {
        "cop_score": 25, "thief_score": 15, "tokens_total": 200, "winner": "cop",
    }


def test_an_equal_total_is_reported_as_a_tie_not_left_blank() -> None:
    """`:2042`: an equal accumulated score means each group receives a "Tie Score" — a
    result in its own right, so the report must name it."""
    drawn = [{**SUB_GAMES[0], "cop_score": 10, "thief_score": 10}]
    assert _result(sub_games=drawn)["final_result"]["winner"] == "tie"


def test_an_unagreed_result_is_refused_before_it_can_be_sent() -> None:
    """Rule 35 (Mandatory): "a conflicting report causes disqualification of the game and
    a score of 0 for **both teams**". Not sending costs only us (`:2584`); sending a
    contradictory one costs the opponent too, so this refuses rather than warns."""
    with pytest.raises(ResultArtifactError, match="0 for BOTH teams"):
        _result(mutual_agreement=False)


def test_a_report_with_no_sub_games_is_refused() -> None:
    with pytest.raises(ResultArtifactError, match="nothing to score"):
        _result(sub_games=[])


def test_a_sub_game_line_missing_a_field_is_refused_by_name() -> None:
    with pytest.raises(ResultArtifactError, match="tokens"):
        _result(sub_games=[{k: v for k, v in SUB_GAMES[0].items() if k != "tokens"}])


def test_agreement_can_be_earned_by_a_settlement_rather_than_asserted() -> None:
    """`M7-18c` closing the loop. `mutual_agreement` began as a bool a caller asserted —
    which meant a report could claim agreement that never happened. It now also accepts a
    `Settlement`, whose `reportable` is only true after the audit passed *and* both sides
    returned the same outcome."""
    from p2p_cop_agent.orchestration.settlement import Settled, Settlement

    agreed = Settlement(Settled.AGREED, "capture", "capture")
    assert _result(mutual_agreement=agreed)["mutual_agreement"] is True

    conflicted = Settlement(Settled.CONFLICT, "capture", "survival")
    with pytest.raises(ResultArtifactError, match="0 for BOTH teams"):
        _result(mutual_agreement=conflicted)
