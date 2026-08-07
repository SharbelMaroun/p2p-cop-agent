"""`M7-11`: token counts per game and per series, both defensible (rule 54).

Rule 54 wants both figures and they answer different questions. The series total is what the
league compares; the per-game count is what shows the agreed limit was respected in the game
where it mattered.

The tests target the three ways this number goes quietly wrong rather than addition: a
per-game counter reset where a crash interrupts, a retried sub-game summed into its first
attempt, and a missing provider usage block read as zero. Each produces a figure that looks
fine, which is what makes them worse than a refusal — rule 35 scores a report that
contradicts the opponent's 0 for **both** teams.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.reporting.token_ledger import (
    TokenLedger,
    TokenLedgerError,
    TokenUsage,
)


def ledger(limit: int = 200_000) -> TokenLedger:
    return TokenLedger(max_tokens_per_game=limit)


def usage(total: int) -> TokenUsage:
    return TokenUsage(prompt=total // 2, completion=total - total // 2)


def test_both_rule_54_figures_are_available() -> None:
    book = ledger()
    book.record(1, usage(1000))
    book.record(2, usage(2000))
    assert book.tokens_for(1) == 1000
    assert book.tokens_total_series == 3000


def test_the_series_total_is_derived_rather_than_carried() -> None:
    """Nothing to forget to carry. A stored total can drift from the entries that justify
    it, and rule 35 punishes exactly that contradiction."""
    book = ledger()
    for number in range(1, 7):
        book.record(number, usage(100))
    assert book.tokens_total_series == 600
    book.amend(3, usage(400))
    assert book.tokens_total_series == 900, "the total tracked the amendment"


def test_the_ledger_does_not_reset_between_sub_games() -> None:
    """The obvious implementation zeroes a counter at each sub-game start, and that reset
    sits exactly where a crash or a role swap interrupts."""
    book = ledger()
    book.record(1, usage(500))
    book.record(6, usage(500))
    assert book.tokens_total_series == 1000


def test_recording_a_sub_game_twice_is_refused_rather_than_summed() -> None:
    """**The realistic corruption.** Replaying after a disconnection is real, and adding the
    second attempt to the first inflates a figure rule 54 requires to be accurate."""
    book = ledger()
    book.record(1, usage(1000))
    with pytest.raises(TokenLedgerError, match="AE-54"):
        book.record(1, usage(1000))


def test_a_replayed_sub_game_is_amended_deliberately() -> None:
    """Both readings are legitimate; only one can be the silent default."""
    book = ledger()
    book.record(1, usage(1000))
    book.amend(1, usage(1500))
    assert book.tokens_total_series == 1500


def test_amending_a_sub_game_that_was_never_recorded_is_refused() -> None:
    """An amend that quietly creates the entry would let a typo'd number add a game that
    was never played."""
    with pytest.raises(TokenLedgerError, match="no entry to amend"):
        ledger().amend(4, usage(10))


def test_an_over_run_is_reported_rather_than_clamped() -> None:
    """A ledger that caps its own number reports a compliant figure for a game that was
    not, which is the contradiction rule 35 scores 0 for both groups."""
    book = ledger(1000)
    book.record(1, usage(1200))
    assert book.over_limit() == (1,)
    assert book.tokens_total_series == 1200, "the real number survives the finding"


def test_every_over_run_is_listed_rather_than_the_first() -> None:
    book = ledger(100)
    for number, spent in ((1, 500), (2, 50), (3, 500)):
        book.record(number, usage(spent))
    assert book.over_limit() == (1, 3)


def test_usage_exactly_at_the_limit_is_not_an_over_run() -> None:
    """The agreed figure is a ceiling that may be reached. An off-by-one here reports a
    compliant game as a breach — a false statement in the direction that costs the
    opponent's trust in every other number we send."""
    book = ledger(1000)
    book.record(1, usage(1000))
    assert book.over_limit() == ()


def test_the_report_carries_both_figures_and_their_evidence() -> None:
    book = ledger(1000)
    book.record(1, usage(400))
    book.record(2, usage(1200))
    assert book.report() == {"max_tokens_per_game": 1000,
                             "per_sub_game": {1: 400, 2: 1200},
                             "tokens_total_series": 1600,
                             "sub_games_over_limit": [2]}


def test_a_series_with_no_usage_is_refused_rather_than_reported_as_zero() -> None:
    """Zero tokens and no measurement are different claims, and only one is reportable."""
    with pytest.raises(TokenLedgerError, match="AE-54"):
        ledger().report()
