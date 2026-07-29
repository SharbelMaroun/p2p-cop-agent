"""Deterministic baseline decision between moving and placing a barrier.

A turn is one or the other, never both: placing a barrier gives up that turn's
movement (book §3.4). The returned intent type encodes that exclusivity, so a
caller cannot express an illegal "move and place" turn.

Barrier *mechanics* are confirmed rules: placement on the Cop's own cell or one
orthogonal step, a barrier on the Thief's cell captures, a Thief with no legal
move is captured, and the quota is bounded. What to do with those mechanics is
private strategy and carries no contract status.

Priority, highest first:

1. **Move to capture.** If the Thief's cell is one step away, move onto it. That
   captures exactly as a barrier there would but spends no quota, so it strictly
   dominates placing one.
2. **Trap.** Otherwise, place a barrier that removes the Thief's last legal move.
   Skipped when the Thief is already trapped, since capture has already occurred
   and a further barrier would waste quota.
3. **Pursue.** Otherwise, move by the pursuit baseline.

## Why there is no "squeeze" rule here

The book also describes squeezing the Thief toward corners and pre-emptively
walling escape corridors. Neither is expressible against a *known* Thief cell,
and the reason is structural rather than a simplification:

A barrier only reduces the Thief's mobility if it is orthogonally adjacent to
the Thief. Placement range is one step from the Cop. So whenever such a barrier
is placeable at all, the Cop stands at most two steps from the Thief — and at
any finite distance greater than zero a distance-reducing move always exists,
because barrier-aware breadth-first distance changes by exactly one between
adjacent cells. Rule 3 therefore always outranks a squeeze, and a squeeze branch
would be unreachable code.

Genuine squeezing requires predicting where the Thief will go, which needs the
M6 belief model. It is deliberately left until that exists rather than shipped
as a rule that can never fire.
"""

from __future__ import annotations

from dataclasses import dataclass

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierError, BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move, legal_moves
from p2p_cop_agent.strategy.pursuit import choose_action


@dataclass(frozen=True, slots=True)
class MoveIntent:
    """Spend the turn moving."""

    action: Action


@dataclass(frozen=True, slots=True)
class BarrierIntent:
    """Spend the turn placing one disclosed barrier."""

    cell: Coordinate


TurnIntent = MoveIntent | BarrierIntent


def _mobility(board: Board, cell: Coordinate, blocked: frozenset[Coordinate]) -> int:
    """Return how many directional escapes the given cell still has."""
    return sum(1 for action in legal_moves(board, cell, blocked) if action is not Action.STAY)


def _candidates(board: Board, cop: Coordinate, barriers: BarrierField) -> tuple[Coordinate, ...]:
    """Return every legal barrier cell for this turn, in deterministic order."""
    reachable = (cop, *(apply_move(board, cop, a, frozenset()) for a in legal_moves(board, cop)))
    legal = []
    for cell in reachable:
        try:
            barriers.place_adjacent(board, cop, cell)
        except BarrierError:
            continue
        legal.append(cell)
    return tuple(legal)


def choose_turn_intent(
    board: Board,
    cop: Coordinate,
    target: Coordinate,
    barriers: BarrierField,
) -> TurnIntent:
    """Return the deterministic legal turn intent: one move or one barrier.

    Both cells are validated first. An off-board cell has no on-board
    neighbours, so an unvalidated target would read as already trapped and
    produce a bogus barrier placement.
    """
    board.require_on_board(cop)
    board.require_on_board(target)
    blocked = barriers.cells

    for action in legal_moves(board, cop, blocked):
        if apply_move(board, cop, action, blocked) == target:
            return MoveIntent(action)

    if _mobility(board, target, blocked) > 0:
        for cell in _candidates(board, cop, barriers):
            if _mobility(board, target, blocked | {cell}) == 0:
                return BarrierIntent(cell)

    return MoveIntent(choose_action(board, cop, target, blocked))
