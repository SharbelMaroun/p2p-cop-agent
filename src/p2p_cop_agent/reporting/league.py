"""How many games we have played against whom, and what the series is worth.

Covers `M7-09`, `M7-09a`, `M7-09b`, `M7-12`, `M7-19`, `M7-19a`, `M7-19b`.

Rule 37 (Mandatory): declare accurately the number of games actually played at the start of
each game. Rule 38 (Prohibited): a false declaration **disqualifies the project** — "absolute
disqualification for disciplinary and integrity reasons".

That sanction is why nothing here is hand-entered. A tally somebody maintains is a number a
human can be wrong about; a count derived from the result artifacts on disk is the same
evidence the lecturer receives, so the two cannot disagree. Rule 38 does not distinguish a
lie from an arithmetic slip.

**Warm-ups do not count** (rule 52): only one game per opponent accumulates score, and
warm-ups are permitted but uncounted. A game must therefore be marked at emission — deciding
afterwards which games "were really warm-ups", once the scores are known, is precisely the
false declaration rule 38 forbids.

**The diversity reward is 10 points, Fixed** (Appendix F table 18), for a **win** against an
opponent not met before. Not a draw, not a loss, and not a repeat: rule 52 says repeat games
accumulate nothing at all.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

DIVERSITY_REWARD = 10


class LeagueError(ValueError):
    """Raised when a declared history would not match the artifacts that back it."""


@dataclass(frozen=True, slots=True)
class PlayedGame:
    """One finished game, as its result artifact records it."""

    game_id: str
    opponent_group_id: str
    counted: bool = True
    won: bool = False

    @classmethod
    def from_result(cls, result: Mapping[str, object], *, our_group_id: str) -> PlayedGame:
        """Read a game from its emitted result artifact (`M7-09a`).

        `counted` defaults to **True**. A result that forgot the flag is far likelier to be
        a counted game with a missing field than an unlabelled warm-up — and under rule 38
        over-declaring is safe while under-declaring is the offence.
        """
        agreement = result.get("mutual_agreement")
        opponent = ""
        if isinstance(agreement, Mapping):
            opponent = str(agreement.get("opponent_group_id") or "")
        if not opponent:
            raise LeagueError(
                f"result {result.get('game_id')!r} names no opponent; rule 37 counts per "
                "opponent and an unattributed game cannot be counted against anyone")
        final = result.get("final_result")
        won = bool(isinstance(final, Mapping)
                   and final.get("winner_group") == our_group_id)
        return cls(game_id=str(result.get("game_id") or ""), opponent_group_id=opponent,
                   counted=bool(result.get("counted", True)), won=won)


def counted_against(played: Iterable[PlayedGame], opponent: str) -> int:
    """Counted games against one opponent, warm-ups excluded (`M7-09b`, `M7-12`)."""
    return sum(1 for game in played if game.opponent_group_id == opponent and game.counted)


def declaration_block(played: Sequence[PlayedGame], opponent: str) -> dict[str, object]:
    """The block rule 37 requires at the start of a game, derived rather than asserted.

    The count **includes the game being opened**: rule 37 is "at the start of each game", so
    a number that omitted it would have both sides declaring different totals for the same
    match.
    """
    before = counted_against(played, opponent)
    return {
        "opponent_group_id": opponent,
        "games_played_including_this": before + 1,
        "counted_games_before_this": before,
        "first_meeting_between_groups": before == 0,
        "warm_ups_excluded": sum(1 for g in played
                                 if g.opponent_group_id == opponent and not g.counted),
    }


def check_declared(declared: int, played: Sequence[PlayedGame], opponent: str) -> None:
    """Refuse a declaration the artifacts do not support (`M7-09`)."""
    actual = counted_against(played, opponent) + 1
    if declared != actual:
        raise LeagueError(
            f"declared {declared} game(s) against {opponent!r} but the result artifacts show "
            f"{actual}; rule 38 disqualifies the project for a false declaration [AE-38]")


def diversity_reward(played: Sequence[PlayedGame], opponent: str, *, won: bool) -> int:
    """Ten points for a **win** against a group not met before (`M7-19b`).

    Two conditions, both easy to drop. A first meeting that we lose earns nothing, and a win
    against a familiar opponent earns nothing either. A previous *warm-up* does not spend the
    novelty, because a warm-up was never a counted meeting — treating it as one silently
    forfeits ten Fixed points.
    """
    if not won:
        return 0
    return DIVERSITY_REWARD if counted_against(played, opponent) == 0 else 0


def series_total(sub_games: Iterable[Mapping[str, object]]) -> dict[str, int]:
    """Recompute the series from its stored sub-game lines (`M7-19`, `M7-19a`).

    Recomputed, never carried. A total that travels beside the lines can contradict them,
    and rule 35 scores a contradicting report 0 for **both** teams — so the figure we send
    has to be one the artifacts reproduce.
    """
    lines = list(sub_games)
    if not lines:
        raise LeagueError("a series with no sub-games has no total to report")
    return {
        "sub_games": len(lines),
        "total_score": sum(int(line.get("score", 0)) for line in lines),
        "tokens_total_series": sum(int(line.get("tokens", 0)) for line in lines),
    }
