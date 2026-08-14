"""Additive-only containment: denial untouched, extra cuts only where it places none (v5).

Phase C v2 improved both target evaders (flee_smart/flee_deadend 17->20 under perfect
localization) but crashed flee_interior/flee_enclosure, because it *changed* denial's
sanctuary barriers -- the clearance-magnet geometry those wins depend on. v5 keeps that
positive signal and removes the cause by never touching a denial barrier at all.

Strict hierarchy, per current state:

1. Compute denial's complete action.
2. If denial selects a barrier, return that exact barrier -- never replaced, relocated,
   suppressed, delayed, or reserved (rules 3-4).
3. Only when denial selects **no** barrier (it moves) may the candidate add one (rule 5),
   and only as an addition -- otherwise denial's move is returned unchanged (rule 2).

An addition is considered only in the endgame (the Cop within `CLOSE_RANGE` of the evader,
where a range-1 wall can actually cut an exit) and only with a conservative quota reserve
intact, so it cannot consume a barrier denial expects to spend later. It must shrink the
evader's future free region / exits and must not push the evader further from the Cop.
Strategy proposes; `place_adjacent` stays the sole legality authority. Deterministic.
"""

from __future__ import annotations

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierError, BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move, legal_moves
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, TurnIntent
from p2p_cop_agent.strategy.denial import denial_turn_intent
from p2p_cop_agent.strategy.pursuit import step_distances

#: Only add a wall when the Cop is this close -- a range-1 barrier cannot cut a distant exit.
CLOSE_RANGE = 2
#: Net cells an added wall must remove from the evader's reach+exits to be worth a chase step.
ADD_BENEFIT_THRESHOLD = 2
#: Barriers left untouched for denial's own future use -- the conservative quota-safety rule.
QUOTA_RESERVE = 6


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
    """Net cells an added wall at ``cell`` removes from the evader's reach and exits, or -1.

    Returns -1 -- never added -- when the wall would push the evader further from the Cop
    (obstruct the chase) or fail to shrink its region: an addition that helps the evader,
    or merely costs a chase step for nothing, is worse than moving.
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


def _best_addition(
    board: Board, cop: Coordinate, believed: Coordinate, barriers: BarrierField
) -> Coordinate | None:
    """The best legal added wall, or None when quota safety, range, or benefit forbid one."""
    if barriers.remaining <= QUOTA_RESERVE:
        return None  # conservative quota safety: leave denial's future barriers intact
    far = board.grid_size * board.grid_size + 1
    if step_distances(board, cop, barriers.cells).get(believed, far) > CLOSE_RANGE:
        return None  # only the endgame, where a range-1 wall can bite
    cells = [cop, *(apply_move(board, cop, action, barriers.cells)
                    for action in legal_moves(board, cop, barriers.cells)
                    if action is not Action.STAY)]
    best: tuple[tuple[int, int, int], Coordinate] | None = None
    for cell in dict.fromkeys(cells):
        try:
            benefit = _benefit(board, cop, believed, barriers, cell)
        except BarrierError:
            continue
        if benefit < ADD_BENEFIT_THRESHOLD:
            continue
        key = (benefit, -cell.row, -cell.col)
        if best is None or key > best[0]:
            best = (key, cell)
    return best[1] if best is not None else None


def contain_add_turn_intent(
    board: Board,
    cop: Coordinate,
    believed: Coordinate,
    barriers: BarrierField,
    previous: Coordinate | None = None,
) -> TurnIntent:
    """Denial's action verbatim, plus at most an extra wall on a turn denial would move."""
    incumbent = denial_turn_intent(board, cop, believed, barriers, previous)
    if isinstance(incumbent, BarrierIntent):
        return incumbent  # rules 3-4: denial's barrier is never touched
    if apply_move(board, cop, incumbent.action, barriers.cells) == believed:
        return incumbent  # a capturing move is a finish -- never trade it for a wall
    added = _best_addition(board, cop, believed, barriers)
    if added is not None:
        return BarrierIntent(added)  # rule 5: an addition only on a no-barrier (move) turn
    return incumbent  # rule 2: denial's exact move, preserved
