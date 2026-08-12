"""Sanctuary denial: make "stay interior" a strategy about nothing (M10, `flee_interior`).

`uoh-ay26`'s post-G003 evader hard-excludes any move with less **board-edge clearance**
than its best safe option -- it is magnetically bound to the highest-clearance cells,
and its proximity filter makes it flee the Cop. Both together are the exploit:

* its sanctuary is *geometric* -- barriers do not enter its clearance arithmetic, so a
  barriered sanctuary is simply gone, and the next ring outward becomes the new
  sanctuary the moment the old one is unreachable;
* it will not contest ground near the Cop, so the Cop can walk the sanctuary and
  barrier it out from under the evader **unopposed**.

One rule, applied until a reserve is reached: compute the unblocked maximum-clearance
set; barrier it when adjacent, walk toward it otherwise. On 7x7 that denies (3,3),
then eats into the 16-cell clearance-2 ring, whose severed arcs end in exactly the
walls the incumbent squeeze/containment/interception stack corners evaders against.
The finishing layers always speak first, so a capturable turn is never spent digging.

The reserve keeps barriers for the incumbent's own endgame walls; measured, not
guessed -- see `results/tournament_grid.json` for the arm this module adds.
"""

from __future__ import annotations

from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import Action, apply_move, legal_moves
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, MoveIntent, TurnIntent
from p2p_cop_agent.strategy.pursuit import step_distances
from p2p_cop_agent.strategy.shrink import shrinking_turn_intent

#: Barriers held back for the incumbent stack's own walls (trap, squeeze, ratchet).
DENIAL_RESERVE = 3


def _clearance(board: Board, cell: Coordinate) -> int:
    low = board.min_index
    high = board.max_index
    return min(cell.row - low, cell.col - low, high - cell.row, high - cell.col)


def sanctuary_cells(board: Board, blocked: frozenset[Coordinate]) -> tuple[Coordinate, ...]:
    """The unblocked cells the evader's clearance magnet is drawn to, in denial order.

    Phase 1 is the whole clearance>=2 core (9 cells on 7x7): while any of it stands,
    the evader orbits it, so all of it goes. Phase 2 is the clearance-1 ring -- not to
    fill it (16 cells is beyond any quota) but because a single barrier **cuts the
    orbit into a path**, and equal-speed pursuit corners an evader on a path where it
    never can on a cycle. The board's outer edge is the last cycle, cut the same way.
    """
    cells = [
        Coordinate(row, col)
        for row in range(board.min_index, board.max_index + 1)
        for col in range(board.min_index, board.max_index + 1)
        if Coordinate(row, col) not in blocked
    ]
    core = [cell for cell in cells if _clearance(board, cell) >= 2]
    if core:
        return tuple(sorted(core, key=lambda cell: (cell.row, cell.col)))
    best = max(_clearance(board, cell) for cell in cells)
    return tuple(sorted(
        (cell for cell in cells if _clearance(board, cell) == best),
        key=lambda cell: (cell.row, cell.col),
    ))


def denial_turn_intent(
    board: Board,
    cop: Coordinate,
    believed: Coordinate,
    barriers: BarrierField,
    previous: Coordinate | None = None,
) -> TurnIntent:
    """The denial stack: finishing layers first, then sanctuary denial, then chase."""
    incumbent = shrinking_turn_intent(board, cop, believed, barriers, previous)
    # A finishing wall or a capture step is always better than development.
    if isinstance(incumbent, BarrierIntent):
        return incumbent
    if apply_move(board, cop, incumbent.action, barriers.cells) == believed:
        return incumbent

    if barriers.remaining > DENIAL_RESERVE:
        sanctuary = [cell for cell in sanctuary_cells(board, barriers.cells)
                     if cell != believed and cell != cop]
        core_phase = any(_clearance(board, cell) >= 2 for cell in sanctuary)
        far_enough = abs(believed.row - cop.row) + abs(believed.col - cop.col) >= 3
        if sanctuary and (core_phase or far_enough):
            adjacent = [cell for cell in sanctuary
                        if abs(cell.row - cop.row) + abs(cell.col - cop.col) == 1]
            if adjacent:
                return BarrierIntent(adjacent[0])
            # Ring phase: one cut per orbit is enough -- walk to the nearest ring
            # cell only while the evader is elsewhere; the chase does the rest.
            towards = _step_towards(board, cop, sanctuary, barriers.cells)
            if towards is not None:
                return MoveIntent(towards)

    return incumbent


def _step_towards(
    board: Board,
    cop: Coordinate,
    targets: list[Coordinate],
    blocked: frozenset[Coordinate],
) -> Action | None:
    """One legal step reducing the distance to the nearest target, deterministically."""
    reach = step_distances(board, cop, blocked)
    far = board.grid_size * board.grid_size + 1
    goal = min(targets, key=lambda cell: (reach.get(cell, far), cell.row, cell.col))
    if reach.get(goal, far) >= far:
        return None
    best: tuple[int, str] | None = None
    chosen: Action | None = None
    for action in legal_moves(board, cop, blocked):
        if action is Action.STAY:
            continue
        landing = apply_move(board, cop, action, blocked)
        cost = step_distances(board, landing, blocked).get(goal, far)
        rank = (cost, action.name)
        if best is None or rank < best:
            best, chosen = rank, action
    return chosen
