"""Predictive barrier squeezing: spend a barrier to shrink the Thief's escape (M6-06).

The book gives the objective and no algorithm. `inst/police_thief_p2p_Summary.md:812`:

    **Resource Management:** The Cop has a limited quota of barriers. Consequently, the
    Cop must manage these resources strategically to **block the Thief's escape routes
    without inadvertently obstructing their own path**.

The reference is no help here either, and says so: its shipped brain "only *occasionally*
walls a cell", is "deliberately simple", and is explicitly "a basic default you should
improve". So the tactic below is ours, and the two clauses of that sentence are the two
halves of it — cut their escapes, do not cut ours.

**Why this needs the belief model.** `barrier_policy.choose_turn_intent` already places a
barrier when one *immediately* traps a known cell, but that condition almost never fires:
a barrier is only placeable within one step of the Cop, and at that range a
distance-reducing move always exists and is taken first. Squeezing has to act on where
the Thief will be, not where it is, which is why this row waited for `M6-02`. The target
here is the belief argmax — a *prediction*, never observed truth.

**Lexicographic, not weighted**, like the rest of the strategy: candidates are ordered by
escapes removed, then by our own mobility preserved, then by proximity to the prediction,
with a fixed tie-break. There is no coefficient to tune, which is also why there is no
tuning value that could leak into the shared configuration (`M6-04a`).

**A squeeze is never taken when it costs us the chase.** A barrier that removes one of
the Thief's escapes but adds a step to our own route is a bad trade at a 35-step horizon,
and the book names that exact failure. Placement is refused rather than accepted with a
penalty, because a strict rule is auditable from the log and a weighted one is not.
"""

from __future__ import annotations

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierError, BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move, legal_moves
from p2p_cop_agent.strategy.pursuit import step_distances

# A squeeze must remove at least this many escapes to be worth a barrier from the quota.
MIN_ESCAPES_REMOVED = 1


def escape_routes(board: Board, cell: Coordinate, blocked: frozenset[Coordinate]) -> int:
    """Return how many directional escapes ``cell`` still has (STAY is not an escape)."""
    return sum(
        1 for action in legal_moves(board, cell, blocked) if action is not Action.STAY
    )


def legal_barrier_cells(
    board: Board, cop: Coordinate, barriers: BarrierField
) -> tuple[Coordinate, ...]:
    """Return every cell this Cop may legally wall this turn, in deterministic order."""
    reachable = (cop, *(apply_move(board, cop, a, frozenset()) for a in legal_moves(board, cop)))
    legal: list[Coordinate] = []
    for cell in reachable:
        try:
            barriers.place_adjacent(board, cop, cell)
        except BarrierError:
            continue
        if cell not in legal:
            legal.append(cell)
    return tuple(legal)


def _steps_to(board: Board, start: Coordinate, goal: Coordinate, blocked: frozenset) -> int:
    """Return the blocked-aware step distance, or a large sentinel when unreachable."""
    return step_distances(board, goal, blocked).get(start, board.grid_size**2 + 1)


def obstructs_our_own_path(
    board: Board,
    cop: Coordinate,
    predicted: Coordinate,
    cell: Coordinate,
    blocked: frozenset[Coordinate],
) -> bool:
    """Return whether walling ``cell`` would lengthen our own route to ``predicted``.

    This is the second half of `:812` made executable. A barrier we stand next to is a
    barrier we may have to walk around.
    """
    return _steps_to(board, cop, predicted, blocked | {cell}) > _steps_to(
        board, cop, predicted, blocked
    )


def choose_squeeze(
    board: Board,
    cop: Coordinate,
    predicted: Coordinate,
    barriers: BarrierField,
    *,
    min_removed: int = MIN_ESCAPES_REMOVED,
) -> Coordinate | None:
    """Return the best legal squeezing cell, or ``None`` when no trade is worth it.

    ``predicted`` is the belief argmax -- where we *think* the Thief will be. Nothing
    here ever receives its true position, so a squeeze cannot become a truth leak.
    """
    board.require_on_board(cop)
    board.require_on_board(predicted)
    blocked = barriers.cells
    if barriers.remaining <= 0:
        return None
    before = escape_routes(board, predicted, blocked)
    if before <= 0:
        return None  # already trapped: a barrier would buy nothing

    ranked: list[tuple[int, int, int, int, int, Coordinate]] = []
    for cell in legal_barrier_cells(board, cop, barriers):
        if cell == predicted:
            continue  # walling the predicted cell is a capture claim, not a squeeze
        after_blocked = blocked | {cell}
        removed = before - escape_routes(board, predicted, after_blocked)
        if removed < min_removed:
            continue
        if obstructs_our_own_path(board, cop, predicted, cell, blocked):
            continue  # `:812`: never at the cost of our own path
        ranked.append((
            -removed,                                        # most escapes removed first
            -escape_routes(board, cop, after_blocked),       # keep our own options open
            abs(cell.row - predicted.row) + abs(cell.col - predicted.col),
            cell.row, cell.col, cell,                        # deterministic tie-break
        ))
    return min(ranked)[-1] if ranked else None
