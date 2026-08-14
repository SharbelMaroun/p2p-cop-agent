"""Containment pursuit: shrink the evader's future free region (Phase C, structural gap).

`denial` loses to `flee_smart`/`flee_deadend` 17/24 even with PERFECT localization: a
mobility-maximizing evader on an open board is never cornered by an equal-speed chase, and
denial's sanctuary trick needs the board-edge-clearance tell those two archetypes lack.
This policy herds instead of chasing -- it scores each legal action by the evader's Voronoi
*free region* (the cells the evader reaches strictly before the Cop) and drives it toward
zero, cutting it with a barrier when the Cop is close enough for one to bite.

It is additive over the proven stack, never a replacement:

* a finishing capture or trapping barrier (`shrink`) is returned unchanged;
* a barrier `denial` would place -- its sanctuary/orbit cut, which is what beats
  `flee_interior` -- is returned unchanged; containment only ever replaces the *chase*;
* when region minimization finds no improving legal action it falls back to `denial`.

Strategy proposes; the domain `BarrierField.place_adjacent` stays the sole legality
authority (illegal candidates raise and are skipped). Deterministic throughout -- fixed
action order and row-major cell order -- so replays and audits reproduce (M6-03d).
"""

from __future__ import annotations

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierError, BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move, legal_moves
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, MoveIntent, TurnIntent
from p2p_cop_agent.strategy.denial import denial_turn_intent
from p2p_cop_agent.strategy.pursuit import step_distances
from p2p_cop_agent.strategy.shrink import shrinking_turn_intent

_ACTIONS = list(Action)
#: Barriers held for the finishing stack; containment cuts spend only above this reserve.
CONTAIN_RESERVE = 2
#: Rank sentinel for an action that captures: below any real (region, ...) key.
_CAPTURE = (-1, -1, -1)


def free_region(
    board: Board, evader: Coordinate, cop: Coordinate, blocked: frozenset[Coordinate]
) -> int:
    """Count cells the evader reaches strictly before the Cop -- its future free region.

    The barrier-aware Voronoi split: a cell falls to the evader when its step distance from
    the evader is strictly less than from the Cop (a tie is contested, and conceded to the
    Cop). Minimising it corners a mobility-maximiser an equal-speed chase never closes on.
    """
    far = board.grid_size * board.grid_size + 1
    reach_e = step_distances(board, evader, blocked)
    reach_c = step_distances(board, cop, blocked)
    return sum(1 for cell, de in reach_e.items() if de < reach_c.get(cell, far))


def _mobility(board: Board, cell: Coordinate, blocked: frozenset[Coordinate]) -> int:
    return sum(1 for action in legal_moves(board, cell, blocked) if action is not Action.STAY)


def _score(
    board: Board, evader: Coordinate, cop_after: Coordinate, blocked_after: frozenset[Coordinate]
) -> tuple[int, int, int]:
    """Rank key to MINIMISE: smaller free region, then evader mobility, then Cop distance."""
    far = board.grid_size * board.grid_size + 1
    region = free_region(board, evader, cop_after, blocked_after)
    mobility = _mobility(board, evader, blocked_after)
    distance = step_distances(board, cop_after, blocked_after).get(evader, far)
    return (region, mobility, distance)


def _move_options(
    board: Board, cop: Coordinate, believed: Coordinate, blocked: frozenset[Coordinate]
):
    """Yield (score, tie_order, MoveIntent) for every legal Cop move."""
    for action in legal_moves(board, cop, blocked):
        landing = apply_move(board, cop, action, blocked)
        score = _CAPTURE if landing == believed else _score(board, believed, landing, blocked)
        yield score, _ACTIONS.index(action), MoveIntent(action)


def _barrier_options(board: Board, cop: Coordinate, believed: Coordinate, barriers: BarrierField):
    """Yield (score, tie_order, BarrierIntent) for every legal, reserve-permitted barrier.

    Candidates are the Cop's own cell and its orthogonal neighbours; `place_adjacent` is the
    legality authority, so an off-board or duplicate placement simply raises and is skipped.
    """
    if barriers.remaining <= CONTAIN_RESERVE:
        return
    reach = [cop, *(apply_move(board, cop, action, barriers.cells)
                    for action in legal_moves(board, cop, barriers.cells)
                    if action is not Action.STAY)]
    for order, cell in enumerate(dict.fromkeys(reach)):
        try:
            after = barriers.place_adjacent(board, cop, cell)
        except BarrierError:
            continue
        score = _CAPTURE if cell == believed else _score(board, believed, cop, after.cells)
        yield score, order, BarrierIntent(cell)


def _best_contain(
    board: Board, cop: Coordinate, believed: Coordinate, barriers: BarrierField
) -> TurnIntent | None:
    """Return the region-minimising legal action, moves and barriers ranked together."""
    options = [*_move_options(board, cop, believed, barriers.cells),
               *_barrier_options(board, cop, believed, barriers)]
    if not options:
        return None
    return min(options, key=lambda option: (option[0], option[1]))[2]


def contain_turn_intent(
    board: Board,
    cop: Coordinate,
    believed: Coordinate,
    barriers: BarrierField,
    previous: Coordinate | None = None,
) -> TurnIntent:
    """The containment stack: finish, preserve denial's walls, else herd, else fall back."""
    blocked = barriers.cells
    finish = shrinking_turn_intent(board, cop, believed, barriers, previous)
    if isinstance(finish, BarrierIntent) or apply_move(board, cop, finish.action, blocked) == believed:
        return finish
    # Preserve denial's proven barrier plays (the sanctuary/orbit cut that beats
    # flee_interior); containment only ever replaces a bare developing chase.
    incumbent = denial_turn_intent(board, cop, believed, barriers, previous)
    if isinstance(incumbent, BarrierIntent):
        return incumbent
    best = _best_contain(board, cop, believed, barriers)
    return best if best is not None else incumbent
