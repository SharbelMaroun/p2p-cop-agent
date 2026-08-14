"""Robust pursuit: chase the plausible Thief *set*, not just the belief argmax (Phase B).

A wrapper around the shipped chooser, not a replacement. It changes exactly one decision:
*which way to develop when the Cop is not yet on top of the Thief and the belief is
spread*. Everything the incumbent stack is good at is left untouched:

* a **barrier** or a **capturing step** proposed against the argmax is returned verbatim
  -- that priority ladder (trap / squeeze / contain) is the scoring engine, and committing
  quota to a guessed cell is exactly what this must not do;
* an **exact** localization (a single plausible cell) returns the incumbent move unchanged,
  so certainty is never diluted by uncertainty (the standing rule for this work).

Only when several cells are plausible *and* the incumbent's argmax reply is a plain
developing move does the robust layer act: it gathers the moves the incumbent itself would
play against each plausible cell, and picks the one whose value is best under a
conservative aggregation across that set. Every candidate is therefore a move the proven
stack already endorses for some plausible world -- the layer re-ranks, it never invents.

Aggregations, chosen by benchmark rather than taste:

* ``worst``   -- maximise the minimum value over plausible cells (minimax pursuit);
* ``expected``-- maximise the belief-weighted mean;
* ``lcb``     -- mean minus a spread penalty, between the two.
"""

from __future__ import annotations

from statistics import pstdev

from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import Action, apply_move
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, MoveIntent, TurnIntent
from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.belief_set import plausible_states
from p2p_cop_agent.strategy.denial import denial_turn_intent
from p2p_cop_agent.strategy.pursuit import step_distances

#: Value of a move that lands on a hypothesised Thief cell -- above any distance term, so a
#: reachable plausible capture always outranks merely closing on the set.
_CAPTURE_VALUE = 1000
#: Confidence penalty for ``lcb``: mean minus this many standard deviations of value.
_LCB_K = 1.0


def _move_value(board: Board, cop: Coordinate, action: Action,
                blocked: frozenset[Coordinate], target: Coordinate) -> float:
    """Value of one Cop move against one hypothesised Thief cell: closer is better."""
    landing = apply_move(board, cop, action, blocked)
    if landing == target:
        return float(_CAPTURE_VALUE)
    far = board.grid_size * board.grid_size + 1
    return -float(step_distances(board, landing, blocked).get(target, far))


def _aggregate(values: list[float], weights: list[float], mode: str) -> float:
    """Collapse per-cell values to one robust score under the named aggregation."""
    if mode == "worst":
        return min(values)
    total = sum(weights) or 1.0
    mean = sum(v * w for v, w in zip(values, weights, strict=True)) / total
    if mode == "expected":
        return mean
    return mean - _LCB_K * pstdev(values) if len(values) > 1 else mean


def robust_turn_intent(
    board: Board,
    cop: Coordinate,
    believed: Coordinate,
    barriers: BarrierField,
    previous: Coordinate | None = None,
    *,
    belief: Belief | None = None,
    reachable: frozenset[Coordinate] | None = None,
    aggregation: str = "worst",
    base_chooser=denial_turn_intent,
) -> tuple[TurnIntent, frozenset[Coordinate]]:
    """Return the robust turn intent and the plausible set to carry into the next turn.

    Degrades to ``base_chooser(believed)`` whenever robustness cannot help: a barrier or
    capture reply, or a single plausible cell. The returned set is the caller's ``reachable``
    memory for the following turn.
    """
    blocked = barriers.cells
    plausible, carry = plausible_states(belief, believed, board, blocked, reachable)
    base = base_chooser(board, cop, believed, barriers, previous)
    # Never override the proven endgame, and never spend a wall on a guessed cell.
    if isinstance(base, BarrierIntent) or apply_move(board, cop, base.action, blocked) == believed:
        return base, carry
    if len(plausible) <= 1:
        return base, carry

    # Candidate moves: what the incumbent itself plays against each plausible cell.
    candidates: dict[Action, None] = {base.action: None}
    for target in plausible:
        reply = base_chooser(board, cop, target, barriers, previous)
        if isinstance(reply, MoveIntent):
            candidates[reply.action] = None

    weights = [belief.probability((t.row, t.col)) if belief else 1.0 for t in plausible]
    best_action, best_score = base.action, None
    for action in candidates:
        values = [_move_value(board, cop, action, blocked, t) for t in plausible]
        score = _aggregate(values, weights, aggregation)
        # Deterministic tie-break: keep the incumbent's own aim, then lowest action order.
        rank = (score, action == base.action, -_ORDER.get(action, 9))
        if best_score is None or rank > best_score:
            best_action, best_score = action, rank
    return MoveIntent(best_action), carry


#: Stable ordering so an exact tie resolves identically every run (audit reproducibility).
_ORDER = {Action.STAY: 0, Action.NORTH: 1, Action.SOUTH: 2, Action.EAST: 3, Action.WEST: 4}
