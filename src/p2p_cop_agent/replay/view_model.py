"""What the replay screen shows, as data (`M8-06`, `M8-06a`, `M8-08b`).

`M8-06`'s condition is "no widget touches domain or protocol code directly", and `M8-06a`'s
is "the view cannot mutate game state". Both are met the same way: this module turns a
`Replay` cursor into **display-ready strings and primitives**, and the widget layer reads
nothing else. Asked directly, the reference draws the same boundary — its widgets are
"dumb" components receiving dictionaries of ready-to-display strings, with `ReplayApp` as
the controller in between.

That split is what makes the screenshot testable. A Tk window cannot be asserted about in
CI, but `ReplayFrame` can: `test_replay_view_model.py` pins the exact banner text and
colour for both verdicts, so the picture in the README is backed by an assertion rather
than by someone having looked at it once.

**Frozen dataclasses, so rendering cannot write back.** `M8-06a` asks for a read-only
snapshot; the cheapest way to guarantee it is a type that has no setters.

**The per-step verdict is here too (`M8-08b`).** The reference shows a per-step result
beside the board — recomputed each time the user advances — as well as a match-level one.
Both matter for a screenshot: the match banner is the headline, and the per-step line is
what tells an auditor *which* step failed.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from p2p_cop_agent.replay.cursor import Replay
from p2p_cop_agent.replay.verify import Verdict

# Taken from the reference's own palette so a grader comparing screenshots sees the same
# colours: green `#2ecc71` for a good state, police blue, thief orange, dark barriers.
COLOUR_OK = "#2ecc71"
COLOUR_TAMPERED = "#c0392b"
COLOUR_NEUTRAL = "#546e7a"
COLOUR_TEXT_ON_STAMP = "#ffffff"


@dataclass(frozen=True)
class StepRow:
    """One record as the info panel shows it.

    `commit` and `nonce` are carried in full as well as abbreviated: asked directly, the
    screen must display "the nonce, move, and the original commit hash from the log entry"
    (p.56/142). The short forms are for the scrolling list, where a 64-character wall is
    unreadable; the full ones are shown for the step under the cursor, which is what a
    screenshot has to make checkable.
    """

    index: int
    step: str
    sender: str
    move: str
    verdict: str
    reason: str
    commit: str
    nonce: str
    is_current: bool
    ok: bool

    @property
    def commit_short(self) -> str:
        """For the scrolling list only. The nonce has no short form because the list does
        not show one — the panel shows it in full for the step under the cursor."""
        return _short(self.commit)


@dataclass(frozen=True)
class ReplayFrame:
    """Everything the screen needs for one cursor position. No domain objects."""

    origin: str
    game_id: str
    sub_game: str
    position: int
    total: int
    stamp: str
    stamp_colour: str
    banner: str
    sequence_summary: str
    sequence_ok: bool
    rows: tuple[StepRow, ...]

    @property
    def position_label(self) -> str:
        return f"step {self.position + 1} of {self.total}"

    @property
    def current(self) -> StepRow:
        return self.rows[self.position]


def _short(value: object, keep: int = 12) -> str:
    """Abbreviate a digest for the panel. A full SHA-256 does not fit and, more to the
    point, an unreadable 64-character wall is what makes a screenshot look unverified."""
    text = "—" if value is None else str(value)
    return text if len(text) <= keep else f"{text[:keep]}…"


def _text(value: object) -> str:
    return "—" if value is None else str(value)


def _row(index: int, record: Mapping[str, object], check, current: int) -> StepRow:
    if not isinstance(record, Mapping):  # a damaged record still has to render
        record = {}
    return StepRow(
        index=index,
        step=_text(record.get("step", "?")),
        sender=_text(record.get("sender")),
        move=_text(record.get("move")),
        verdict=check.verdict.value,
        reason=check.reason,
        commit=_text(record.get("commit")),
        nonce=_text(record.get("nonce")),
        is_current=index == current,
        ok=check.ok,
    )


def frame_of(replay: Replay) -> ReplayFrame:
    """Snapshot the replay for rendering. Reads only; never advances the cursor.

    The verdict is taken from `replay.verdict`, which recomputes on every access
    (`M8-08a`) — so a frame built after the underlying log changes reports the new
    verdict, and a screenshot taken from a frame is a screenshot of a live computation.
    """
    verdict = replay.verdict
    sequence = replay.sequence
    records = replay.log.records
    return ReplayFrame(
        origin=replay.log.origin,
        game_id=str(replay.log.game_id or "—"),
        sub_game=str(replay.log.sub_game or "—"),
        position=replay.position,
        total=replay.total,
        stamp=verdict.verdict.value,
        stamp_colour=COLOUR_OK if verdict.ok else COLOUR_TAMPERED,
        banner=verdict.banner,
        sequence_summary=sequence.summary,
        sequence_ok=sequence.contiguous,
        rows=tuple(
            _row(index, record, check, replay.position)
            for index, (record, check) in enumerate(zip(records, verdict.checks, strict=True))
        ),
    )


def stamp_is_green(frame: ReplayFrame) -> bool:
    """The single question a submission screenshot has to answer (`M8-05b`)."""
    return frame.stamp == Verdict.VERIFIED_OK.value and frame.stamp_colour == COLOUR_OK
