"""M6-02: the Cop-local belief distribution, from observation only.

Belief is Cop-private, so the likelihood math is a local choice; what the book fixes
is that it uses observation only `[AE-8]`, normalises safely, and stays a valid
distribution even with no evidence.
"""

from __future__ import annotations

import inspect

import pytest

from p2p_cop_agent.strategy.belief import Belief, BeliefError, scent_likelihood


def test_a_uniform_belief_is_board_sized_and_sums_to_one() -> None:
    belief = Belief.uniform(7)
    assert len(belief.probabilities) == 49
    assert belief.probability((0, 0)) == pytest.approx(1 / 49)
    assert sum(belief.probabilities.values()) == pytest.approx(1.0)


def test_uniform_refuses_a_nonpositive_board() -> None:
    with pytest.raises(BeliefError):
        Belief.uniform(0)


def test_an_update_concentrates_belief_and_stays_normalised() -> None:
    belief = Belief.uniform(3).updated({(1, 1): 10.0})
    assert belief.most_likely() == (1, 1)
    assert belief.probability((1, 1)) > belief.probability((0, 0))
    assert sum(belief.probabilities.values()) == pytest.approx(1.0)


def test_zero_evidence_leaves_the_distribution_unchanged() -> None:
    """M6-02c: an observation supporting no cell must not divide by zero."""
    prior = Belief.uniform(3)
    assert prior.updated({}) is prior
    assert prior.updated({(0, 0): 0.0, (1, 1): -5.0}) is prior


def test_most_likely_breaks_ties_in_row_major_order() -> None:
    """A uniform belief is all-ties; the deterministic choice is the first cell."""
    assert Belief.uniform(4).most_likely() == (0, 0)


def test_scent_likelihood_floors_unseen_cells_and_boosts_scented_ones() -> None:
    likelihood = scent_likelihood({(2, 2): 0.9}, grid_size=5, floor=0.01)
    assert likelihood[(0, 0)] == pytest.approx(0.01)          # unseen -> floor only
    assert likelihood[(2, 2)] == pytest.approx(0.01 + 0.9)    # scented -> boosted
    assert len(likelihood) == 25


def test_belief_tracks_observed_scent_to_its_source() -> None:
    """End to end: a uniform prior, updated by observed scent, points at the source."""
    belief = Belief.uniform(5).updated(scent_likelihood({(3, 1): 0.9}, grid_size=5))
    assert belief.most_likely() == (3, 1)


def test_belief_input_is_observation_only_never_truth() -> None:
    """M6-02d: the update and likelihood take observation maps, not a Thief cell."""
    assert list(inspect.signature(Belief.updated).parameters) == ["self", "likelihood"]
    truth_words = {"thief", "truth", "position", "target", "actual"}
    for fn in (Belief.updated, scent_likelihood):
        names = " ".join(inspect.signature(fn).parameters)
        assert not (truth_words & set(names.split())), f"{fn.__name__} must take no truth input"
