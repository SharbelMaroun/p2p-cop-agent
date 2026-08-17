"""C-043: the emailed report matches the book's own [Result File] template.

The book attaches the template as `final-result.txt`; the notebook quoted it verbatim
on 2026-08-12. The old builder diverged in eight places -- wrong `report_type`, no
`links` block, one commit hash instead of rule 53's per-game-per-team dicts, a bare
boolean where `:2220` demands SHA-256 mutual agreement -- and a template-shaped
opponent (uoh-ay26's converter is one) meeting our old artifact in a counted series
is rule 35's structurally-conflicting-reports 0/0.
"""

import pytest

from p2p_cop_agent.reporting.result_template import (
    ResultTemplateError,
    build_final_result,
    sub_game_row,
)

GROUPS = ["sharNamr", "uoh-ay26"]
REPOS = ["https://a/cop", "https://a/thief", "https://b/cop", "https://b/thief"]


def summary(n: int, role: str, result: str) -> dict:
    return {"sub_game_number": n, "group_id": "sharNamr", "role": role,
            "opponent_group_id": "uoh-ay26", "result": result,
            "started_at": f"2026-08-12T19:0{n}:00+00:00",
            "ended_at": f"2026-08-12T19:0{n}:59+00:00",
            "tokens_total": 0, "game_id": "game-5a7b4a6e58be",
            "github_commit": {"sharNamr": "a" * 40, "uoh-ay26": "b" * 40}}


def six_rows() -> list[dict]:
    plan = [(1, "thief", "survival"), (2, "police", "capture"), (3, "thief", "survival"),
            (4, "police", "capture"), (5, "thief", "survival"), (6, "police", "capture")]
    return [sub_game_row(summary(n, role, res), GROUPS) for n, role, res in plan]


def build(rows=None, **overrides) -> dict:
    kwargs = {"game_id": "game-5a7b4a6e58be", "game_uid": "5a7b4a6e58be" + "0" * 20,
              "groups": GROUPS, "rows": rows if rows is not None else six_rows(),
              "repositories": REPOS, "config_sha256": "c" * 64}
    kwargs.update(overrides)
    return build_final_result(**kwargs)


def test_the_template_top_level_shape() -> None:
    result = build()
    assert result["report_type"] == "final_game_result"
    assert set(result["links"]) == {"declaration", "config", "log", "result"}
    assert result["groups"] == GROUPS
    assert result["num_sub_games"] == 6
    assert result["mutual_agreement"] == {"sha256": "c" * 64, "confirmed": True}


def test_per_sub_game_rows_carry_per_team_members() -> None:
    """Rule 53's commit hash is per game, per team -- never one for the series."""
    row = build()["sub_games"][1]
    assert row["roles"] == {"sharNamr": "cop", "uoh-ay26": "thief"}
    assert row["github_commit"] == {"sharNamr": "a" * 40, "uoh-ay26": "b" * 40}
    assert row["score"] == {"sharNamr": 20, "uoh-ay26": 5}


def test_an_unverified_log_is_reported_unverified() -> None:
    """This asserted `{"log_verified": True, "tampered": False}` until 2026-08-17.

    It passed because the template emitted those literals unconditionally, so the test and
    the code agreed on a claim neither had earned -- every report said the log had been
    verified when nothing had checked one. The fixture summary carries no `audit`, so the
    honest answer here is NOT verified, and that is now what both assert.
    `reporting.log_audit` supplies the real value when a log is present.
    """
    row = build()["sub_games"][1]
    assert row["audit"]["log_verified"] is False
    assert row["audit"]["steps_checked"] == 0


def test_a_verified_log_carries_its_verdict_through() -> None:
    earned = {"log_verified": True, "tampered": False, "steps_checked": 25}
    row = sub_game_row({**summary(2, "police", "capture"), "audit": earned}, GROUPS)
    assert row["audit"] == earned


def test_the_series_totals_read_ninety_thirty() -> None:
    final = build()["final_result"]
    assert final["total_score"] == {"sharNamr": 90, "uoh-ay26": 30}
    assert final["sub_games_won"] == {"sharNamr": 6, "uoh-ay26": 0}
    assert final["winner_group"] == "sharNamr"
    assert final["series_tie"] is False


def test_survival_scores_the_thief_side() -> None:
    row = build()["sub_games"][0]
    assert row["roles"]["sharNamr"] == "thief"
    assert row["score"] == {"sharNamr": 10, "uoh-ay26": 5}
    assert row["winner_group"] == "sharNamr"


def test_non_contiguous_sub_games_are_refused() -> None:
    rows = six_rows()
    del rows[2]
    with pytest.raises(ResultTemplateError, match="contiguous"):
        build(rows=rows)


def test_rule_49_requires_exactly_four_links() -> None:
    with pytest.raises(ResultTemplateError, match="4 links"):
        build(repositories=REPOS[:3])


def test_a_log_naming_the_wrong_groups_is_refused() -> None:
    bad = summary(1, "thief", "survival")
    bad["opponent_group_id"] = "someone-else"
    with pytest.raises(ResultTemplateError, match="names"):
        sub_game_row(bad, GROUPS)


def test_missing_commits_degrade_to_unknown_not_a_crash() -> None:
    """Old logs predate the enrichment; the builder must not fabricate hashes."""
    s = summary(1, "thief", "survival")
    del s["github_commit"]
    row = sub_game_row(s, GROUPS)
    assert row["github_commit"] == {"sharNamr": "unknown", "uoh-ay26": "unknown"}

def test_a_series_tie_adds_the_fixed_draw_score() -> None:
    """Table 17 row 5 (Fixed): 2 to each side on a cumulative draw -- 47-47 for a
    six-survival series, matching the opponent's live G004 aggregate exactly."""
    plan = [(n, role, "survival") for n, role in
            [(1, "thief"), (2, "police"), (3, "thief"), (4, "police"),
             (5, "thief"), (6, "police")]]
    rows = [sub_game_row(summary(n, role, res), GROUPS) for n, role, res in plan]
    final = build(rows=rows)["final_result"]
    assert final["total_score"] == {"sharNamr": 47, "uoh-ay26": 47}
    assert final["series_tie"] is True
    assert final["winner_group"] is None
    assert final["sub_games_won"] == {"sharNamr": 3, "uoh-ay26": 3}
