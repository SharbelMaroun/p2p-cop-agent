"""Search-chosen Cop turns: the entry point the policy stack calls (M11-02).

The shipped stack is a priority ladder -- capture if you can, else squeeze, else contain,
else intercept. Each rung is sound on its own and none of them can see two turns ahead,
so the stack cannot tell a barrier that begins a seal from a barrier that merely removes
one exit: to a rule that scores only the current turn they look identical.

This searches instead, through `engine_search`, with both sides given full information
and the Thief assumed to play the best reply. That is deliberately pessimistic -- a real
evader plays worse than the search's model of it, so a capture this engine believes in
survives contact with one that does not.

This module owns only the boundary: `Coordinate` and `BarrierField` in, `TurnIntent` out,
bit indices in between. Its signature matches the shipped choosers exactly, so it drops
into the same slot as `denial_turn_intent` with no other change.
"""

from __future__ import annotations

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, MoveIntent, TurnIntent
from p2p_cop_agent.strategy.bitboard import cell_of, neighbours
from p2p_cop_agent.strategy.engine_eval import CAPTURE, Weights, free_mask
from p2p_cop_agent.strategy.engine_search import MAX_DEPTH, Budget, search_root

# Nodes per decision. 20k keeps a 7x7 turn well inside a tenth of a second on the
# recorded hardware -- two orders under the 30s `step_deadline_seconds` cap, which is the
# margin the deadline tracker needs on a machine that is also serving MCP over a tunnel.
DEFAULT_BUDGET = 20_000

# Deepening in whole turns: a Cop ply and the Thief's reply are one unit of foresight,
# and stopping between them would let the search count a capture the Thief still gets to
# answer.
DEPTH_STEP = 2


def engine_turn_intent(
    board: Board,
    cop: Coordinate,
    believed: Coordinate,
    barriers: BarrierField,
    previous: Coordinate | None = None,
    *,
    weights: Weights | None = None,
    budget: int = DEFAULT_BUDGET,
    horizon: int = 64,
) -> TurnIntent:
    """Return the Cop's move or barrier for this turn, searched to a node budget.

    ``previous`` is accepted so this is a drop-in for the shipped stack's signature; the
    search has no use for it, because a position the ratchet would remember is one the
    search can simply look at.

    ``horizon`` is the number of turns left in the sub-game. It matters: a capture that
    needs six more turns is worth nothing on turn 33, and a search that does not know the
    game ends will happily plan one.
    """
    size = board.grid_size
    origin = board.min_index
    weights = weights or Weights()
    free = free_mask(size, frozenset(
        (cell.row - origin, cell.col - origin) for cell in barriers.placements))
    cop_index = _index(cop, size, origin)
    thief_index = _index(believed, size, origin)
    if not free & (1 << thief_index):
        # The believed cell is one we have already walled, so there is nothing there to
        # chase. Standing still beats walking confidently at a barrier.
        return MoveIntent(Action.STAY)
    if thief_index == cop_index:
        # A belief pointing at our own cell is not a capture, and must never be read as
        # one: the Thief standing here would have ended the sub-game already, so this is
        # a mis-aimed belief. Reporting it as a capture would put a **false capture claim
        # on the wire**, and rule 22 answers that with disqualification, not a lost turn.
        return _first_step(cop_index, free, size, origin)

    action: tuple[str, int] = ("move", cop_index)
    for depth in range(DEPTH_STEP, MAX_DEPTH + 1, DEPTH_STEP):
        allowance = Budget(budget)
        candidate, value = search_root(cop_index, thief_index, free, barriers.remaining,
                                       size, depth, weights, allowance, horizon)
        if allowance.left <= 0:
            # **Discard an iteration the budget cut short.** When the allowance runs out
            # every remaining node returns its static evaluation, so the later actions of
            # that sweep were scored at a shallower depth than the earlier ones and the
            # comparison between them is meaningless. Measured, not reasoned: keeping the
            # truncated sweep scored 58/120 against the archetype grid where discarding it
            # and playing the last *complete* depth scores far higher, and it was the
            # whole gap between the small-budget and large-budget arms.
            break
        action = candidate
        if value >= CAPTURE - MAX_DEPTH:
            break
    return _intent(action, cop_index, size, origin)


def _index(cell: Coordinate, size: int, origin: int) -> int:
    """Return the bit index of a board coordinate."""
    return (cell.row - origin) * size + (cell.col - origin)


def _first_step(cop: int, free: int, size: int, origin: int) -> TurnIntent:
    """Return a deterministic legal step off the current cell, or STAY if walled in."""
    reachable = neighbours(cell_of(cop, size), size) & free
    if not reachable:
        return MoveIntent(Action.STAY)
    low = reachable & -reachable
    return _intent(("move", low.bit_length() - 1), cop, size, origin)


def _intent(action: tuple[str, int], cop: int, size: int, origin: int) -> TurnIntent:
    """Return the domain intent for a searched action."""
    kind, target = action
    row, col = cell_of(target, size)
    if kind == "barrier":
        return BarrierIntent(Coordinate(row + origin, col + origin))
    if target == cop:
        return MoveIntent(Action.STAY)
    origin_row, origin_col = cell_of(cop, size)
    if row < origin_row:
        return MoveIntent(Action.NORTH)
    if row > origin_row:
        return MoveIntent(Action.SOUTH)
    return MoveIntent(Action.EAST if col > origin_col else Action.WEST)
