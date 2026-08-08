"""M6-01: the multiplicative scent field, pinned to the book.

The decay formula and the documented radial values are source-backed (Book Ch. 4
Figure 4, `inst/police_thief_p2p_Summary.md:947-955`; Appendix F table 16). The two
gaps the book leaves are handled differently from each other on purpose: the 8
intermediate outer-ring cells (U-030) are now a **negotiated** value carried by the
rule-23 lock, while the re-emission cap (U-031) is still an open question and is
asserted as a gap rather than guessed.
"""

from __future__ import annotations

import math

import pytest

from p2p_cop_agent.strategy.scent import (
    DEFAULT_OUTER_RING_DELTA,
    DOCUMENTED_EMISSION,
    OUTER_RING_OFFSETS,
    ScentModelError,
    decay,
    emission_field,
    emission_offsets,
    require_outer_ring,
)


def test_the_documented_radial_profile_matches_the_book() -> None:
    """M6-01c: 0.90 / 0.62 / 0.42 / 0.20 / 0.04, to the documented precision.

    **Corrected 2026-08-08.** This test pinned 0.20 for the diagonal and 0.14 for the
    mid-side -- the same curve shifted inward one radial class -- and passed for weeks
    because it was pinned to the table it was guarding rather than to the source.
    """
    assert DOCUMENTED_EMISSION[(0, 0)] == pytest.approx(0.90)      # centre
    assert DOCUMENTED_EMISSION[(1, 0)] == pytest.approx(0.62)      # cross
    assert DOCUMENTED_EMISSION[(1, 1)] == pytest.approx(0.42)      # diagonal
    assert DOCUMENTED_EMISSION[(2, 0)] == pytest.approx(0.20)      # mid-side
    assert DOCUMENTED_EMISSION[(2, 2)] == pytest.approx(0.04)      # corner


def test_the_profile_is_the_radial_gaussian_the_caption_describes() -> None:
    """**The check that would have caught the shift**, and it needs no source at all.

    Figure 4's caption says the intensity "decays radially from the center". Fit
    ``0.9*exp(-k*d^2)`` through the two values every reading of the figure agreed on --
    centre 0.90 and cross 0.62 -- and every other class follows with no free parameter.
    The old table failed this at the diagonal (0.20 against 0.427) and the mid-side
    (0.14 against 0.203); nothing in the suite was asking.

    The tolerance is 0.01 because the figure prints two decimals of a continuous curve
    (0.42 for 0.4271, 0.04 for 0.0456). That is still twenty times tighter than the
    error it is guarding: the old diagonal missed by 0.227.
    """
    k = -math.log(0.62 / 0.90)
    for (dr, dc), tau in emission_offsets().items():
        expected = 0.90 * math.exp(-k * (dr * dr + dc * dc))
        assert tau == pytest.approx(expected, abs=0.01), f"cell {(dr, dc)} leaves the curve"


def test_each_radial_class_is_symmetric() -> None:
    cross = {(-1, 0), (1, 0), (0, -1), (0, 1)}
    corners = {(-2, -2), (-2, 2), (2, -2), (2, 2)}
    assert {DOCUMENTED_EMISSION[c] for c in cross} == {0.62}
    assert {DOCUMENTED_EMISSION[c] for c in corners} == {0.04}


def test_the_ring_is_held_separately_from_the_other_seventeen_cells() -> None:
    """`DOCUMENTED_EMISSION` holds 17 cells and the ring is added by `emission_offsets`.

    **The reason for the split changed on 2026-08-08.** It used to be that the book
    named 17 cells and left 8 to negotiation. The book names all 25; the split now only
    keeps the one class a peer may still override addressable on its own.
    """
    assert len(DOCUMENTED_EMISSION) == 17
    for gap in OUTER_RING_OFFSETS:
        assert gap not in DOCUMENTED_EMISSION
    assert len(emission_offsets()) == 25


def test_the_undocumented_ring_is_exactly_the_eight_squared_distance_five_cells() -> None:
    assert len(OUTER_RING_OFFSETS) == 8
    assert {dr * dr + dc * dc for dr, dc in OUTER_RING_OFFSETS} == {5}


def test_the_negotiated_profile_covers_every_cell_of_the_window() -> None:
    """M6-01a: 25 cells, because the reference emits 25 and a gap reads as a zero."""
    profile = emission_offsets()
    assert len(profile) == 25
    assert all(profile[offset] == DEFAULT_OUTER_RING_DELTA for offset in OUTER_RING_OFFSETS)


def test_an_agreed_ring_value_replaces_the_default_everywhere_at_once() -> None:
    profile = emission_offsets(0.07)
    assert {profile[offset] for offset in OUTER_RING_OFFSETS} == {0.07}
    assert profile[(0, 0)] == pytest.approx(0.90)  # book classes are untouched


@pytest.mark.parametrize("bad", [-0.01, 1.0, "0.04", True, None])
def test_a_ring_value_outside_the_model_is_refused(bad: object) -> None:
    """An opponent supplies this value, so it is validated like any other input."""
    with pytest.raises(ScentModelError):
        require_outer_ring(bad)


def test_the_ring_may_legally_be_zero_or_the_centre_intensity() -> None:
    assert require_outer_ring(0.0) == 0.0
    assert require_outer_ring(0.9) == 0.9


def test_decay_is_multiplicative_not_subtractive() -> None:
    """C-009: at rho=0.10 a cell retains 0.90*tau, not tau-0.10."""
    assert decay(0.9) == pytest.approx(0.81)
    assert decay(0.9) != pytest.approx(0.80)  # subtractive would give 0.80


def test_decay_adds_new_emission_without_a_cap() -> None:
    """U-031: the formula accumulates; no 0.9 cap is applied here."""
    assert decay(0.9, 0.9) == pytest.approx(0.81 + 0.9)


def test_a_never_visited_cell_stays_zero_and_is_clipped() -> None:
    assert decay(0.0) == 0.0
    assert decay(0.0, -1.0) == 0.0  # max(0, ...) clips a negative to absence


def test_emission_is_centred_on_the_agent() -> None:
    field = emission_field((3, 4))
    assert field[(3, 4)] == pytest.approx(0.90)
    assert field[(2, 4)] == pytest.approx(0.62)  # one north
    assert field[(1, 2)] == pytest.approx(0.04)  # a corner, two north-west
    assert len(field) == 25


def test_the_emitted_field_carries_the_agreed_ring_not_the_default() -> None:
    field = emission_field((3, 4), outer_ring=0.07)
    assert field[(1, 3)] == pytest.approx(0.07)  # offset (-2,-1), squared distance 5
