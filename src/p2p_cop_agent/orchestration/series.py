"""The six-sub-game series and its role schedule (`M7-01`, `M7-07`).

**The schedule is settled, not inferred.** `U-025` closed on 2026-07-31 with a lecturer
answer relayed by the coordinator: sub-games **1, 3, 5 natural role; 2, 4, 6 swapped;
Thief moves first**. It is a constant here rather than a computed alternation, because a
formula would be one refactor away from silently disagreeing with the ruling.

**Six, and that took reading two rows carefully.** Appendix F prints *two* rows labelled
"[Number of Agents]": `:3484` is "number of players in the race | 2 | Fixed", and `:3540`
is "number of agents **in a series against an opponent** | 6 | Fixed". The second is the
games count under a mistranslated label — its description says so. The template at
`:2963` carries `"num_games": 1`, which is a single-game default for the example file, not
the league requirement.

**What resets and what does not.** Each sub-game is a fresh game: its own barrier quota,
its own scent field, its own belief. Carrying belief across would be worse than a bug — it
would mean our score in sub-game 4 depended on inference gathered while we were the other
role, which is not a thing the rules contemplate. Only the *series* identity persists, so
all twelve per-sub-game artifacts share one `game_uid` (`M7-02c`).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum

from p2p_cop_agent.reporting.naming import MatchIdentity

SUB_GAMES = 6
# `U-025`, coordinator-relayed lecturer answer 2026-07-29. Written out rather than derived.
NATURAL_SUB_GAMES = (1, 3, 5)
SWAPPED_SUB_GAMES = (2, 4, 6)


class Role(str, Enum):
    COP = "cop"
    THIEF = "thief"


class SeriesError(ValueError):
    """Raised when a series would be played on a schedule the ruling does not describe."""


def role_for(sub_game: int, natural_role: Role) -> Role:
    """Return which role we play in this sub-game, per the closed `U-025` schedule."""
    if sub_game in NATURAL_SUB_GAMES:
        return natural_role
    if sub_game in SWAPPED_SUB_GAMES:
        return Role.THIEF if natural_role is Role.COP else Role.COP
    raise SeriesError(f"sub-game {sub_game} is outside the fixed series of {SUB_GAMES}")


def schedule(natural_role: Role) -> tuple[tuple[int, Role], ...]:
    """The whole series as (sub_game, our_role), in play order."""
    return tuple((n, role_for(n, natural_role)) for n in range(1, SUB_GAMES + 1))


def each_side_plays_both_roles(natural_role: Role) -> bool:
    """The property the alternation exists for: neither side is only ever the pursuer."""
    roles = {role for _, role in schedule(natural_role)}
    return roles == {Role.COP, Role.THIEF}


@dataclass(frozen=True, slots=True)
class SubGameLine:
    """One sub-game's contribution to the series result."""

    sub_game: int
    role: Role
    outcome: str
    cop_score: int
    thief_score: int
    tokens: int

    def as_result_line(self) -> Mapping[str, object]:
        return {
            "sub_game": self.sub_game, "outcome": self.outcome,
            "cop_score": self.cop_score, "thief_score": self.thief_score,
            "tokens": self.tokens,
        }


@dataclass(frozen=True, slots=True)
class SeriesResult:
    """The whole meeting: every line, and what the six of them add up to."""

    identity: MatchIdentity
    lines: tuple[SubGameLine, ...]

    @property
    def complete(self) -> bool:
        return len(self.lines) == SUB_GAMES

    def cumulative(self, tie_award: int) -> Mapping[str, object]:
        """Sum the series. `:2042`: an equal total is a "Tie Score" for each group, so a
        draw is a decided result -- "no meeting remains without a decision"."""
        cop = sum(line.cop_score for line in self.lines)
        thief = sum(line.thief_score for line in self.lines)
        if cop == thief:
            return {"winner": "tie", "cop_score": tie_award, "thief_score": tie_award,
                    "raw_cop": cop, "raw_thief": thief}
        return {"winner": "cop" if cop > thief else "thief",
                "cop_score": cop, "thief_score": thief}


def run_series(
    identity: MatchIdentity,
    natural_role: Role,
    play: Callable[[int, Role], SubGameLine],
) -> SeriesResult:
    """Play all six sub-games on the fixed schedule and collect their lines.

    ``play`` is injected, so this module orchestrates without owning transport, strategy
    or artifacts -- the same separation `M7-25` requires of emission.
    """
    lines = []
    for sub_game, role in schedule(natural_role):
        line = play(sub_game, role)
        if line.sub_game != sub_game:
            raise SeriesError(f"sub-game {sub_game} returned a line for {line.sub_game}")
        lines.append(line)
    return SeriesResult(identity, tuple(lines))


def artifact_names(identity: MatchIdentity) -> Sequence[str]:
    """Every filename one series produces: two per series, two per sub-game (`M7-01a`)."""
    from p2p_cop_agent.reporting.naming import match_filenames

    return tuple(sorted(match_filenames(identity, tuple(range(1, SUB_GAMES + 1))).values()))
