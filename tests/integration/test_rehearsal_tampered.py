"""`M7-20b`: a tampered audit — detection, and the report we must then NOT send.

Two behaviours, both required and easy to conflate. Rule 19 scores 0 for **the falsifying
group**, so catching the forgery is *their* loss. Rule 35 scores 0 for **both teams** if we
then file a contradicting report of our own. Detecting and declining to report are separate
things; a rehearsal that only proved detection would leave the expensive half untested.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from p2p_cop_agent.orchestration.series import Role, SubGameLine, run_series
from p2p_cop_agent.orchestration.settlement import (
    Settled,
    SettlementError,
    agree,
    audit_series,
    require_reportable,
    settlement_record,
)
from tests.integration.test_series_rehearsal import IDENT, SUB_GAMES, _play_sub_game


def test_a_tampered_audit_is_detected_and_stops_the_report(tmp_path: Path) -> None:
    """`M7-20b`. Two behaviours, both required: the forgery is caught, **and** we do not
    then file our own contradicting report. Rule 19 costs *them* the sub-game; rule 35
    would cost us both the game if we reported over the top of it."""
    reveals = []

    def play(sub_game: int, role: Role) -> SubGameLine:
        line, reveal = _play_sub_game(tmp_path, sub_game, outcome="capture",
                                      tamper=(sub_game == 4))
        reveals.append(reveal)
        return line

    run_series(IDENT, Role.COP, play)

    audit = audit_series(reveals)
    assert not audit.passed and audit.failed_at == 4

    settled = agree(audit, "capture", "survival")
    assert settled.state is Settled.AUDIT_FAILED
    with pytest.raises(SettlementError, match="shared one"):
        require_reportable(settled)

    # The evidence survives: the artifacts are still on disk for the lecturer to inspect.
    assert len(list(tmp_path.iterdir())) == 2 * SUB_GAMES
    assert settlement_record(settled)["audit_failed_at"] == 4
