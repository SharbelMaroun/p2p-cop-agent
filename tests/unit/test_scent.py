"""M6-01: the multiplicative scent field, pinned to the book.

The decay formula and the documented radial values are source-backed (Book Ch. 4
Figure 4, `inst/police_thief_p2p_Summary.md:947-955`; Appendix F table 16). The two
gaps the book leaves are handled differently from each other on purpose: the 8
intermediate outer-ring cells (U-030) are now a **negotiated** value carried by the
rule-23 lock, while the re-emission cap (U-031) is still an open question and is
asserted as a gap rather than guessed.
"""

from __future__ import annotations

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
    """M6-01c: 0.90 / 0.62 / 0.20 / 0.14 / 0.04, to the documented precision."""
    assert DOCUMENTED_EMISSION[(0, 0)] == pytest.approx(0.90)      # centre
    assert DOCUMENTED_EMISSION[(1, 0)] == pytest.approx(0.62)      # cross
    assert DOCUMENTED_EMISSION[(1, 1)] == pytest.approx(0.20)      # diagonal
    assert DOCUMENTED_EMISSION[(2, 0)] == pytest.approx(0.14)      # mid-side
    assert DOCUMENTED_EMISSION[(2, 2)] == pytest.approx(0.04)      # corner


def test_each_radial_class_is_symmetric() -> None:
    cross = {(-1, 0), (1, 0), (0, -1), (0, 1)}
    corners = {(-2, -2), (-2, 2), (2, -2), (2, 2)}
    assert {DOCUMENTED_EMISSION[c] for c in cross} == {0.62}
    assert {DOCUMENTED_EMISSION[c] for c in corners} == {0.04}


def test_the_book_documents_only_seventeen_of_the_twenty_five_cells() -> None:
    """U-030: the book record stays 17 cells; the ring is never folded into it.

    Keeping the two apart is the point. `DOCUMENTED_EMISSION` is what the source
    *states*; the ring is what the peers *agree*. Merging them would let a negotiated
    number acquire book authority it does not have.
    """
    assert len(DOCUMENTED_EMISSION) == 17
    for gap in OUTER_RING_OFFSETS:
        assert gap not in DOCUMENTED_EMISSION


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
