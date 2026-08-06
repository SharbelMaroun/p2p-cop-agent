"""Stepping through a replay, with the verdict recomputed every time (`M8-08`, `M8-08a`).

`:1689`: the player "loads the final log file … and the viewer allows the user to navigate
forward and backward in time using playback controls". The reference ships the same
controls — `Play / Pause`, `Step >`, `Restart`, `Go to step`, and a sub-game selector.

**The verdict is a property, not a field.** `M8-08a` asks that verification be recomputed
on every navigation rather than cached from load time, and the cheapest way to guarantee
that is to leave nowhere to cache it: this class stores a cursor position and nothing else.
A stale verdict is unrepresentable rather than merely avoided.

That is not ceremony. The `Verified OK` banner is submission evidence (`:1769`, and the
README report "absolute mandatory" screenshot), and evidence that was computed once at
load and then painted forever is a claim about the past tense. If the document underneath
changes — a viewer that reloads, a file rewritten between steps, a test that forges a
record — the banner has to change with it, or it is decoration rather than proof.
`test_navigation.py` holds this by tampering with a loaded log *between* two navigations
and asserting the banner flips without a reload.

**Navigation cannot leave the log.** `go_to` clamps rather than raising: a viewer whose
`Next` button throws at the last step is a viewer that crashes during the demo it exists to
produce. Out-of-range is a no-op with the cursor still somewhere real.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_cop_agent.replay.load import ReplayLog
from p2p_cop_agent.replay.sequence import SequenceReport, inspect_sequence
from p2p_cop_agent.replay.verify import MatchVerdict, RecordCheck, Verdict, verify_records


class Replay:
    """A cursor over a loaded log. Holds a position; derives everything else."""

    def __init__(self, log: ReplayLog) -> None:
        self._log = log
        self._position = 0

    # --- state -------------------------------------------------------------------------

    @property
    def log(self) -> ReplayLog:
        return self._log

    @property
    def position(self) -> int:
        """Zero-based index of the step under the cursor."""
        return self._position

    @property
    def total(self) -> int:
        return len(self._log.records)

    @property
    def record(self) -> Mapping[str, object]:
        return self._log.records[self._position]

    # --- the derived verdict -----------------------------------------------------------

    @property
    def verdict(self) -> MatchVerdict:
        """Re-verify the whole log, now. Recomputed on every read by construction."""
        return verify_records(self._log.records)

    @property
    def sequence(self) -> SequenceReport:
        """Structural findings, reported beside the verdict and never folded into it."""
        return inspect_sequence(self._log.records)

    @property
    def check(self) -> RecordCheck:
        """The verdict for the step under the cursor, also recomputed on every read."""
        return self.verdict.checks[self._position]

    @property
    def banner(self) -> str:
        """What the viewer paints for the match as a whole — green stamp or red banner."""
        return self.verdict.banner

    @property
    def stamp(self) -> Verdict:
        return self.verdict.verdict

    # --- navigation --------------------------------------------------------------------

    def step_forward(self) -> int:
        """`Step >`. Stops at the last record rather than running off the end."""
        return self.go_to(self._position + 1)

    def step_back(self) -> int:
        """The half `:1689` asks for that a forward-only player would miss."""
        return self.go_to(self._position - 1)

    def go_to(self, position: int) -> int:
        """`Go to step` by index, clamped into the log."""
        self._position = max(0, min(position, self.total - 1))
        return self._position

    def go_to_step(self, step: object) -> int:
        """Jump by the record's own `step` value, which is what an auditor cites.

        Falls back to the index when no record carries that step, because a log whose
        numbering we do not recognise is exactly the log we still want to look at.
        """
        for index, record in enumerate(self._log.records):
            if isinstance(record, Mapping) and record.get("step") == step:
                return self.go_to(index)
        return self._position

    def restart(self) -> int:
        """`Restart`."""
        return self.go_to(0)

    def go_to_first_divergence(self) -> int | None:
        """Jump straight to the step that voided the match, if any.

        The one navigation an auditor actually performs: `:1769` gives a `TAMPERED` match
        "no appeal process", so the only remaining question is *which step*, and making
        someone click `Step >` through a hundred records to find it is how the answer gets
        recorded wrong.
        """
        bad = self.verdict.first_bad
        if bad is None:
            return None
        return self.go_to(bad.index)
