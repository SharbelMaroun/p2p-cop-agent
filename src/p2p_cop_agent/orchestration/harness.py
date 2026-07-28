"""Single-process rules harness: play one local sub-game with no transport.

This is a **local referee for validating rules and termination**, not a peer and
not part of Cop runtime knowledge. It holds objective truth — both positions —
because a referee must. ``CopState`` never receives the Thief's cell, so the
Cop's local truth boundary is preserved: the harness's objective view and the
Cop's local view stay separate objects.

No opponent behaviour ships here. Both policies are supplied by the caller, so
this module never encodes how any particular opponent plays.

Turn order is `PROJECT-PROPOSED`, not book-confirmed: the Thief acts first, then
the Cop, and capture is evaluated after each side acts. It is injectable for
exactly that reason — when an authoritative live-turn ordering arrives, it drops
in without touching the rules. Nothing here carries contract status.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.capture import CaptureReason, capture_reason
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move
from p2p_cop_agent.domain.scoring import Outcome, ScoreLine, ScoringTable
from p2p_cop_agent.orchestration.state import CopState, StateError

CopPolicy = Callable[[CopState, Coordinate], Action]
ThiefPolicy = Callable[[Board, Coordinate, Coordinate, BarrierField], Action]


@dataclass(frozen=True, slots=True)
class SubGameResult:
    """The decided result of one locally refereed sub-game."""

    outcome: Outcome
    score: ScoreLine
    turns: int
    reason: CaptureReason | None


def _survival_threshold(game_config: Mapping[str, object]) -> int:
    """Return the configured survival threshold in turns."""
    section = game_config.get("movement_and_barriers")
    threshold = section.get("survival_threshold") if isinstance(section, Mapping) else None
    if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
        raise StateError(f"survival_threshold must be a positive integer, got {threshold!r}")
    return threshold


def _thief_start(game_config: Mapping[str, object]) -> Coordinate:
    """Return the agreed Thief start; public, and held only by the referee."""
    section = game_config.get("board_and_agents")
    if not isinstance(section, Mapping):
        raise StateError("game config is missing a board_and_agents object")
    return Coordinate.from_pair(section.get("thief_start"))


def run_sub_game(
    game_config: Mapping[str, object],
    cop_policy: CopPolicy,
    thief_policy: ThiefPolicy,
) -> SubGameResult:
    """Referee one sub-game to a terminal state and return the scored result.

    The Cop policy receives its own ``CopState`` plus a presumed Thief cell. In
    this harness the referee supplies the true cell, which is a **simulation
    affordance for rules validation only**: without the M6 belief model there is
    no principled presumption to supply, and the purpose here is to prove that
    the rules terminate, not to measure strategy quality.
    """
    threshold = _survival_threshold(game_config)
    table = ScoringTable.from_config(game_config)
    cop = CopState.opening(game_config)
    thief = _thief_start(game_config)

    for turn in range(1, threshold + 1):
        evasion = thief_policy(cop.board, thief, cop.position, cop.barriers)
        thief = apply_move(cop.board, thief, evasion, cop.blocked)
        decided = _decide(cop, thief, turn, table)
        if decided is not None:
            return decided
        cop = cop.moved(cop_policy(cop, thief)).next_turn()
        decided = _decide(cop, thief, turn, table)
        if decided is not None:
            return decided
    return SubGameResult(Outcome.SURVIVAL, table.award(Outcome.SURVIVAL), threshold, None)


def _decide(
    cop: CopState,
    thief: Coordinate,
    turn: int,
    table: ScoringTable,
) -> SubGameResult | None:
    """Return a capture result when any capture condition holds, else None."""
    reason = capture_reason(cop.board, cop.position, thief, cop.barriers)
    if reason is None:
        return None
    return SubGameResult(Outcome.CAPTURE, table.award(Outcome.CAPTURE), turn, reason)
