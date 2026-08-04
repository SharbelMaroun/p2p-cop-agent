"""M6-01: the multiplicative scent field, pinned to the book.

The decay formula and the documented radial values are source-backed (Book Ch. 4,
Appendix F table 16); the two gaps the book leaves -- the 8 intermediate outer-ring
cells (U-030) and the re-emission cap (U-031) -- are asserted as gaps, not guessed.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.strategy.scent import (
    DOCUMENTED_EMISSION,
    decay,
    emission_field,
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


def test_only_the_seventeen_documented_cells_are_defined() -> None:
    """U-030: the 8 intermediate outer-ring cells are undocumented, so absent."""
    assert len(DOCUMENTED_EMISSION) == 17
    for gap in [(2, 1), (2, -1), (-2, 1), (1, 2), (-1, 2), (1, -2)]:
        assert gap not in DOCUMENTED_EMISSION


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
    assert len(field) == 17
