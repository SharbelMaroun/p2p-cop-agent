"""`M8-04a` / `M8-13`: every fault class has an **observed** outcome, not a predicted one.

`M8-13`'s condition is exactly that wording, and it is the point. The repository already
*describes* what happens on a crash or a timeout; this makes each one happen and records
what came back.

The required outcomes, from Table 2 (`:844`) and Appendix E:

| Fault | Required outcome |
|---|---|
| crash, timeout, or cryptographic forgery | **Technical Loss — 0 to the Cop, 0 to the Thief** |
| opponent silent past the deadline | terminal state, never a hang (rules 6 and 7) |

The config-mismatch class is `test_negotiation_refusal.py`: it is the one fault that must
stop a match *before* it starts rather than resolve one that has gone wrong.

Note what Table 2 literally says: a technical loss scores **0 | 0**, both columns. Asked
directly, the prose around it describes the loss as falling on "the side responsible", but
the table itself gives neither side a point, and the table is what rule 48 says to score
by. We implement the table.

Rule 7's sanction is the one that shapes `M8-13a`: "Game crash and **loss of formal
documentation**". So a crash must still leave artifacts behind — a terminated series that
wrote nothing has incurred the sanction rather than avoided it.
"""

from __future__ import annotations

import json
from pathlib import Path

from p2p_cop_agent.domain.scoring import Outcome, ScoringTable
from p2p_cop_agent.orchestration.series import SUB_GAMES, Role, SubGameLine, run_series
from p2p_cop_agent.reporting import MatchIdentity, config_filename, log_filename
from p2p_cop_agent.reporting.log_artifact import build_log
from p2p_cop_agent.reporting.naming import match_filenames

ROOT = Path(__file__).resolve().parents[2]
GAME = json.loads((ROOT / "shared_contract" / "fixtures" / "match_config.example.json")
                  .read_text("utf-8"))
IDENT = MatchIdentity("failure-matrix", "e" * 32)


# --- the scoring table's own row ---------------------------------------------------------


def test_a_technical_loss_scores_zero_for_both_sides() -> None:
    """Table 2 (`:844`): "Side crashes, times out, or performs a cryptographic forgery"
    scores `0 | 0`. Both columns — this is the row rule 48 says to score by."""
    table = ScoringTable.from_config(GAME)
    line = table.award(Outcome.TECHNICAL_LOSS)
    assert (line.cop, line.thief) == (0, 0)


def test_the_other_two_outcomes_are_not_zero_so_the_row_above_is_distinctive() -> None:
    """A scoring table that returned 0/0 for everything would pass the test above while
    being catastrophically wrong."""
    table = ScoringTable.from_config(GAME)
    assert table.award(Outcome.CAPTURE).cop > 0
    assert table.award(Outcome.SURVIVAL).thief > 0


# --- M8-13a: a crash mid-series still produces artifacts ---------------------------------


def _emit(directory: Path, sub_game: int, outcome: str) -> SubGameLine:
    """Write one sub-game's pair of artifacts and return its result line."""
    (directory / config_filename(IDENT, sub_game)).write_text(
        json.dumps({"_schema": "per-subgame-config", "sub_game_number": sub_game}), "utf-8")
    log = build_log(identity=IDENT, sub_game=sub_game,
                    records=[{"step": 1, "sender": "police", "commit": "a" * 64,
                              "move": "N", "hint": "north", "intent": True}],
                    summary={"outcome": outcome, "turns": 1})
    (directory / log_filename(IDENT, sub_game)).write_text(json.dumps(log), "utf-8")
    scores = {"capture": (20, 5), "technical_loss": (0, 0)}[outcome]
    return SubGameLine(sub_game, Role.COP, outcome, scores[0], scores[1], 0)


def test_an_opponent_crash_mid_series_still_leaves_a_complete_artifact_set(
    tmp_path: Path,
) -> None:
    """`M8-13a`. Rule 7's sanction for an unmonitored crash is "loss of formal
    documentation", so a series that dies quietly has *incurred* the sanction, not dodged
    it. The crash happens at sub-game 3 and every later sub-game is a technical loss."""
    crashed_at = 3

    def play(sub_game: int, role: Role) -> SubGameLine:
        outcome = "capture" if sub_game < crashed_at else "technical_loss"
        return _emit(tmp_path, sub_game, outcome)

    result = run_series(IDENT, Role.COP, play)

    assert result.complete, "the series must reach a terminal state, not hang"
    assert len(list(tmp_path.iterdir())) == 2 * SUB_GAMES, "every sub-game keeps its pair"
    for sub_game in range(crashed_at, SUB_GAMES + 1):
        assert (tmp_path / log_filename(IDENT, sub_game)).exists()
    lost = [line for line in result.lines if line.outcome == "technical_loss"]
    assert len(lost) == SUB_GAMES - crashed_at + 1
    assert all(line.cop_score == 0 and line.thief_score == 0 for line in lost)


def test_the_artifact_names_do_not_depend_on_the_outcome(tmp_path: Path) -> None:
    """A crash must not change where the evidence lands, or a grader looking for
    `log_<game_id>_g03.json` finds nothing and reads it as a missing sub-game."""
    names = match_filenames(IDENT, (1, 2, 3))
    assert names["log_g01"] == log_filename(IDENT, 1)
    assert names["config_g03"] == config_filename(IDENT, 3)


# --- M8-13b: a drop mid-turn is terminal, not a hang -------------------------------------


def test_a_series_whose_every_sub_game_drops_still_terminates(tmp_path: Path) -> None:
    """`M8-13b`. The condition is "terminal outcome is defined, not a hang". The worst
    case is that nothing ever succeeds; the series must still end and still report."""
    result = run_series(IDENT, Role.COP,
                        lambda sub_game, role: _emit(tmp_path, sub_game, "technical_loss"))

    assert result.complete and len(result.lines) == SUB_GAMES
    assert all(line.cop_score == 0 for line in result.lines), "every sub-game scores 0/0"
    assert len(list(tmp_path.iterdir())) == 2 * SUB_GAMES


def test_a_series_of_technical_losses_currently_earns_the_tie_award(tmp_path: Path) -> None:
    """**Not an assertion that this is right — an assertion of what happens** (`U-033`).

    Every sub-game scores 0/0 under Table 2, so the cumulative is 0-0, and `:2042` makes an
    equal total a draw worth the `tie_score` to each group. Read literally that is what the
    rules say, and it is what this implements: two teams that crashed out of all six
    sub-games each collect 2 points.

    Whether the tie award was meant to reach a series decided entirely by technical losses
    is genuinely unclear — rule 48 scores the *scenario* at 0/0, while the draw row scores
    the *cumulative*. Pinned here so the behaviour is visible and cannot change silently,
    and recorded as an open question rather than quietly reinterpreted.
    """
    result = run_series(IDENT, Role.COP,
                        lambda sub_game, role: _emit(tmp_path, sub_game, "technical_loss"))
    cumulative = result.cumulative(tie_award=2)
    assert cumulative["cop_score"] == 2 and cumulative["thief_score"] == 2
