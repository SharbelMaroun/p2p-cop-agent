"""`X-08`: the reveal is refused while the game is still in play.

Split from `test_log_artifact.py`, which covers building and revealing. This covers **when**
revealing is allowed, and the placement is the whole finding.

The row arrived from the companion repository, where one builder produces the finished
artifact and therefore needs an end-of-game check. Here the two are split: `build_log`
already refuses any record carrying a nonce, so the in-play artifact *cannot* hold a reveal
— a stronger guarantee than the Thief's. Transplanting the guard as written would have added
a redundant check to `build_log` and left the actual exposure, `reveal_log`, wide open.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.reporting.log_artifact import (
    LogArtifactError,
    build_log,
    is_revealed,
    reveal_log,
)
from tests.unit.test_log_artifact import IDENT, REVEALS, STEPS, SUMMARY


def test_revealing_a_log_for_a_game_still_in_play_is_refused() -> None:
    """`X-08`. Rule 18 keeps nonces secret until the end of the game, and Step 4 is the
    Final Reveal — so calling `reveal_log` mid-game produces exactly the artifact the rule
    forbids.

    **The guard sits on `reveal_log`, not `build_log`, and the placement is the finding.**
    The row was written from the companion repository's design, where one builder produces
    the finished artifact and therefore needs an end-of-game check. Here `build_log` already
    refuses any record carrying a nonce, so the in-play artifact *cannot* hold a reveal —
    a stronger guarantee. The exposure was one function further along, and transplanting the
    guard as written would have added a redundant check while leaving the real gap open.
    """
    in_play = build_log(identity=IDENT, sub_game=1, records=STEPS,
                        summary={k: v for k, v in SUMMARY.items() if k != "ended_at"})
    with pytest.raises(LogArtifactError, match="AE-18"):
        reveal_log(in_play, REVEALS)


def test_a_finished_log_still_reveals() -> None:
    """The guard refuses a moment, not the operation. An `ended_at` is all it asks for."""
    assert is_revealed(reveal_log(build_log(identity=IDENT, sub_game=1, records=STEPS,
                                            summary=SUMMARY), REVEALS))
