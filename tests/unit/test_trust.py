"""M6-02b / M6-02f / M6-11b: the reliability factor, and the book's own case study.

Chapter 4.4 (`inst/police_thief_p2p_Summary.md:1007-1022`) is written from the pursuer's
side, so its worked example is reproduced here as a test: the Thief claims north, a
fresh trail of 0.81 lies the other way, the claimed direction measures 0.00, and trust
must fall.

Its *intensities* are the book's; its *cells* are not. The case study labels `(1,4)`
"south-east" and `(5,2)` "northern", which is inverted under the Appendix F top-left
origin where row grows downward — registered as `C-032`. Copying its cell numbers
literally would have pinned an upside-down board into the tests.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.strategy.hint_consumption import NEUTRAL_TRUST, TrustScore
from p2p_cop_agent.strategy.hint_decode import decode_hint
from p2p_cop_agent.strategy.trust import (
    apply_support,
    corroboration,
    expected_fresh_scent,
    trust_weighted,
)

NEUTRAL = TrustScore.neutral()

GRID = 7
CENTRE = (3, 3)


def _claim(text: str):
    return decode_hint(text, observer=CENTRE, grid_size=GRID, max_words=15)


def test_the_expected_fresh_trail_is_the_books_own_arithmetic() -> None:
    """`:1017`: "approximately 0.81 (calculated as 0.9 * (1 - 0.1) = 0.81)"."""
    assert expected_fresh_scent() == pytest.approx(0.81)


def test_the_expected_value_follows_the_locked_model_rather_than_a_literal() -> None:
    """A renegotiated scent model must move this with it, not leave it stale."""
    assert expected_fresh_scent(centre=0.5, decay=0.5) == pytest.approx(0.25)


def test_the_books_case_study_a_claim_with_no_scent_behind_it() -> None:
    """`:1018`: the discrepancy between the expected 0.81 and the measured 0.00.

    The book's intensities are kept (0.81 fresh, 0.63 adjacent, 0.00 where claimed) but
    its *cells* are not: its case study labels `(1,4)` "south-east" and `(5,2)`
    "northern", which is upside down under the Appendix F top-left origin where row
    grows downward (`C-032`). Reproducing the numbers literally would have pinned an
    inverted board, so the scenario is placed by the confirmed convention instead.
    """
    scent = {(5, 4): 0.81, (5, 3): 0.63}  # mass to the south; nothing to the north
    claim = _claim("I am moving North")
    support = corroboration(claim, scent)
    assert support == pytest.approx(0.0)  # "absolute" contradiction
    assert apply_support(NEUTRAL, support).value < NEUTRAL_TRUST  # ":1020" lowers it


def test_a_corroborated_claim_raises_trust() -> None:
    scent = {(0, 3): 0.81, (1, 3): 0.62}  # fresh trail exactly where the hint points
    support = corroboration(_claim("north"), scent)
    assert support == pytest.approx(1.0)
    assert apply_support(NEUTRAL, support).value > NEUTRAL_TRUST


def test_trust_approaches_its_bounds_but_never_reaches_certainty() -> None:
    """`TrustScore`'s bounded step: no peer is ever granted or denied certainty."""
    liar = NEUTRAL
    for _ in range(20):
        liar = apply_support(liar, 0.0)
    assert 0.0 < liar.value < 0.01
    honest = NEUTRAL
    for _ in range(20):
        honest = apply_support(honest, 1.0)
    assert 0.99 < honest.value < 1.0


def test_a_caught_liar_can_rebuild_trust_by_telling_the_truth() -> None:
    """Bluffing is legal, so a liar is doubted, never permanently condemned."""
    burnt = TrustScore(0.02)
    assert apply_support(burnt, 1.0).value > burnt.value


def test_a_marginal_disagreement_moves_trust_less_than_an_absolute_one() -> None:
    """The book's contradiction is "absolute"; a near-miss is not the same event."""
    absolute = NEUTRAL_TRUST - apply_support(NEUTRAL, 0.0).value
    marginal = NEUTRAL_TRUST - apply_support(NEUTRAL, 0.4).value
    assert 0 < marginal < absolute


def test_an_unfalsifiable_hint_leaves_trust_untouched() -> None:
    """A hint naming no direction makes no claim, and silence is not a lie."""
    flat = _claim("lovely evening for it")
    assert corroboration(flat, {(1, 4): 0.81}) == pytest.approx(0.5)
    assert apply_support(NEUTRAL, 0.5).value == pytest.approx(NEUTRAL_TRUST)


def test_full_trust_applies_a_hint_unchanged() -> None:
    claim = _claim("north")
    assert trust_weighted(claim, 1.0) == claim


def test_zero_trust_flattens_a_hint_into_no_evidence() -> None:
    """`:1020`: "the pursuer ignores the verbal claim" -- by arithmetic, not a branch."""
    ignored = trust_weighted(_claim("north"), 0.0)
    assert len(set(ignored.values())) == 1


def test_a_distrusted_hint_is_ignored_never_inverted() -> None:
    """A liar's claim is evidence of nothing, not evidence of the opposite."""
    claim = _claim("north")
    weighted = trust_weighted(claim, 0.1)
    assert weighted[(0, 3)] >= weighted[(6, 3)]


def test_partial_trust_moves_a_hint_partway_toward_flat() -> None:
    claim = _claim("north")
    half = trust_weighted(claim, 0.5)
    spread_full = max(claim.values()) - min(claim.values())
    spread_half = max(half.values()) - min(half.values())
    assert 0 < spread_half < spread_full


def test_an_empty_likelihood_is_handled_without_dividing_by_zero() -> None:
    assert trust_weighted({}, 0.5) == {}


def test_a_scent_model_that_expects_nothing_makes_every_hint_unfalsifiable() -> None:
    """A degenerate negotiated model (centre 0) leaves no trail to test a claim against,
    so no hint can be called a lie and trust must not move."""
    assert corroboration(_claim("north"), {(0, 3): 0.9}, expected=0.0) == pytest.approx(0.5)
