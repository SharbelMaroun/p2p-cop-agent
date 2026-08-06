"""Loading a log for replay — including one we did not write (`M8-12`).

**The foreign log is the requirement, not a bonus.** Rule 36 mandates a "comprehensive
mutual log audit" at the end of every match as a necessary condition for agreement
(p.131/276), and p.39/102 says what that means in practice: "each side presents its full
log … each side reconstructs the opponent's data through the revealed nonces". A verifier
that only ever reads its own output proves nothing — it would confirm that our writer and
our reader agree, which they always will. The reference simulator makes the same move: its
replay app auto-locates `logs/<opponent_group_id>/log_<game_id>_gNN.json` to put both
sides on one board.

So `load_log` takes **a path and nothing else**. It never consults our identity, our
`game_id`, our key material, or our output directory. `test_foreign_log_replay.py` holds
that line two ways: by verifying a log built by a stranger's code path, and by parsing this
package's own imports so a future dependency on our identity fails the suite rather than
passing it quietly.

**Tolerant about shape, strict about the reveal.** An opponent's log may carry a different
`schema_version`, extra keys, or sections we do not emit; refusing it on those grounds
would fail rule 36 over a cosmetic difference and hand a real forger the excuse that our
viewer "could not open" the evidence. What we require is only what verification consumes:
a `records` array whose entries carry `commit`, `payload` and `nonce`.

**Not-yet-revealed is not forged.** A log written mid-game has no nonces at all — rule 18
requires exactly that — and calling it `TAMPERED` would accuse an honest peer of the one
thing that carries "no appeal process" (`:1769`). That is a load-time refusal with its own
error, not a verdict. A peer who *never* reveals is a settlement problem
(`Settled.UNANSWERED`), not a replay problem: the viewer judges forgery, settlement judges
refusal.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path


class LogNotReplayableError(ValueError):
    """The file cannot be replayed at all — distinct from replaying to a `TAMPERED`."""


@dataclass(frozen=True)
class ReplayLog:
    """A loaded log plus where it came from. `origin` is shown so a viewer screenshot
    makes clear *whose* log produced the banner — the point of a mutual audit."""

    origin: str
    document: Mapping[str, object]

    @property
    def records(self) -> Sequence[Mapping[str, object]]:
        records = self.document.get("records")
        return records if isinstance(records, Sequence) else ()  # type: ignore[return-value]

    @property
    def game_id(self) -> object:
        return self.document.get("game_id")

    @property
    def sub_game(self) -> object:
        """The template's key name, with the older one accepted for a foreign log."""
        document = self.document
        return document.get("sub_game_number", document.get("sub_game"))


def parse_log(document: object, origin: str = "<memory>") -> ReplayLog:
    """Accept a parsed document as a replayable log, or say precisely why it is not."""
    if not isinstance(document, Mapping):
        raise LogNotReplayableError(f"{origin}: top level is not a JSON object")
    records = document.get("records")
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)) or not records:
        raise LogNotReplayableError(f"{origin}: no `records` array to replay")
    unrevealed = [
        index
        for index, record in enumerate(records)
        if not isinstance(record, Mapping) or "nonce" not in record
    ]
    # All of them missing means the game has not ended yet -- honest, and rule 18 requires
    # it. *Some* of them missing is a log that was revealed and then interfered with, so
    # that one goes through to the verifier and comes back `TAMPERED`.
    if len(unrevealed) == len(records):
        raise LogNotReplayableError(
            f"{origin}: no record has been revealed; this is an in-play log, not a final "
            "one [AE-18]. A peer who never reveals is a settlement matter, not a forgery."
        )
    return ReplayLog(origin, document)


def load_log(path: str | Path) -> ReplayLog:
    """Read a log from disk for replay. Any readable path — ours or an opponent's."""
    location = Path(path)
    try:
        text = location.read_text("utf-8")
    except OSError as error:  # a missing opponent log is a normal, reportable state
        raise LogNotReplayableError(f"{location}: cannot be read ({error.strerror})") from error
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        raise LogNotReplayableError(f"{location}: is not valid JSON ({error.msg})") from error
    return parse_log(document, origin=str(location))
