"""M6-03: belief-driven pursuit aims the deterministic policy at argmax b(s).

The M3 pursuit already chooses a legal, deterministic, barrier-aware move toward a
target; these prove M6 supplies that target from belief, keeps every move legal even
when belief is wrong, and stays deterministic.
"""

from __future__ import annotations

from p2p_cop_agent.domain import Action, BarrierField, Board, Coordinate
from p2p_cop_agent.strategy.barrier_policy import choose_turn_intent
from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.belief_pursuit import (
    belief_target,
    belief_turn_intent,
    pursue_belief,
)
from p2p_cop_agent.strategy.pursuit import choose_action

BOARD = Board(7, 0, "top-left")


def _belief_at(cell: tuple[int, int]) -> Belief:
    return Belief.uniform(7).updated({cell: 100.0})


def test_belief_target_is_the_argmax_cell() -> None:
    assert belief_target(_belief_at((2, 4))) == Coordinate(2, 4)


def test_pursuit_aims_at_the_belief_peak_through_the_barrier_aware_policy() -> None:
    """M6-03a: the target is argmax b(s); the move is the M3 barrier-aware choice."""
    cop = Coordinate(0, 0)
    belief = _belief_at((0, 6))
    assert pursue_belief(BOARD, cop, belief) == choose_action(BOARD, cop, Coordinate(0, 6))


def test_a_misdirected_belief_still_emits_a_legal_action() -> None:
    """M6-03b: belief may point at an unreachable cell; the move stays legal."""
    cop = Coordinate(0, 0)
    blocked = frozenset({Coordinate(0, 1), Coordinate(1, 0)})  # boxes the corner in
    assert pursue_belief(BOARD, cop, _belief_at((6, 6)), blocked) is Action.STAY


def test_the_policy_is_deterministic() -> None:
    """M6-03d: identical belief and position yield an identical action."""
    cop, belief = Coordinate(1, 1), _belief_at((3, 5))
    assert pursue_belief(BOARD, cop, belief) == pursue_belief(BOARD, cop, belief)


def test_belief_turn_intent_aims_at_the_belief_peak() -> None:
    cop = Coordinate(0, 0)
    belief = _belief_at((0, 6))
    barriers = BarrierField(max_barriers=14)
    assert belief_turn_intent(BOARD, cop, belief, barriers) == choose_turn_intent(
        BOARD, cop, Coordinate(0, 6), barriers
    )
