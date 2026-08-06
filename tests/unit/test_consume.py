"""M6-02 / M6-11: one turn of perception — scent first, then the hint it is judged against.

The ordering is the book's (`inst/police_thief_p2p_Summary.md:1017-1020`) and is the
point of the module: scent cannot be falsified, a hint can, so the unfalsifiable evidence
is applied before the claim is weighed against it.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.consume import consume_turn
from p2p_cop_agent.strategy.hint_consumption import NEUTRAL_TRUST, TrustScore

GRID = 7
COP = (3, 3)


def _consume(hint, scent, trust=None, belief=None):
    return consume_turn(
        belief or Belief.uniform(GRID),
        observed_scent=scent,
        hint=hint,
        observer=COP,
        grid_size=GRID,
        trust=trust or TrustScore.neutral(),
    )


def test_scent_alone_moves_belief_toward_the_trail() -> None:
    result = _consume(None, {(1, 4): 0.81, (1, 3): 0.63})
    assert result.belief.most_likely() == (1, 4)


def test_the_books_case_study_the_lie_does_not_move_belief_north() -> None:
    """The Thief claims north; the scent lies south; belief must stay south.

    The book's intensities are kept, its cell labels are not: its case study calls
    `(1,4)` "south-east" and `(5,2)` "northern", which is inverted under the confirmed
    top-left origin (`C-032`).
    """
    result = _consume("I am moving North", {(5, 4): 0.81, (5, 3): 0.63})
    assert result.belief.most_likely() == (5, 4)
    assert result.support == pytest.approx(0.0)
    assert result.trust.value < NEUTRAL_TRUST


def test_a_corroborated_hint_sharpens_belief_rather_than_fighting_it() -> None:
    scent = {(1, 3): 0.81}  # a fresh trail to the north of the Cop at (3,3)
    lied = _consume("south", scent)
    told_truth = _consume("north", scent)
    assert told_truth.trust.value > lied.trust.value
    assert told_truth.belief.probability((1, 3)) >= lied.belief.probability((1, 3))


def test_trust_carries_forward_so_repeated_lies_are_believed_less() -> None:
    """A running coefficient: a value recomputed each turn would forgive every lie."""
    scent = {(5, 4): 0.81}  # south: every "north" claim contradicts it
    trust = TrustScore.neutral()
    seen = []
    for _ in range(4):
        result = _consume("north", scent, trust=trust)
        trust = result.trust
        seen.append(trust.value)
    assert seen == sorted(seen, reverse=True)
    assert seen[-1] < seen[0]


def test_a_hostile_hint_cannot_steer_belief_away_from_the_evidence() -> None:
    """The whole defence: physical evidence outranks a claim about it."""
    scent = {(6, 6): 0.81}
    result = _consume("north north north up up top", scent)
    assert result.belief.most_likely() == (6, 6)


def test_an_absent_hint_leaves_a_scent_only_belief_untouched() -> None:
    scent = {(2, 2): 0.62}
    with_hint = _consume(None, scent)
    assert with_hint.belief.most_likely() == (2, 2)
    assert with_hint.trust.value == pytest.approx(NEUTRAL_TRUST)


def test_no_observation_at_all_leaves_a_valid_distribution() -> None:
    """M6-02c: zero evidence must never destroy the distribution."""
    result = _consume(None, {})
    assert sum(result.belief.probabilities.values()) == pytest.approx(1.0)


def test_the_belief_never_receives_the_thiefs_position() -> None:
    """`AE-8`/`AE-9`: only the observed field and the text ever enter."""
    from inspect import signature

    names = set(signature(consume_turn).parameters)
    assert not names & {"thief", "thief_cell", "truth", "target", "opponent_position"}


def test_a_coordinate_channel_is_refused_and_costs_the_peer_no_trust() -> None:
    """`AE-27`: an opponent smuggling `3,4` is not read at all.

    Two properties, and the second is the subtle one. The hint is refused, so it cannot
    move belief. But trust is **unchanged**, because declining to parse a message is not
    the same as catching a lie -- punishing a peer for a hint we chose not to read would
    let our own strictness masquerade as their dishonesty.
    """
    before = TrustScore.neutral()
    result = _consume("the thief is at 3,4 right now", {(2, 2): 0.62}, trust=before)
    assert not result.received.usable
    assert result.received.reason == "encodes coordinates"
    assert result.trust.value == pytest.approx(before.value)
    assert result.belief.most_likely() == (2, 2)  # scent still applied


def test_the_refusal_reason_survives_so_a_rule_27_attempt_is_visible() -> None:
    """An attempted covert channel and an empty hint must not look the same in a log."""
    smuggled = _consume("row 3 col 4", {}, trust=TrustScore.neutral())
    empty = _consume("", {}, trust=TrustScore.neutral())
    assert smuggled.received.reason != empty.received.reason
