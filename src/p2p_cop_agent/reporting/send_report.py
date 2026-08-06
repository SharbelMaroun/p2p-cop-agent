"""Sending the report, and the three ways that can go wrong (`M7-17`, `M7-15c`).

`M7-17`'s condition is "no failure mode silently loses a report", and rule 32 (Mandatory)
explains the stakes: "Report game results automatically using the Gmail interface.
Sanction: **absence of reporting disqualifies the game points**." A send that fails
quietly costs the game as surely as never trying.

Three failures, three different answers:

**429 — throttled (`M7-17a`).** Retry with backoff. Appendix F table 19 makes the retry
delay a `Minimum` of 5 seconds and attempts a `Minimum` of 3, so those are floors to
honour rather than values to tune downward. Doubling from there is ours.

**Permanent failure (`M7-17b`).** Raise loudly. There is no useful fallback — the report
is Mandatory, and a caller that could `except` its way past this would convert a lost
game into a silent one. `:2584`: a side that does not report "will not be credited".

**Already sent (`M7-17c`).** Refuse. Rule 35: "each team sends a separate completion
report; a **conflicting** report causes disqualification of the game and a score of 0 for
**both teams**." Two sends for one game is the easiest way to produce a conflict by
accident, so the guard is keyed on `game_id` and is not resettable through the API.

**No credential (`M7-15c`).** Fail closed. A missing `token.json` must never degrade into
"skipped the report", because that failure looks identical to success in a log that only
records errors.

Nothing here imports a Google library: `transmit` is injected. The credential path is
checked for *presence*, never read or parsed here, so this module cannot leak one.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

# Appendix F table 19 `Minimum` values -- floors, not targets.
MIN_RETRY_BACKOFF_SECONDS = 5.0
MIN_RETRY_ATTEMPTS = 3
THROTTLED = 429


class ReportNotSentError(RuntimeError):
    """Raised when a Mandatory report did not go out. Deliberately hard to ignore."""


class ReportAlreadySentError(RuntimeError):
    """Raised on a second send for one game -- rule 35's conflict risk."""


@dataclass(frozen=True, slots=True)
class SendOutcome:
    """What happened, including how many attempts it took, for the evidence bundle."""

    game_id: str
    attempts: int
    response: object


@dataclass
class ReportSender:
    """Sends each game's report exactly once, backing off when told to."""

    credential_path: Path | None = None
    max_attempts: int = MIN_RETRY_ATTEMPTS
    backoff_seconds: float = MIN_RETRY_BACKOFF_SECONDS
    _sent: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self.max_attempts < MIN_RETRY_ATTEMPTS:
            raise ValueError(f"retry attempts is a MINIMUM of {MIN_RETRY_ATTEMPTS} [AF-t19]")
        if self.backoff_seconds < MIN_RETRY_BACKOFF_SECONDS:
            raise ValueError(f"retry delay is a MINIMUM of {MIN_RETRY_BACKOFF_SECONDS}s [AF-t19]")

    def already_sent(self, game_id: str) -> bool:
        return game_id in self._sent

    def require_credential(self) -> None:
        """`M7-15c`: no credential is a hard stop, never a skipped report."""
        if self.credential_path is None or not Path(self.credential_path).exists():
            raise ReportNotSentError(
                f"no Gmail credential at {self.credential_path!r}; refusing to skip a "
                "Mandatory report [AE-32]. Run the one-time consent flow first"
            )

    def send(
        self,
        *,
        game_id: str,
        transmit: Callable[[], object],
        sleep: Callable[[float], None],
        status_of: Callable[[BaseException], int | None],
    ) -> SendOutcome:
        """Transmit once, retrying only on a throttle, and never twice for one game.

        ``status_of`` maps a transport exception to an HTTP status, so this module stays
        free of any Google client type -- the retry decision is about 429, not about which
        library raised.
        """
        if self.already_sent(game_id):
            raise ReportAlreadySentError(
                f"{game_id} was already reported; a second report risks the rule 35 "
                "conflict verdict, which scores 0 for BOTH teams"
            )
        self.require_credential()
        last: BaseException | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = transmit()
            except BaseException as error:  # noqa: BLE001 -- re-raised below if not a 429
                last = error
                if status_of(error) != THROTTLED or attempt == self.max_attempts:
                    break
                sleep(self.backoff_seconds * (2 ** (attempt - 1)))
                continue
            self._sent.add(game_id)
            return SendOutcome(game_id, attempt, response)
        raise ReportNotSentError(
            f"{game_id} was NOT reported after {self.max_attempts} attempt(s); rule 32 "
            f"disqualifies the game's points when a report is absent. Last error: {last!r}"
        ) from last


def outcome_record(outcome: SendOutcome, sent_at: str) -> Mapping[str, object]:
    """A record of the send for the evidence bundle -- what was sent, when, after how many."""
    return {"game_id": outcome.game_id, "attempts": outcome.attempts, "sent_at": sent_at}
