"""`M7-20` companion: the properties a rehearsal is uniquely placed to check.

Identity consistency and schedule adherence are both true by construction in the unit
tests. Here they are checked across a **real six-sub-game run** that wrote real files,
which is the only place a wiring mistake between the pieces would show.

`test_series_rehearsal.py` carries the clean run and the two failure rehearsals.
"""

from __future__ import annotations

import json
from pathlib import Path

from p2p_cop_agent.orchestration.series import Role, SubGameLine, run_series, schedule
from p2p_cop_agent.reporting.validate import check_one_identity
from tests.integration.test_series_rehearsal import IDENT, SUB_GAMES, _play_sub_game


def test_every_artifact_in_the_rehearsal_shares_one_identity(tmp_path: Path) -> None:
    """`M7-14e` across a real run rather than a constructed pair."""
    def play(sub_game: int, role: Role) -> SubGameLine:
        return _play_sub_game(tmp_path, sub_game, outcome="capture")[0]

    run_series(IDENT, Role.COP, play)
    written = [json.loads(p.read_text("utf-8")) for p in sorted(tmp_path.iterdir())]
    check_one_identity(written)
    assert len(written) == 2 * SUB_GAMES


def test_the_schedule_drives_the_rehearsal(tmp_path: Path) -> None:
    """The rehearsal must exercise the ruled role order, not six identical sub-games."""
    seen: list[tuple[int, Role]] = []

    def play(sub_game: int, role: Role) -> SubGameLine:
        seen.append((sub_game, role))
        return _play_sub_game(tmp_path, sub_game, outcome="capture")[0]

    run_series(IDENT, Role.COP, play)
    assert seen == list(schedule(Role.COP))
