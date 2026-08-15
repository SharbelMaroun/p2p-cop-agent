"""M6-09: the trail is symmetric, involuntary, and cannot be suppressed.

The book at `inst/police_thief_p2p_Summary.md:895` is the specification: the scent "is
emitted by the **movement or the stay itself**, and no agent can plant a misleading
trail -- each side emits its own scent, and each side reads the scent field of its
opponent only."
"""

from __future__ import annotations

from inspect import signature

import pytest

from p2p_cop_agent.domain.board import Board, BoardError
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.scent import CENTER_INTENSITY
from p2p_cop_agent.strategy.scent_field import ScentField

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def _field() -> ScentField:
    return ScentField(board=BOARD)


def test_standing_still_deposits_exactly_as_moving_does() -> None:
    """`M6-09a` / `:917`: "every time an agent moves **or remains in its location**".

    Both peers arrive at (3,3) on turn two -- one by staying, one by stepping across --
    and both leave the same trail behind, because the deposit is a function of the cell
    alone. A `STAY` is not a quieter move; it is the same move onto the same square.
    """
    stayed, moved = _field(), _field()
    stayed.advance(Coordinate(3, 3))
    stayed.advance(Coordinate(3, 3))  # a STAY: the same cell twice
    moved.advance(Coordinate(3, 2))   # arrives from the west
    moved.advance(Coordinate(3, 3))
    # `C-048`: both reach the ceiling rather than climbing past it. The point of the test is
    # unchanged -- a STAY deposits exactly as an arrival does -- and it is now asserted as an
    # equality, which is strictly the stronger claim the docstring was always making.
    assert stayed.intensity((3, 3)) == pytest.approx(CENTER_INTENSITY)
    assert moved.intensity((3, 3)) == pytest.approx(CENTER_INTENSITY)
    assert stayed.intensity((3, 3)) == pytest.approx(moved.intensity((3, 3)))


def test_a_thief_cannot_hide_by_standing_still() -> None:
    """The centre reads full intensity after a STAY, so silence is not invisibility."""
    trail = _field()
    for _ in range(5):
        trail.advance(Coordinate(2, 2))
    assert trail.intensity((2, 2)) >= CENTER_INTENSITY


def test_emission_cannot_be_suppressed_because_it_takes_no_action() -> None:
    """`M6-09c`: suppression is unrepresentable, not merely refused.

    `advance` accepts a cell and nothing else. There is no action, no flag, and no
    provider parameter that a caller could set to skip the deposit.
    """
    params = set(signature(ScentField.advance).parameters) - {"self"}
    assert params == {"occupied"}
    assert not params & {"action", "move", "emit", "suppress", "silent", "enabled"}


def test_every_advance_deposits_no_matter_how_often_it_is_called() -> None:
    trail = _field()
    for step in range(1, 6):
        trail.advance(Coordinate(3, 3))
        assert trail.intensity((3, 3)) > 0.0, f"silent at step {step}"


def test_the_trail_decays_between_turns_where_the_agent_is_not() -> None:
    """A vacated cell fades; that decay is what makes a trail readable and finite."""
    trail = _field()
    trail.advance(Coordinate(3, 3))
    left_behind = trail.intensity((3, 3))
    trail.advance(Coordinate(0, 0))
    assert 0.0 < trail.intensity((3, 3)) < left_behind


def test_a_fresh_deposit_is_not_attenuated_by_its_own_turns_decay() -> None:
    """`C-009`: the book decays *then* adds, so the cell just stepped on reads 0.9."""
    trail = _field()
    trail.advance(Coordinate(3, 3))
    assert trail.intensity((3, 3)) == pytest.approx(CENTER_INTENSITY)


def test_scent_never_spills_off_the_board() -> None:
    trail = _field()
    trail.advance(Coordinate(0, 0))  # a corner: most of the 5x5 window is off-board
    assert all(
        BOARD.min_index <= r <= BOARD.max_index and BOARD.min_index <= c <= BOARD.max_index
        for r, c in trail.intensities
    )


def test_a_faded_trail_is_dropped_rather_than_kept_as_a_dust_of_zeros() -> None:
    trail = _field()
    trail.advance(Coordinate(6, 6))
    for _ in range(200):
        trail.advance(Coordinate(0, 0))
    assert (6, 6) not in trail.intensities


def test_the_window_is_the_five_by_five_view_clipped_to_the_board() -> None:
    trail = _field()
    trail.advance(Coordinate(3, 3))
    assert len(trail.window(Coordinate(3, 3))) == 25
    assert len(trail.window(Coordinate(0, 0))) == 9  # a corner clips to 3x3


def test_the_window_reports_silent_cells_rather_than_omitting_them() -> None:
    """The reference sends a full window, so a receiver sees its whole shape."""
    trail = _field()
    trail.advance(Coordinate(0, 0))
    window = trail.window(Coordinate(5, 5))  # beyond the 5x5 deposited at the corner
    assert len(window) == 16  # clipped to the board, but still complete
    assert set(window.values()) == {0.0}


def test_accumulation_is_bounded_by_the_centre_intensity() -> None:
    """`U-031` CLOSED by `C-048`: the ceiling is `0.9`, not the fixed point.

    This asserted `CENTER_INTENSITY < intensity <= 9.0` until 2026-08-15 -- the fixed point
    of the uncapped recurrence `t = (1-p)t + 0.9`. Nine times the intensity the book
    declares tau can hold, published on the wire every turn, and the docstring called it
    "what the wire parser must tolerate" rather than treating it as the contradiction it
    was. Group `yanell11` did not tolerate it, and rule 23 backs them.
    """
    trail = _field()
    for _ in range(400):
        trail.advance(Coordinate(3, 3))
    assert trail.intensity((3, 3)) == pytest.approx(CENTER_INTENSITY)


def test_an_off_board_position_is_refused() -> None:
    """A position we cannot occupy is one we cannot have emitted from."""
    with pytest.raises(BoardError):
        _field().advance(Coordinate(9, 9))
