"""The replay verdict: `Verified OK`, or `TAMPERED` and the match is void (`M8-02`).

Appendix E rule 20 is Mandatory — "build a match log reconstruction and replay app for
observation and verification", sanction "**threshold condition** for confirmation of logs
and submission of the project" (p.129/272). Asked directly, the sources confirm that
reading: the project cannot be accepted without this. It is the one deliverable whose
absence is not a lost mark but a rejected submission.

**Exactly two verdicts, and the second one is fatal.** `:1693`: "If the values match, a
green `Verified OK` stamp is displayed. If even the slightest change in the historical
data is detected … the viewer displays a bright red `TAMPERED` banner, and the replay is
immediately invalidated." `:1769` removes the escape hatch — "There is no appeal process
and no room for manual correction". So `Verdict` has two members and no third; a
`SUSPICIOUS` or `PARTIAL` state would be a state the rules do not have.

**One bad step voids the whole match (`M8-02c`).** The book's own `replay` walks every
entry and returns `TAMPERED` on the first failure (`:1743`, and `:1753` — "If any single
step returns `TAMPERED`, the entire match is invalidated"). We keep walking anyway, so the
report can say *where*, but the match verdict is decided by the first divergence.

**Why we do not use the book's chapter-7 formula (`M8-02d`).** `:1733` computes
`sha256(f"{nonce}|{move}")` — nonce first, and only the bare move. Our commitment is
`sha256(canonical_payload_bytes(payload) + b"|" + nonce)`. Those never agree.

This is **not** a contradiction to disclose, which is what `M8-02d` originally assumed.
`:1757` says so in the book's own voice: "the sketch simplified the input for the sake of
the illustration; in practice the signature covers all components of the step — Intent,
Move, State and Nonce — as detailed in the protocol in Chapter 5". The chapter-7 listing
is a teaching simplification that names chapter 5 as normative. Filing it as a conflict
would have recorded a disagreement the sources do not have.

The reference simulator diverges the same way and for the same reason: its `verify_record`
(`src/police_thief/gui/replay_data.py`) recomputes the digest over the revealed *payload*
with the nonce, not over a bare move string.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum

from p2p_cop_agent.protocol.commit import verify_commit

REVEAL_FIELDS = ("commit", "payload", "nonce")


class Verdict(str, Enum):
    """The only two outcomes the rules define. `:1707` labels the second "disqualify"."""

    VERIFIED_OK = "Verified OK"
    TAMPERED = "TAMPERED"


@dataclass(frozen=True)
class RecordCheck:
    """One step's outcome, with the reason kept for the banner and the audit trail."""

    index: int
    step: object
    verdict: Verdict
    reason: str

    @property
    def ok(self) -> bool:
        return self.verdict is Verdict.VERIFIED_OK


@dataclass(frozen=True)
class MatchVerdict:
    """The match-level result. `first_bad` is the step the book stops the replay at."""

    verdict: Verdict
    checks: tuple[RecordCheck, ...]
    first_bad: RecordCheck | None

    @property
    def ok(self) -> bool:
        return self.verdict is Verdict.VERIFIED_OK

    @property
    def banner(self) -> str:
        """The line a viewer paints, green or red."""
        if self.ok:
            return f"{Verdict.VERIFIED_OK.value} — {len(self.checks)} steps re-verified"
        bad = self.first_bad
        assert bad is not None  # a TAMPERED verdict always names its step
        return f"{Verdict.TAMPERED.value} — step {bad.step!r}: {bad.reason}"


def verify_record(record: Mapping[str, object], index: int = 0) -> RecordCheck:
    """Recompute one record's commitment from the file's own bytes.

    A record that *cannot* be checked is `TAMPERED`, not an exception: a missing nonce in
    a revealed log is a nonce someone removed, and the reference collapses its `CryptoError`
    to the same red banner. Refusing to reach a verdict here would let a forger escape by
    damaging a record rather than rewriting it.

    (Refusing an *entire* log that was never revealed is a different matter and belongs to
    `load`, which distinguishes a peer who has not yet revealed from one who has forged.)
    """
    step = record.get("step") if isinstance(record, Mapping) else None
    if not isinstance(record, Mapping):
        return RecordCheck(index, step, Verdict.TAMPERED, "record is not an object")
    missing = [name for name in REVEAL_FIELDS if name not in record]
    if missing:
        return RecordCheck(
            index, step, Verdict.TAMPERED, f"record carries no {', '.join(missing)}"
        )
    if not verify_commit(record["payload"], record["nonce"], record["commit"]):
        return RecordCheck(
            index, step, Verdict.TAMPERED, "recomputed digest does not match the commitment"
        )
    disagreeing = _visible_fields_contradicting_the_seal(record)
    if disagreeing:
        return RecordCheck(
            index, step, Verdict.TAMPERED,
            f"visible {', '.join(disagreeing)} contradicts the sealed payload",
        )
    return RecordCheck(index, step, Verdict.VERIFIED_OK, "reveal matches commit")


def _visible_fields_contradicting_the_seal(record: Mapping[str, object]) -> list[str]:
    """Which displayed fields disagree with the payload the commitment actually covers.

    **Found by `M8-12b`'s appended-step test, which a digest check alone let through.** The
    commitment binds the *payload*; it says nothing about the record's own `step` and
    `move` keys, which are what a viewer paints on the board. So a forger can leave the
    sealed payload untouched — every digest still matches, green stamp — and rewrite only
    the visible move. The replay would then be a picture of a game nobody played, stamped
    `Verified OK`.

    `:1691` closes it: the viewer takes "the Nonce and the move **appearing in the log**"
    and re-encodes *them*. The move appearing in the log has to be the move that was
    sealed, or the re-encoding is of something the record does not claim.

    Compared by intersection rather than a fixed field list, so a payload that later seals
    a position or a verdict is covered without anyone remembering to add it here.
    """
    payload = record.get("payload")
    if not isinstance(payload, Mapping):
        return []
    return sorted(
        name
        for name, sealed in payload.items()
        if name in record and name not in REVEAL_FIELDS and record[name] != sealed
    )


def verify_records(records: Sequence[Mapping[str, object]]) -> MatchVerdict:
    """Verify every record and return the match verdict — void on the first divergence.

    Every record is checked even after a failure, because "which step was altered" is what
    an auditor asks next and re-running to find out would mean trusting the same code twice.
    The *verdict* still follows `:1753`: one bad step invalidates the entire match.
    """
    if not records:
        return MatchVerdict(
            Verdict.TAMPERED,
            (),
            RecordCheck(0, None, Verdict.TAMPERED, "log has no records to verify"),
        )
    checks = tuple(verify_record(record, index) for index, record in enumerate(records))
    first_bad = next((check for check in checks if not check.ok), None)
    verdict = Verdict.VERIFIED_OK if first_bad is None else Verdict.TAMPERED
    return MatchVerdict(verdict, checks, first_bad)
