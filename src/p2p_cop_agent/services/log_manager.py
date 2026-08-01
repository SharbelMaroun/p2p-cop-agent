"""The append-only match log subsystem (M5-12).

This is the concrete subsystem behind the orchestrator's ``LogManager`` port. It must
be enough to reconstruct a match for the end-game audit `[AE-36]`, and it enforces
two disciplines rather than merely storing text:

* **Append-only** -- there is no method that edits or deletes a past event, and
  ``events`` hands back a copy, so history cannot be rewritten after the fact.
* **Nonce secrecy** -- a commitment's hash is recorded live, but the nonce that opens
  it is refused until ``open_reveal`` marks the post-game reveal `[AE-18]`. A log
  captured mid-match therefore cannot leak the seal.

Each match writes to its own ``logs/<match_id>.jsonl`` path, so two matches never
overwrite each other, and the id is validated as a safe file stem before it is used.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from p2p_cop_agent.shared.config import JsonObject

_UNSAFE = ("/", "\\")


class LogError(RuntimeError):
    """Raised when the append-only or nonce-secrecy discipline would be broken."""


@dataclass
class MatchLog:
    """A structured, append-only record of one match."""

    match_id: str
    path: Path | None = None
    _events: list[JsonObject] = field(default_factory=list)
    _revealed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.match_id, str) or not self.match_id.strip():
            raise LogError("match_id must be a non-empty string")
        if self.match_id in (".", "..") or any(mark in self.match_id for mark in _UNSAFE):
            raise LogError(f"match_id {self.match_id!r} is not a safe file stem")

    @classmethod
    def for_match(cls, match_id: str, logs_dir: str | Path) -> MatchLog:
        """Open the log for one match under its own path; other matches are untouched."""
        log = cls(match_id=match_id)
        directory = Path(logs_dir)
        directory.mkdir(parents=True, exist_ok=True)
        log.path = directory / f"{match_id}.jsonl"
        return log

    def record(self, event: str, detail: Mapping[str, object] | None = None) -> None:
        """Append one structured event, refusing a nonce before the reveal is open."""
        payload = dict(detail or {})
        if not self._revealed and _mentions_nonce(payload):
            raise LogError(f"a nonce cannot be logged before the reveal (event {event!r})")
        entry: JsonObject = {"event": event, **payload}
        self._events.append(entry)
        self._append_line(entry)

    def open_reveal(self) -> None:
        """Mark the post-game reveal, after which nonces may be recorded `[AE-18]`."""
        self._revealed = True
        self.record("reveal_opened")

    @property
    def events(self) -> tuple[JsonObject, ...]:
        """Return every event in order, as a copy history cannot be rewritten through."""
        return tuple(self._events)

    def _append_line(self, entry: JsonObject) -> None:
        """Append one JSON line to the per-match file, if a path was opened."""
        if self.path is None:
            return
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")


def _mentions_nonce(detail: Mapping[str, object]) -> bool:
    """Return whether any member name looks like it carries a commitment nonce."""
    return any("nonce" in str(key).lower() for key in detail)
