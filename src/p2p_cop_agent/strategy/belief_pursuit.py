"""Belief-driven pursuit: aim the deterministic policy at the most-likely cell (M6-03).

M3 gave a deterministic, barrier-aware pursuit toward a *given* target
(`choose_action`, `choose_turn_intent`). M6 supplies that target from **perception**
rather than an oracle: the Cop pursues ``argmax b(s)`` -- the cell its private belief
holds most probable -- never a Thief position it is forbidden to see `[AE-8]`.

The composition preserves every M3 guarantee, because belief only chooses *where* to
aim. The move itself still comes from `choose_action`, which draws candidates from
`legal_moves`, so a misdirected belief can waste a turn but can **never** emit an
illegal action (M6-03b). Both halves are deterministic -- `Belief.most_likely` breaks
ties in row-major order and the pursuit is fixed-order -- so identical observations
yield an identical action (M6-03d).

Distance stays the M3 **barrier-aware** BFS, not the book's straight-line Manhattan:
equal on an open board, but correct around walls, so a wall never looks like a shortcut
(M3-09b). The belief pursuit inherits that rather than regressing to Manhattan.
"""

from __future__ import annotations

from collections.abc import Set as AbstractSet

from p2p_cop_agent.domain import Action, BarrierField, Board, Coordinate
from p2p_cop_agent.strategy.barrier_policy import TurnIntent, choose_turn_intent
from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.pursuit import choose_action

_NO_BARRIERS: frozenset[Coordinate] = frozenset()


def belief_target(belief: Belief) -> Coordinate:
    """Return the most-probable cell as a board coordinate -- the pursuit's aim.

    The belief must be built over the board's index range, so its ``argmax`` cell is a
    valid on-board coordinate; the pursuit then validates it.
    """
    return Coordinate.from_pair(belief.most_likely())


def pursue_belief(
    board: Board,
    cop: Coordinate,
    belief: Belief,
    blocked: AbstractSet[Coordinate] = _NO_BARRIERS,
) -> Action:
    """Return the legal action that best closes on the belief's most-likely cell."""
    return choose_action(board, cop, belief_target(belief), blocked)


def belief_turn_intent(
    board: Board,
    cop: Coordinate,
    belief: Belief,
    barriers: BarrierField,
) -> TurnIntent:
    """Return one legal move-or-barrier intent aimed at the belief's most-likely cell."""
    return choose_turn_intent(board, cop, belief_target(belief), barriers)
