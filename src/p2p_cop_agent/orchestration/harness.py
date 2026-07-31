"""Single-process rules harness: play one local sub-game with no transport.

This is a **local referee for validating rules and termination**, not a peer and
not part of Cop runtime knowledge. It holds objective truth — both positions —
because a referee must. ``CopState`` never receives the Thief's cell, so the
Cop's local truth boundary is preserved: the harness's objective view and the
Cop's local view stay separate objects.

No opponent behaviour ships here. Both policies are supplied by the caller, so
this module never encodes how any particular opponent plays.

Turn order — Thief first, then Cop, capture evaluated after each side acts — was
`PROJECT-PROPOSED` when this was written and is now **book-confirmed** (checked
against the book PDF, 2026-08-01): the Thief moves first in every turn cycle, and
the Cop sees the Thief's hint before choosing its own move. The constant keeps its
name so no caller breaks, and the schedule stays injectable, but the default is no
longer a guess. Nothing here carries contract status.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum, auto
from typing import Final, TypeAlias

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.capture import CaptureReason, capture_reason
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move
from p2p_cop_agent.domain.scoring import Outcome, ScoreLine, ScoringTable
from p2p_cop_agent.orchestration.state import CopState, StateError
from p2p_cop_agent.strategy import BarrierIntent, MoveIntent, TurnIntent

CopPolicy = Callable[[CopState], Action | TurnIntent]
ThiefPolicy = Callable[[Board, Coordinate, Coordinate, BarrierField], Action]


class TurnEvent(Enum):
    """One injectable event in a locally refereed turn."""

    THIEF_ACTION = auto()
    COP_ACTION = auto()
    CAPTURE_CHECK = auto()


TurnOrder: TypeAlias = tuple[TurnEvent, ...]
PROJECT_PROPOSED_TURN_ORDER: Final[TurnOrder] = (
    TurnEvent.THIEF_ACTION,
    TurnEvent.CAPTURE_CHECK,
    TurnEvent.COP_ACTION,
    TurnEvent.CAPTURE_CHECK,
)


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


def _validate_turn_order(turn_order: TurnOrder) -> None:
    """Reject schedules that cannot represent one complete local turn."""
    if not isinstance(turn_order, tuple) or any(
        not isinstance(event, TurnEvent) for event in turn_order
    ):
        raise StateError("turn_order must be a tuple containing only TurnEvent values")
    if turn_order.count(TurnEvent.THIEF_ACTION) != 1:
        raise StateError("turn_order must contain exactly one THIEF_ACTION")
    if turn_order.count(TurnEvent.COP_ACTION) != 1:
        raise StateError("turn_order must contain exactly one COP_ACTION")
    if TurnEvent.CAPTURE_CHECK not in turn_order:
        raise StateError("turn_order must contain at least one CAPTURE_CHECK")


def _apply_cop_intent(cop: CopState, intent: Action | TurnIntent) -> CopState:
    """Apply one exclusive Cop move-or-barrier intent and advance the turn."""
    if isinstance(intent, Action):
        intent = MoveIntent(intent)
    if isinstance(intent, MoveIntent):
        return cop.moved(intent.action).next_turn()
    if isinstance(intent, BarrierIntent):
        return cop.with_barrier_at(intent.cell).next_turn()
    raise StateError(f"Cop policy must return an Action or TurnIntent, got {intent!r}")


def run_sub_game(
    game_config: Mapping[str, object],
    cop_policy: CopPolicy,
    thief_policy: ThiefPolicy,
    *,
    turn_order: TurnOrder = PROJECT_PROPOSED_TURN_ORDER,
) -> SubGameResult:
    """Referee one sub-game to a terminal state and return the scored result.

    The Cop policy receives only ``CopState`` and returns one movement or barrier
    intent. It never receives the referee's objective Thief position. The event
    schedule is injectable because actor and capture-check ordering remain
    provisional; the default merely preserves the documented project proposal.
    """
    _validate_turn_order(turn_order)
    threshold = _survival_threshold(game_config)
    table = ScoringTable.from_config(game_config)
    cop = CopState.opening(game_config)
    thief = _thief_start(game_config)

    for turn in range(1, threshold + 1):
        for event in turn_order:
            if event is TurnEvent.THIEF_ACTION:
                evasion = thief_policy(cop.board, thief, cop.position, cop.barriers)
                thief = apply_move(cop.board, thief, evasion, cop.blocked)
            elif event is TurnEvent.COP_ACTION:
                cop = _apply_cop_intent(cop, cop_policy(cop))
            else:
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
