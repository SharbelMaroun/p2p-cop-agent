"""M6-12: the perception pipeline stays legal and deterministic under every shape.

Exercises scent -> likelihood -> belief -> pursuit (M6-01/02/03) end to end under the
observation extremes the book names: no evidence, a saturated field, a near vs a far
source, and repeated runs. The hint-contradiction case (M6-12b) has its own file,
``test_contradiction.py``, now that the hint model (M6-10/M6-11) exists.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.domain import Action, Board, Coordinate
from p2p_cop_agent.strategy.belief import Belief, scent_likelihood
from p2p_cop_agent.strategy.belief_pursuit import belief_target, pursue_belief

BOARD = Board(7, 0, "top-left")
GRID = 7


def _action(cop: Coordinate, observed: dict[tuple[int, int], float]) -> Action:
    belief = Belief.uniform(GRID).updated(scent_likelihood(observed, GRID))
    return pursue_belief(BOARD, cop, belief)


def test_no_scent_still_yields_a_legal_action() -> None:
    """M6-12a: a uniform belief (no evidence) resolves to a legal action, not an error."""
    assert _action(Coordinate(3, 3), {}) in set(Action)


def test_a_saturated_field_overflows_nothing_and_stays_a_distribution() -> None:
    """M6-12c: every cell at max scent -> valid, normalised belief, no divide-by-zero."""
    saturated = {(r, c): 0.9 for r in range(GRID) for c in range(GRID)}
    belief = Belief.uniform(GRID).updated(scent_likelihood(saturated, GRID))
    assert sum(belief.probabilities.values()) == pytest.approx(1.0)
    assert _action(Coordinate(0, 0), saturated) in set(Action)


def test_a_near_and_a_far_source_give_distinct_sane_choices() -> None:
    """M6-12d: adjacent vs far Thief scent produce different, legal targets."""
    cop = Coordinate(3, 3)
    near = Belief.uniform(GRID).updated(scent_likelihood({(3, 4): 0.9}, GRID))
    far = Belief.uniform(GRID).updated(scent_likelihood({(6, 6): 0.9}, GRID))
    assert belief_target(near) == Coordinate(3, 4)
    assert belief_target(far) == Coordinate(6, 6)
    assert belief_target(near) != belief_target(far)
    assert _action(cop, {(3, 4): 0.9}) in set(Action)
    assert _action(cop, {(6, 6): 0.9}) in set(Action)


def test_repeated_runs_are_byte_identical() -> None:
    """M6-12e: determinism is a submission property, not an accident."""
    cop, observed = Coordinate(1, 2), {(5, 5): 0.9, (5, 4): 0.62}
    assert _action(cop, observed) == _action(cop, observed)
    first = Belief.uniform(GRID).updated(scent_likelihood(observed, GRID))
    second = Belief.uniform(GRID).updated(scent_likelihood(observed, GRID))
    assert first.probabilities == second.probabilities
