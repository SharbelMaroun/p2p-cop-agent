"""Barrier-only containment: denial's movement, kept exactly, with smarter walls (Phase C).

Phase C v1 replaced denial's *chase* with a region-minimising move and cratered captures --
minimising the evader's free region is capture-averse as a movement objective. The lesson:
a containment objective must sit strictly *under* an unchanged capture/chase priority.

So this candidate never changes a move. Its hard contract, asserted by
`test_barrier_containment_invariant`:

    denial returns a MoveIntent  ==>  this returns the identical MoveIntent.

It intervenes on exactly one kind of turn -- the one where denial places a *non-finishing*
(sanctuary) barrier -- and only re-decides the barrier there:

* a finishing capture move, or a trap/squeeze/containment barrier (`shrink`), is returned
  unchanged -- the scoring engine is untouched;
* a denial chase or sanctuary-walk *move* is returned unchanged -- movement is preserved
  exactly, including its tie-breaking;
* on a denial sanctuary barrier, it scores every legal candidate barrier by its effect on
  the evader's future free region and exits, places the best only if that benefit clears a
  positive threshold, and otherwise **reserves the quota** and advances the chase with
  denial's own `interception_move`.

A candidate barrier is never allowed to push the evader further from the Cop (it must not
obstruct our own approach) or to enlarge the evader's region. Strategy proposes; the domain
`place_adjacent` stays the sole legality authority. Deterministic throughout (M6-03d).
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
from p2p_cop_agent.strategy.shrink import interception_move, shrinking_turn_intent

#: Minimum net cells a barrier must remove from the evader's reach+exits to be worth quota.
BARRIER_BENEFIT_THRESHOLD = 2
#: Barriers held back for the finishing stack; containment cuts spend only above this.
LATE_GAME_RESERVE = 2


def free_region(
    board: Board, evader: Coordinate, cop: Coordinate, blocked: frozenset[Coordinate]
) -> int:
    """Count cells the evader reaches strictly before the Cop -- its future free region."""
    far = board.grid_size * board.grid_size + 1
    reach_e = step_distances(board, evader, blocked)
    reach_c = step_distances(board, cop, blocked)
    return sum(1 for cell, de in reach_e.items() if de < reach_c.get(cell, far))


def _mobility(board: Board, cell: Coordinate, blocked: frozenset[Coordinate]) -> int:
    return sum(1 for action in legal_moves(board, cell, blocked) if action is not Action.STAY)


def _benefit(
    board: Board, cop: Coordinate, believed: Coordinate, barriers: BarrierField, cell: Coordinate
) -> int:
    """Net cells a barrier at ``cell`` removes from the evader's reach and exits, or -1.

    Returns -1 -- never placed -- when the wall would push the evader further from the Cop
    (obstruct our own chase path) or otherwise fail to shrink its region: a barrier that
    helps the evader is worse than no barrier.
    """
    blocked = barriers.cells
    after = barriers.place_adjacent(board, cop, cell).cells
    far = board.grid_size * board.grid_size + 1
    if step_distances(board, cop, after).get(believed, far) > \
            step_distances(board, cop, blocked).get(believed, far):
        return -1
    region = free_region(board, believed, cop, blocked) - free_region(board, believed, cop, after)
    exits = _mobility(board, believed, blocked) - _mobility(board, believed, after)
    return region + exits


def _candidate_cells(board: Board, cop: Coordinate, blocked: frozenset[Coordinate]):
    """The Cop's own cell and its legal orthogonal neighbours, row-major, de-duplicated."""
    cells = [cop, *(apply_move(board, cop, action, blocked)
                    for action in legal_moves(board, cop, blocked) if action is not Action.STAY)]
    return list(dict.fromkeys(cells))


def _best_cut(
    board: Board, cop: Coordinate, believed: Coordinate, barriers: BarrierField
) -> tuple[Coordinate, int] | None:
    """Return the highest-benefit legal barrier and its benefit, keeping a late reserve."""
    if barriers.remaining <= LATE_GAME_RESERVE:
        return None
    best: tuple[tuple[int, int, int], Coordinate, int] | None = None
    for cell in _candidate_cells(board, cop, barriers.cells):
        try:
            benefit = _benefit(board, cop, believed, barriers, cell)
        except BarrierError:
            continue
        key = (benefit, -cell.row, -cell.col)  # max benefit, then row-major cell
        if best is None or key > best[0]:
            best = (key, cell, benefit)
    return (best[1], best[2]) if best is not None else None


def contain_barrier_turn_intent(
    board: Board,
    cop: Coordinate,
    believed: Coordinate,
    barriers: BarrierField,
    previous: Coordinate | None = None,
) -> TurnIntent:
    """Denial's exact movement, with denial's sanctuary barrier re-decided as a real cut."""
    blocked = barriers.cells
    finish = shrinking_turn_intent(board, cop, believed, barriers, previous)
    if isinstance(finish, BarrierIntent):
        return finish  # trap / squeeze / containment: the finisher is untouched
    if apply_move(board, cop, finish.action, blocked) == believed:
        return finish  # the free capture move outranks everything
    incumbent = denial_turn_intent(board, cop, believed, barriers, previous)
    if isinstance(incumbent, MoveIntent):
        return incumbent  # INVARIANT: every denial move is preserved exactly
    # Only a denial sanctuary (development) barrier reaches here; re-decide the wall alone.
    cut = _best_cut(board, cop, believed, barriers)
    if cut is not None and cut[1] >= BARRIER_BENEFIT_THRESHOLD:
        return BarrierIntent(cut[0])
    # Reserve the quota and advance the chase with denial's own movement primitive.
    return MoveIntent(interception_move(board, cop, believed, blocked))
