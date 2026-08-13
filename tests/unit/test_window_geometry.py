"""The geometric localiser: exact on real windows, silent on anything else."""

from __future__ import annotations

import pytest

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.scent_field import ScentField
from p2p_cop_agent.strategy.window_geometry import (
    certainty_likelihood,
    expected_window,
    window_centre,
)

BOARD = Board(7, 0, "top-left")
EVERY_CELL = [(row, col) for row in range(7) for col in range(7)]


@pytest.mark.parametrize("cell", EVERY_CELL)
def test_locates_every_cell_of_a_real_emitted_window(cell: tuple[int, int]) -> None:
    """The window our own shipped emitter transmits localises its emitter exactly."""
    field = ScentField(BOARD)
    field.advance(Coordinate(*cell))
    observed = field.window(Coordinate(*cell))
    assert window_centre(observed, min_index=0, max_index=6) == cell


@pytest.mark.parametrize("cell", EVERY_CELL)
def test_locates_from_keys_alone_when_every_value_is_zero(cell: tuple[int, int]) -> None:
    """A window of honest zeros is no evidence to a likelihood and a fix to geometry.

    This is the case that decided the counted series: the shape carries the position
    even when nothing about the intensities can be read or trusted.
    """
    silent = dict.fromkeys(expected_window(*cell, min_index=0, max_index=6), 0.0)
    assert window_centre(silent, min_index=0, max_index=6) == cell


def test_refuses_a_window_with_its_zero_cells_omitted() -> None:
    """A peer that omits zeros does not describe a window, so no centre is claimed."""
    sparse = {(3, 3): 0.9, (3, 4): 0.62, (2, 3): 0.62}
    assert window_centre(sparse, min_index=0, max_index=6) is None


def test_refuses_a_ragged_grid() -> None:
    """A rectangle missing one interior cell is not a window."""
    ragged = expected_window(3, 3, min_index=0, max_index=6) - {(2, 2)}
    assert window_centre(ragged, min_index=0, max_index=6) is None


def test_refuses_an_empty_grid() -> None:
    assert window_centre({}, min_index=0, max_index=6) is None


def test_refuses_a_window_wider_than_the_board() -> None:
    """Clipped on both sides of an axis, the centre is undetermined -- so say so."""
    whole = {(row, col) for row in range(7) for col in range(7)}
    assert window_centre(whole, min_index=0, max_index=6, half=4) is None


@pytest.mark.parametrize("cell", [(3, 3), (0, 3), (3, 0), (6, 3), (2, 4)])
def test_locates_a_three_by_three_emitter_when_an_axis_reveals_its_size(
    cell: tuple[int, int],
) -> None:
    """A 3x3 peer is located whenever one axis is unclipped and so names the half-width."""
    observed = expected_window(*cell, half=1, min_index=0, max_index=6)
    assert window_centre(observed, min_index=0, max_index=6) == cell


def test_a_doubly_clipped_small_window_reads_as_the_agreed_size() -> None:
    """Ambiguity resolves to the agreed 5x5 model rather than to a guess.

    The 3x3 window centred on (5,1) has exactly the key set of the 5x5 window centred on
    (6,0): clipped on one side of both axes, the shape cannot distinguish them. The
    agreed model is the tie-break, and telling the peer's size takes the `half` argument.
    """
    observed = expected_window(5, 1, half=1, min_index=0, max_index=6)
    assert window_centre(observed, min_index=0, max_index=6) == (6, 0)
    assert window_centre(observed, min_index=0, max_index=6, half=1) == (5, 1)


def test_certainty_likelihood_collapses_a_uniform_prior_onto_the_located_cell() -> None:
    from p2p_cop_agent.strategy.belief import Belief

    belief = Belief.uniform(7).updated(certainty_likelihood((5, 2), grid_size=7))
    assert belief.most_likely() == (5, 2)
    assert belief.probability((5, 2)) == pytest.approx(1.0)
