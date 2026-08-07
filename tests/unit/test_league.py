"""`M7-09*`, `M7-12`, `M7-19*`: the count we declare and what the series is worth.

Rule 38's sanction is **absolute disqualification of the project**, and it does not
distinguish a lie from an arithmetic slip. That makes this the highest-consequence arithmetic
in the repository, so the tests below target the ways the number goes quietly wrong rather
than the happy path.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.reporting.league import (
    DIVERSITY_REWARD,
    LeagueError,
    PlayedGame,
    check_declared,
    counted_against,
    declaration_block,
    diversity_reward,
    series_total,
)

US = "sharNamr"


def game(opponent: str, *, counted: bool = True, won: bool = False) -> PlayedGame:
    return PlayedGame(f"g-{opponent}", opponent, counted, won)


def result(opponent: str, *, winner: str | None = None, **extra) -> dict:
    return {"game_id": f"g-{opponent}", "mutual_agreement": {"opponent_group_id": opponent},
            "final_result": {"winner_group": winner}, **extra}


def test_a_game_is_read_from_its_result_artifact() -> None:
    """Rule 38 does not distinguish a lie from a mistake, so the declared number is derived
    from the same evidence the lecturer receives."""
    read = PlayedGame.from_result(result("rival", winner=US), our_group_id=US)
    assert read.opponent_group_id == "rival" and read.won and read.counted


def test_a_result_naming_no_opponent_is_refused() -> None:
    """Silently dropping it under-declares, which is the direction rule 38 punishes."""
    with pytest.raises(LeagueError, match="names no opponent"):
        PlayedGame.from_result({"game_id": "g"}, our_group_id=US)


def test_a_missing_counted_flag_reads_as_counted() -> None:
    """**Deliberately asymmetric.** Over-declaring is safe; under-declaring is the offence."""
    assert PlayedGame.from_result(result("rival"), our_group_id=US).counted is True


def test_warm_ups_are_excluded_from_the_count() -> None:
    history = [game("rival"), game("rival", counted=False), game("other")]
    assert counted_against(history, "rival") == 1


def test_the_declaration_includes_the_game_being_opened() -> None:
    """Rule 37 is "at the start of each game" — a count omitting it would have both sides
    declaring different totals for the same match."""
    block = declaration_block([game("rival"), game("other")], "rival")
    assert block["games_played_including_this"] == 2
    assert block["counted_games_before_this"] == 1
    assert block["first_meeting_between_groups"] is False


def test_excluded_warm_ups_are_shown_rather_than_hidden() -> None:
    """A count that silently drops games is indistinguishable from one that is wrong."""
    block = declaration_block([game("rival", counted=False)] * 2, "rival")
    assert block["warm_ups_excluded"] == 2 and block["games_played_including_this"] == 1


def test_a_declaration_the_artifacts_do_not_support_is_refused() -> None:
    with pytest.raises(LeagueError, match="AE-38"):
        check_declared(5, [game("rival")], "rival")


def test_a_matching_declaration_passes_quietly() -> None:
    check_declared(2, [game("rival"), game("rival", counted=False)], "rival")


def test_a_win_against_a_new_opponent_earns_the_reward() -> None:
    assert diversity_reward([game("other")], "rival", won=True) == DIVERSITY_REWARD


def test_a_loss_against_a_new_opponent_earns_nothing() -> None:
    """The row is a reward for a **win** against a new opponent — novelty alone pays 0."""
    assert diversity_reward([], "rival", won=False) == 0


def test_a_win_against_a_familiar_opponent_earns_nothing() -> None:
    """Rule 52: repeat games do not accumulate score."""
    assert diversity_reward([game("rival")], "rival", won=True) == 0


def test_a_previous_warm_up_does_not_spend_the_novelty() -> None:
    """The subtle one: a warm-up was never a counted meeting, so the first counted meeting
    is still a first meeting. Treating it otherwise forfeits ten Fixed points."""
    assert diversity_reward([game("rival", counted=False)], "rival",
                            won=True) == DIVERSITY_REWARD


def test_the_series_total_is_recomputed_from_its_lines() -> None:
    """Rule 35 scores a contradicting report 0 for both teams, so the figure we send must be
    one the artifacts reproduce."""
    assert series_total([{"score": 20, "tokens": 100}, {"score": 5, "tokens": 250}]) == {
        "sub_games": 2, "total_score": 25, "tokens_total_series": 350}


def test_a_partial_line_reads_as_zero_rather_than_crashing() -> None:
    assert series_total([{"score": 20}])["tokens_total_series"] == 0


def test_an_empty_series_is_refused_rather_than_reported_as_zero() -> None:
    """A zero total and an empty series are different claims."""
    with pytest.raises(LeagueError, match="no sub-games"):
        series_total([])
