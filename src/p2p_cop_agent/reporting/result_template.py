"""The official [Result File] template, built from a series' own logs (`C-043`).

The book attaches the exact template as `final-result.txt`, and the notebook quoted it
verbatim on 2026-08-12: `report_type: "final_game_result"`, a `links` block naming the
four artifact files, `groups` as two ids, per-sub-game rows with **per-team**
`github_commit`/`tokens`/`score` dicts (rule 53's hash is per game, `inst/:1295`,
`:3456`), a league-aware `final_result`, and `mutual_agreement` as `{sha256, confirmed}`
(`:2220`: "mutual agreement confirmations using SHA-256"). The older
`result_artifact.build_result` predates that reading and is superseded for anything
that leaves the machine; a counted series against a template-shaped opponent would
otherwise produce structurally conflicting reports — rule 35's 0/0.

`repositories` (rule 49's four links) rides as an additive member: the template does
not print it, but the book text mandates the links in the game-end JSON, and an extra
key breaks no template-shaped consumer.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from p2p_cop_agent.shared.config import JsonObject

SCHEMA_VERSION = "1.1"
SCORES = {"capture": {"police": 20, "thief": 5}, "survival": {"police": 5, "thief": 10},
          "technical_loss": {"police": 0, "thief": 0}}


class ResultTemplateError(ValueError):
    """Raised when a report would misstate the series or violate its template."""


def sub_game_row(summary: Mapping[str, object], groups: Sequence[str]) -> JsonObject:
    """Convert one log's summary into the template's per-sub-game row.

    The summary is one side's local truth; per-team members are derived from it. The
    opponent's token count is reported as 0 because this side cannot know it — each
    team's own report carries its own spend (rule 54), and inventing the opponent's
    would be a forged number in a signed artifact.
    """
    ours, theirs = str(summary["group_id"]), str(summary["opponent_group_id"])
    if sorted((ours, theirs)) != sorted(groups):
        raise ResultTemplateError(f"log names {ours}/{theirs}, series names {groups}")
    role = str(summary["role"])
    roles = {ours: "cop" if role == "police" else "thief",
             theirs: "thief" if role == "police" else "cop"}
    result = str(summary["result"])
    if result not in SCORES:
        raise ResultTemplateError(f"unknown result {result!r}")
    score_by_role = SCORES[result]
    score = {gid: score_by_role["police" if r == "cop" else r]
             for gid, r in roles.items()}
    winner_role = {"capture": "cop", "survival": "thief"}.get(result)
    winner = next((g for g, r in roles.items() if r == winner_role), "none")
    commits = summary.get("github_commit")
    commits = dict(commits) if isinstance(commits, Mapping) else \
        {ours: "unknown", theirs: "unknown"}
    number = int(summary["sub_game_number"])  # type: ignore[call-overload]
    return {
        "sub_game_number": number,
        "roles": roles,
        "started_at": summary["started_at"],
        "ended_at": summary["ended_at"],
        "result": result,
        "winner_group": winner,
        "tie": False,
        "github_commit": commits,
        "tokens": {ours: int(summary.get("tokens_total", 0)), theirs: 0},  # type: ignore[call-overload]
        "score": score,
        "log_files": dict.fromkeys((ours, theirs), f"log_{summary['game_id']}_g{number:02d}.json") if "game_id" in summary else
                     dict.fromkeys((ours, theirs), f"log_g{number:02d}.json"),
        # From the log, never a literal. This was
        # `{"log_verified": True, "tampered": False}` hardcoded until 2026-08-17, so every
        # report asserted a verification that had never run -- a false claim in a signed
        # artifact. `reporting.log_audit` now recomputes every commitment from its reveal
        # and the log carries the result; absent or malformed, we report NOT verified,
        # because the honest answer to "did the audit pass" when nothing checked is no.
        "audit": dict(audit) if isinstance(audit := summary.get("audit"), Mapping) and audit
                 else {"log_verified": False, "tampered": False, "steps_checked": 0},
        # Present because the opponent emits it and a grader compares the pair. Ours said
        # 29 where yanell11's said 28 on the same sub-games (2026-08-17); omitting the
        # field hid the disagreement rather than settling it.
        "steps": int(summary.get("steps", 0) or 0),
    }


def build_final_result(
    *,
    game_id: str,
    game_uid: str,
    groups: Sequence[str],
    rows: Sequence[Mapping[str, object]],
    repositories: Sequence[str],
    config_sha256: str,
    league: Mapping[str, object] | None = None,
    timezone: str = "UTC",
) -> JsonObject:
    """Assemble the template-shaped emailed report from per-sub-game rows."""
    if len(groups) != 2 or len(set(groups)) != 2:
        raise ResultTemplateError("exactly two distinct group ids are required")
    if not rows:
        raise ResultTemplateError("a report with no sub-games has nothing to score")
    if len(repositories) != 4:
        raise ResultTemplateError(f"rule 49 requires exactly 4 links, got {len(repositories)}")
    ordered = sorted(rows, key=lambda r: int(r["sub_game_number"]))  # type: ignore[arg-type,call-overload]
    numbers = [int(r["sub_game_number"]) for r in ordered]  # type: ignore[call-overload]
    if numbers != list(range(1, len(numbers) + 1)):
        raise ResultTemplateError(f"sub-games must be contiguous from 1, got {numbers}")
    total = {g: sum(int(r["score"][g]) for r in ordered) for g in groups}  # type: ignore[call-overload,index]
    won = {g: sum(1 for r in ordered if r["winner_group"] == g) for g in groups}
    ties = sum(1 for r in ordered if r.get("tie") is True)
    series_tie = total[groups[0]] == total[groups[1]]
    if series_tie:
        # Table 17 row 5 (Fixed): '[Draw Score] -- score for each side when the
        # cumulative score of all games against an opponent ends in a draw -- 2'.
        # Added to the cumulative, matching the opponent's live aggregate (47-47
        # for G004); a draw is a result, not a gap (C-045).
        total = {g: v + 2 for g, v in total.items()}
    winner = None if series_tie else max(groups, key=lambda g: total[g])
    league = dict(league or {})
    return {
        "_schema": "result-report",
        "schema_version": SCHEMA_VERSION,
        "report_type": "final_game_result",
        "game_id": game_id,
        "game_uid": game_uid,
        "links": {
            "declaration": f"declaration_{game_id}.json",
            "config": f"config_{game_id}_g<NN>.json",
            "log": f"log_{game_id}_g<NN>.json",
            "result": f"result_{game_id}.json",
        },
        "timezone": timezone,
        "groups": list(groups),
        "repositories": list(repositories),
        "num_sub_games": len(ordered),
        "sub_games": [dict(r) for r in ordered],
        "final_result": {
            "total_score": total,
            "sub_games_won": won,
            "ties": ties,
            "winner_group": winner,
            "series_tie": series_tie,
            "tokens_total_series": {
                g: sum(int(r["tokens"].get(g, 0)) for r in ordered) for g in groups},  # type: ignore[call-overload,union-attr]
            "games_played_including_this": league.get(
                "games_played_including_this", dict.fromkeys(groups, 1)),
            "first_meeting_between_groups": league.get("first_meeting_between_groups", True),
            "diversity_reward_applied": league.get(
                "diversity_reward_applied", dict.fromkeys(groups, False)),
        },
        "mutual_agreement": {"sha256": config_sha256, "confirmed": True},
        # Whether this series counts, stated rather than inferred. Absent until
        # 2026-08-17, so nothing in our artifact separated a rehearsal from a graded game
        # -- and we sent five friendly reports that a reader could only tell apart by the
        # recipient. yanell11's own report carries {"counted": false, "reason": "friendly"};
        # this is the same field, deliberately matching their spelling so the two files
        # read as one pair. Defaults to uncounted: a game claimed as counted when it was a
        # rehearsal is the more expensive mistake of the two.
        "league": {"counted": bool(league.get("counted", False)),
                   "reason": str(league.get("reason", "friendly"))},
    }
