"""M6-27: a Cop with no observation sweeps instead of standing on its start cell.

The uniform prior's row-major tie-break is `(0,0)` — the Cop's own opening square — so
the served stack read "already on target" and answered `STAY` for 26 consecutive turns
of the `amireman` friendly. Moving cannot improve what a Cop *observes* (the window is
the opponent's to transmit), but landing on the Thief is itself the capture condition,
so any coverage strictly dominates standing still.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.patrol import (
    WAYPOINT_HOLD_TURNS,
    needs_sweep,
    sweep_target,
    sweep_waypoints,
)

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def test_the_tour_stays_on_the_board_and_spreads_out() -> None:
    tour = sweep_waypoints(BOARD)
    assert len(tour) >= 4
    assert all(0 <= cell.row <= 6 and 0 <= cell.col <= 6 for cell in tour)
    assert len(set(tour)) == len(tour)  # no waypoint is visited twice in one lap


def test_the_first_waypoint_is_the_centre_not_the_corner() -> None:
    """The defect in one assertion: the blind target must not be the Cop's own start."""
    first = sweep_target(BOARD, 1)
    assert (first.row, first.col) == (3, 3)
    assert (first.row, first.col) != (0, 0)


def test_a_waypoint_is_held_long_enough_to_be_reached() -> None:
    """Re-aiming every turn would leave the Cop oscillating and covering nothing."""
    held = {sweep_target(BOARD, turn) for turn in range(1, WAYPOINT_HOLD_TURNS + 1)}
    assert len(held) == 1
    assert sweep_target(BOARD, WAYPOINT_HOLD_TURNS + 1) != sweep_target(BOARD, 1)


def test_the_sweep_covers_ground_over_a_full_game() -> None:
    """Across the 35-turn horizon the blind Cop visits several distinct regions."""
    visited = {sweep_target(BOARD, turn) for turn in range(1, 36)}
    assert len(visited) >= 4


def test_the_sweep_is_deterministic() -> None:
    """M6-03d: identical turns yield identical targets, so matches stay reproducible."""
    assert [sweep_target(BOARD, t) for t in range(1, 20)] == [
        sweep_target(BOARD, t) for t in range(1, 20)
    ]


@pytest.mark.parametrize("size", [7, 9, 11])
def test_the_tour_scales_to_a_negotiated_board(size: int) -> None:
    board = Board(grid_size=size, axis_start_index=0, axis_origin_corner="top-left")
    tour = sweep_waypoints(board)
    assert all(0 <= cell.row < size and 0 <= cell.col < size for cell in tour)
    assert sweep_target(board, 1) == tour[0]


def test_a_waypoint_the_cop_already_occupies_is_skipped() -> None:
    """"Go where you already are" is STAY — the very bug the sweep exists to fix, and
    the hold would repeat it for a whole waypoint's worth of turns."""
    here = sweep_target(BOARD, 1)
    assert sweep_target(BOARD, 1, here) != here


def test_the_stale_and_flat_cases_both_ask_for_a_sweep() -> None:
    """Three paths produced a flat belief in play; all must reach the sweep."""
    flat = Belief.uniform(7)
    peaked = Belief({(r, c): (1.0 if (r, c) == (5, 5) else 0.0)
                     for r in range(7) for c in range(7)})
    assert needs_sweep(flat, None, 1)          # never observed
    assert needs_sweep(flat, 1, 2)             # observed, but no evidence survived
    assert needs_sweep(peaked, 1, 99)          # localised once, long stale
    assert not needs_sweep(peaked, 5, 6)       # a fresh, real peak is pursued
