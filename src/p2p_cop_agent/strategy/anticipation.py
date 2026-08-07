"""Predictive pursuit: close on where the believed Thief can go, not where it was (M6-22).

`pursue_belief` chases the belief argmax — the cell the evidence says the Thief *was*
emitting from. Against a fleeing opponent that is systematically one step stale: by the
time the Cop arrives, a competent Thief has left, and a pursuit that only ever aims at
the last sighting tows behind it forever. The companion Thief repository measured this
from the other side: its evasion escapes a current-cell chaser 23/24, and an
anticipating chaser — one that aims at the *centroid of the Thief's next legal cells* —
cuts that to 8/24. This module is that chaser, built for our side of the board.

**The aim point is the flight set's centroid, not a cell.** The flight set is the
believed cell plus every legal one-step destination from it, honouring our own placed
barriers (a walled cell is not an escape, which is what makes this compose with the
squeeze). Its centroid is usually fractional; distance to it is computed in integers by
scaling both axes by the set's size, so no float ever enters a comparison and the
choice stays exactly reproducible (M6-03d). On an open interior the centroid sits on
the believed cell and this decays to plain pursuit; at walls, corners, and next to our
barriers — precisely where captures happen — it leads the target into the side the
Thief can still run toward.

Barrier-aware reachability stays the second criterion: among moves equally close to
the centroid, the one with the shorter breadth-first route to the believed cell wins,
so anticipation refines pursuit and can never abandon it. The belief itself is supplied
by the caller and nothing here reads a true position `[AE-8]`.
"""

from __future__ import annotations

from collections.abc import Set as AbstractSet

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move, legal_moves
from p2p_cop_agent.strategy.barrier_policy import (
    BarrierIntent,
    MoveIntent,
    TurnIntent,
    choose_turn_intent,
)
from p2p_cop_agent.strategy.containment import choose_containment
from p2p_cop_agent.strategy.pursuit import step_distances
from p2p_cop_agent.strategy.squeeze import choose_squeeze

_NO_BARRIERS: frozenset[Coordinate] = frozenset()


def flight_cells(
    board: Board,
    believed: Coordinate,
    blocked: AbstractSet[Coordinate] = _NO_BARRIERS,
) -> tuple[Coordinate, ...]:
    """Return the believed cell and every cell one legal Thief step away from it.

    ``STAY`` is covered by the believed cell itself; a destination behind one of our
    barriers is excluded because the Thief cannot legally be there next turn.
    """
    board.require_on_board(believed)
    moves = (
        apply_move(board, believed, action, blocked)
        for action in legal_moves(board, believed, blocked)
        if action is not Action.STAY
    )
    return (believed, *moves)


def anticipating_action(
    board: Board,
    cop: Coordinate,
    believed: Coordinate,
    blocked: AbstractSet[Coordinate] = _NO_BARRIERS,
) -> Action:
    """Return the legal move that best cuts off the believed Thief's flight set.

    Ranking, ascending and wholly integer: scaled Manhattan distance to the flight
    centroid, then barrier-aware step distance to the believed cell, then the fixed
    ``Action`` order. When barriers seal us off from the believed cell entirely the
    reachability term is absent for every candidate equally, and the centroid still
    gives chase a direction rather than a shrug.
    """
    board.require_on_board(cop)
    cells = flight_cells(board, believed, blocked)
    scale = len(cells)
    centroid_row = sum(cell.row for cell in cells)
    centroid_col = sum(cell.col for cell in cells)
    reach = step_distances(board, believed, blocked)
    far = board.grid_size * board.grid_size + 1

    def rank(action: Action) -> tuple[int, int, int]:
        destination = apply_move(board, cop, action, blocked)
        lead = (abs(destination.row * scale - centroid_row)
                + abs(destination.col * scale - centroid_col))
        return (lead, reach.get(destination, far), list(Action).index(action))

    return min(legal_moves(board, cop, blocked), key=rank)


def predictive_turn_intent(
    board: Board,
    cop: Coordinate,
    believed: Coordinate,
    barriers: BarrierField,
    previous: Coordinate | None = None,
) -> TurnIntent:
    """Return the full live intent: capture or trap, else squeeze, else lead the chase.

    Strict priority, every layer already shipped and tested separately:

    1. `choose_turn_intent` — move onto the believed cell when adjacent (capture claim
       for free), or wall its last exit (a trap ends the game where a chase only
       continues it);
    2. `choose_squeeze` — while still closing, spend a barrier that cuts flight routes
       without lengthening our own path (the resource management `:812` demands);
    3. `choose_containment` — else, in a locked endgame orbit, wall the cell we just
       vacated (`previous`) so the pursuit path ratchets into a permanent wall, never
       sealing the Thief beyond our own reach;
    4. `anticipating_action` — otherwise close on the flight-set centroid rather than
       the stale sighting.

    The opponent grid is why the composition exists: **every barrier-free arm —
    including the oracle — captured a fleeing archetype 0/40.** Pursuit alone never
    corners an equal-speed evader on an open board; barriers are the entire capture
    mechanism against competent opposition, and anticipation is what makes the chase
    herd the Thief toward the walls being built.
    """
    chosen = choose_turn_intent(board, cop, believed, barriers)
    if isinstance(chosen, BarrierIntent):
        return chosen
    blocked = barriers.cells
    distance = step_distances(board, believed, blocked).get(cop)
    if distance is not None and distance > 1:
        squeeze = choose_squeeze(board, cop, believed, barriers)
        if squeeze is not None:
            return BarrierIntent(squeeze)
        containment = choose_containment(board, cop, believed, barriers, previous)
        if containment is not None:
            return BarrierIntent(containment)
    return MoveIntent(anticipating_action(board, cop, believed, blocked))
