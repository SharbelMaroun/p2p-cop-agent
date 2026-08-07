"""`M8-07` / `M8-07a` / `M8-07b`: the board, our own cell, and disclosed barriers.

Split from `test_live_view_model.py`, which covers the belief ramp and the turn banner.
The seam is real: those decide what the *inference* looks like, these decide what the
*board* may contain — and `M8-07a` is a rule-15 question rather than a rendering one.
"""

from __future__ import annotations

from p2p_cop_agent.live import TurnState, frame_of, local_truth


def _truth(**overrides):
    base = {"grid_size": 4, "own_position": (0, 0),
            "turn_state": TurnState.YOUR_TURN, "step": 3}
    return local_truth(**{**base, **overrides})


# --- M8-07 / M8-07a: the board ------------------------------------------------------------


def test_the_board_shows_our_own_cell_the_step_and_the_score() -> None:
    frame = frame_of(_truth(step=7, score=15))
    assert frame.at((0, 0)).is_own and frame.at((0, 0)).mark == "C"
    assert frame.status_line == "step 7   ·   score 15"


def test_only_disclosed_barriers_are_drawn() -> None:
    """`M8-07a`, on rule 15: a barrier is public *once declared*. `disclosed_barriers` is
    the snapshot's own input, so an undeclared barrier has no route onto the screen — it is
    not filtered out, it was never there."""
    frame = frame_of(_truth(disclosed_barriers=[(1, 1)]))
    assert frame.at((1, 1)).is_barrier and frame.at((1, 1)).mark == "#"
    assert not frame.at((2, 2)).is_barrier


def test_a_barrier_outranks_the_heat_so_it_cannot_be_hidden_under_colour() -> None:
    """A cell that is both believed and blocked must read as blocked: an operator who
    cannot see a barrier will plan a move into it."""
    frame = frame_of(_truth(disclosed_barriers=[(1, 1)], belief={(1, 1): 0.9}))
    assert frame.at((1, 1)).is_barrier and frame.at((1, 1)).colour == "#263238"


def test_visited_cells_are_marked_without_overriding_anything() -> None:
    frame = frame_of(_truth(visited=[(0, 1), (0, 2)]))
    assert frame.at((0, 1)).is_visited and not frame.at((0, 1)).is_barrier


def test_received_hints_are_shown_as_text() -> None:
    """`M8-07b`: the verbal channel is visible to the operator, bluffs included — a hint
    that never reaches the screen cannot be judged against the map beside it."""
    frame = frame_of(_truth(hints=["I'm near the park", "You'll never catch me"]))
    assert frame.hints == ("I'm near the park", "You'll never catch me")


def test_the_frame_covers_every_cell_of_the_board_exactly_once() -> None:
    frame = frame_of(_truth(grid_size=5))
    assert len(frame.cells) == 25
    assert len({view.cell for view in frame.cells}) == 25
