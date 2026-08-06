"""`M7-07`: one whole series through the stack — schedule, artifacts, settlement, result.

The first row that exercises everything together rather than in isolation. It is also the
reason to do this before mirroring M7 to the Thief: a design worth copying should be one
that has actually run.

`test_series.py` carries the schedule and the cumulative scoring.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from p2p_cop_agent.orchestration.series import (
    SUB_GAMES,
    Role,
    SeriesError,
    SubGameLine,
    artifact_names,
    run_series,
    schedule,
)
from p2p_cop_agent.orchestration.settlement import Settled, Settlement
from p2p_cop_agent.reporting import (
    build_config,
    build_result,
    validated_write,
)
from p2p_cop_agent.reporting.validate import check_one_identity
from tests.unit.test_series import GAME, IDENT, _lines


def test_a_series_produces_two_per_series_and_two_per_sub_game_files() -> None:
    names = artifact_names(IDENT)
    assert len(names) == 2 + 2 * SUB_GAMES
    assert "declaration_series-1.json" in names and "result_series-1.json" in names
    assert "config_series-1_g06.json" in names and "log_series-1_g01.json" in names


def test_run_series_plays_all_six_on_the_schedule() -> None:
    seen: list[tuple[int, Role]] = []

    def play(sub_game: int, role: Role) -> SubGameLine:
        seen.append((sub_game, role))
        return SubGameLine(sub_game, role, "capture", 20, 5, 10)

    result = run_series(IDENT, Role.COP, play)
    assert seen == list(schedule(Role.COP)) and result.complete


def test_a_sub_game_returning_the_wrong_line_is_refused() -> None:
    """A line that does not match the sub-game it was asked for would silently corrupt the
    result artifact, which is the one thing the lecturer reads."""
    with pytest.raises(SeriesError, match="returned a line for"):
        run_series(IDENT, Role.COP, lambda n, r: SubGameLine(1, r, "capture", 20, 5, 10))


def test_a_whole_series_emits_a_consistent_artifact_set(tmp_path: Path) -> None:
    """`M7-07` end to end: schedule → per-sub-game configs → settlement → result, with the
    identity check that no per-file schema could make (`M7-14e`)."""
    configs = []
    for sub_game, _role in schedule(Role.COP):
        artifact = build_config(identity=IDENT, sub_game=sub_game, game=GAME,
                                config_sha256="a" * 64)
        validated_write(tmp_path, f"config_series-1_g{sub_game:02d}.json", artifact)
        configs.append(artifact)

    check_one_identity(configs)
    assert len(list(tmp_path.iterdir())) == SUB_GAMES

    result = build_result(
        identity=IDENT,
        groups=[{"group_id": "alpha", "repos": {"c": "https://x/1", "t": "https://x/2"}},
                {"group_id": "beta", "repos": {"c": "https://x/3", "t": "https://x/4"}}],
        sub_games=[line.as_result_line()
                   for line in _lines([(20, 5)] * SUB_GAMES).lines],
        commit_hash="abc1234",
        mutual_agreement=Settlement(Settled.AGREED, "capture", "capture"),
    )
    assert result["num_sub_games"] == SUB_GAMES
    assert result["game_uid"] == IDENT.game_uid
    check_one_identity([*configs, result])
