"""LLM tokens per game and per series (`M7-11`, rule 54).

Rule 54 wants both figures and they answer different questions. The series total is what the
league compares; the per-game count is what shows the agreed `max_tokens_per_game` was
respected in the game where it mattered. A ledger holding only the total cannot answer the
second after the fact, and one holding only per-game figures makes the total somebody's
arithmetic.

Three decisions worth naming, because each prevents a number that looks fine:

**The ledger never resets between sub-games.** A per-game counter zeroed at each start is the
obvious implementation, and the reset sits exactly where a crash or a role swap interrupts.
Here each sub-game is a separate entry and the total is derived, so there is nothing to
forget to carry.

**A repeated sub-game is refused, not summed.** Replaying after a disconnection is real, and
adding the second attempt to the first inflates a figure rule 54 requires to be accurate. The
caller says which it means.

**An over-run is reported, never clamped.** The limit is agreed with the opponent in the
declaration; a ledger that quietly caps its own number reports a compliant figure for a game
that was not, which is the contradiction rule 35 scores 0 for both teams.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass


class TokenLedgerError(ValueError):
    """Raised when token accounting would produce an indefensible figure."""


@dataclass(frozen=True, slots=True)
class TokenUsage:
    """One sub-game's usage, split so an over-run can be attributed."""

    prompt: int
    completion: int

    def __post_init__(self) -> None:
        if self.prompt < 0 or self.completion < 0:
            raise TokenLedgerError(
                f"token counts cannot be negative, got {self.prompt}/{self.completion}")

    @property
    def total(self) -> int:
        return self.prompt + self.completion


class TokenLedger:
    """Per-sub-game usage across one series."""

    __slots__ = ("_entries", "max_tokens_per_game")

    def __init__(self, max_tokens_per_game: int) -> None:
        if max_tokens_per_game <= 0:
            raise TokenLedgerError(
                f"the agreed per-game limit must be positive, got {max_tokens_per_game}")
        self.max_tokens_per_game = max_tokens_per_game
        self._entries: dict[int, TokenUsage] = {}

    def record(self, sub_game: int, usage: TokenUsage) -> None:
        if sub_game in self._entries:
            raise TokenLedgerError(
                f"sub-game {sub_game} already has an entry; summing a retry into the first "
                "attempt inflates a figure rule 54 requires to be accurate — use `amend` if "
                "the game was genuinely replayed [AE-54]")
        self._entries[sub_game] = usage

    def amend(self, sub_game: int, usage: TokenUsage) -> None:
        """Replace an entry, for a sub-game that was genuinely replayed."""
        if sub_game not in self._entries:
            raise TokenLedgerError(f"sub-game {sub_game} has no entry to amend")
        self._entries[sub_game] = usage

    def __iter__(self) -> Iterator[tuple[int, TokenUsage]]:
        return iter(sorted(self._entries.items()))

    def tokens_for(self, sub_game: int) -> int:
        if sub_game not in self._entries:
            raise TokenLedgerError(f"sub-game {sub_game} has no recorded usage")
        return self._entries[sub_game].total

    @property
    def tokens_total_series(self) -> int:
        """Derived, never carried — there is no stored total to drift from the entries."""
        return sum(usage.total for usage in self._entries.values())

    def over_limit(self) -> tuple[int, ...]:
        """Which sub-games exceeded the agreed limit. Every one, not the earliest."""
        return tuple(n for n, usage in sorted(self._entries.items())
                     if usage.total > self.max_tokens_per_game)

    def report(self) -> dict[str, object]:
        """The two figures rule 54 requires, with the evidence behind each."""
        if not self._entries:
            raise TokenLedgerError(
                "a series with no recorded usage has nothing to report; rule 54 requires the "
                "count per game and per series [AE-54]")
        return {
            "max_tokens_per_game": self.max_tokens_per_game,
            "per_sub_game": {n: u.total for n, u in sorted(self._entries.items())},
            "tokens_total_series": self.tokens_total_series,
            "sub_games_over_limit": list(self.over_limit()),
        }


def usage_from_response(response: Mapping[str, object]) -> TokenUsage:
    """Read usage from a provider response, refusing one that carries none.

    Refused rather than defaulted to zero. **A provider that stopped returning usage looks
    exactly like a game that used no tokens**, and the second is a figure we would report to
    the league as fact.
    """
    usage = response.get("usage")
    if not isinstance(usage, Mapping):
        raise TokenLedgerError(
            "provider response carries no usage block; a missing count and a zero count are "
            "different claims and only one of them is reportable [AE-54]")
    prompt = usage.get("prompt_tokens", usage.get("input_tokens"))
    completion = usage.get("completion_tokens", usage.get("output_tokens"))
    if not isinstance(prompt, int) or not isinstance(completion, int):
        raise TokenLedgerError(f"usage block has no integer token counts: {dict(usage)}")
    return TokenUsage(prompt=prompt, completion=completion)
