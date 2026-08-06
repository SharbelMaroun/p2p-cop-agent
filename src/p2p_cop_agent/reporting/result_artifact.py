"""The results report — the one artifact that is actually emailed (`M7-03b`).

`:2241` defines it: "A summary of the game results, including **the score of each group in
all games and the cumulative result**, for the lecturer to weigh the league score."

Three Mandatory rules land in this single file, which is why its checks are strict:

* **Rule 49** — "four links in the JSON files of the two teams". Two repositories per
  group, and exactly four; a fifth or a third means one side's submission is wrong.
* **Rule 53** — "record the commit hash… for every game, you must update the commit
  hash". Code may change between games, so a result that does not say *which* code
  played it cannot be reproduced.
* **Rule 54** — "report… the total number of tokens required for the game **and in the
  sequence**". Two numbers, not one: per sub-game and cumulative.

**And rule 35 is why `mutual_agreement` is not optional.** "Agree with the opponent on the
result, and each team sends a separate completion report; **a conflicting report causes
disqualification of the game and a score of 0 for both teams**." Each side sends its own
file, so two files exist and they must not contradict. Building this artifact without
recording whether the opponent agreed would make it trivially possible to send a report
that costs both teams the game — so an unagreed result is refused at build time rather
than discovered at grading.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from p2p_cop_agent.reporting.naming import MatchIdentity
from p2p_cop_agent.shared.config import JsonObject

SCHEMA_VERSION = "1.1"
REQUIRED_LINKS = 4
SUB_GAME_FIELDS = ("sub_game", "outcome", "cop_score", "thief_score", "tokens")


class ResultArtifactError(ValueError):
    """Raised when a report would be unsendable, unreproducible, or contradictory."""


def build_result(
    *,
    identity: MatchIdentity,
    groups: Sequence[Mapping[str, object]],
    sub_games: Sequence[Mapping[str, object]],
    commit_hash: str,
    mutual_agreement: bool,
    timezone: str = "UTC",
) -> JsonObject:
    """Assemble the emailed report, refusing anything that would be scored against us."""
    if not mutual_agreement:
        raise ResultArtifactError(
            "the opponent has not agreed this result; rule 35 scores a conflicting report "
            "0 for BOTH teams, so an unagreed result is not reportable"
        )
    if not sub_games:
        raise ResultArtifactError("a report with no sub-games has nothing to score")
    if not isinstance(commit_hash, str) or len(commit_hash) < 7:
        raise ResultArtifactError("commit_hash must identify the code that played [AE-53]")

    links = [url for group in groups for url in _repos(group)]
    if len(links) != REQUIRED_LINKS:
        raise ResultArtifactError(
            f"rule 49 requires exactly {REQUIRED_LINKS} repository links, got {len(links)}"
        )
    lines = [_line(index, entry) for index, entry in enumerate(sub_games)]
    return {
        "_schema": "result-report",
        "schema_version": SCHEMA_VERSION,
        "report_type": "final_result",
        "game_id": identity.game_id,
        "game_uid": identity.game_uid,
        "groups": [dict(group) for group in groups],
        "repositories": links,
        "commit_hash": commit_hash,
        "num_sub_games": len(lines),
        "sub_games": lines,
        "final_result": _cumulative(lines),
        "mutual_agreement": True,
        "timezone": timezone,
    }


def _repos(group: Mapping[str, object]) -> list[str]:
    repos = group.get("repos")
    if not isinstance(repos, Mapping):
        raise ResultArtifactError(f"group {group.get('group_id')!r} carries no repos mapping")
    return list(repos.values())


def _line(index: int, entry: Mapping[str, object]) -> JsonObject:
    missing = [name for name in SUB_GAME_FIELDS if name not in entry]
    if missing:
        raise ResultArtifactError(f"sub-game {index} is missing {', '.join(missing)}")
    return {name: entry[name] for name in SUB_GAME_FIELDS}


def _cumulative(lines: Sequence[Mapping[str, object]]) -> JsonObject:
    """Sum the series. `:2042`: an equal total is a tie, which is a result, not a gap."""
    cop = sum(int(line["cop_score"]) for line in lines)  # type: ignore[arg-type]
    thief = sum(int(line["thief_score"]) for line in lines)  # type: ignore[arg-type]
    return {
        "cop_score": cop,
        "thief_score": thief,
        # Rule 54's second number: the series total, alongside each sub-game's own.
        "tokens_total": sum(int(line["tokens"]) for line in lines),  # type: ignore[arg-type]
        "winner": "tie" if cop == thief else ("cop" if cop > thief else "thief"),
    }
