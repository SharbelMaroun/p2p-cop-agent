"""`observe` turns the opponent's published scent into a belief, or keeps the prior.

Split from `live_policy.py` under `G-04`. These tests exercise the function directly
rather than through a served turn, because the interesting cases are the *refusals* —
the ones where the correct answer is to change nothing — and a whole-turn test cannot
distinguish "kept the prior" from "recomputed the same posterior".
"""

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.orchestration.live_observation import observe
from p2p_cop_agent.protocol.scent_wire import encode_scent
from p2p_cop_agent.strategy.scent_field import ScentField

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def wire_after(*walk: Coordinate) -> dict:
    """The `smell_grid` an opponent would publish after walking `walk`.

    Built from the locked scent model rather than hand-written numbers: a residual is
    only meaningful if both observations come from the same physics the decoder assumes.
    """
    trail = ScentField(board=BOARD)
    for cell in walk:
        trail.advance(cell)
    return encode_scent(trail.window(walk[-1]))


def test_a_first_observation_localises_the_emitter() -> None:
    """One 5x5 stamp is enough to concentrate mass at its centre."""
    fresh = observe(BOARD, {"smell_grid": wire_after(Coordinate(3, 3))}, 1, None)
    assert fresh is not None
    belief, seen = fresh
    assert belief.most_likely() == (3, 3)
    assert seen[0] == 1


def test_the_residual_against_the_previous_turn_tracks_a_moved_emitter() -> None:
    """`M6-24`: the newest stamp is the residual, not the raw peak.

    The stale centre still carries the larger raw value, so a decoder reading intensity
    alone lags a cell behind; only differencing against last turn's observation puts
    the emitter where it now is.
    """
    first = observe(BOARD, {"smell_grid": wire_after(Coordinate(3, 3))}, 1, None)
    assert first is not None
    moved = wire_after(Coordinate(3, 3), Coordinate(3, 4))
    second = observe(BOARD, {"smell_grid": moved}, 2, first[1])
    assert second is not None
    assert second[0].most_likely() == (3, 4)


def test_a_silent_turn_keeps_the_prior() -> None:
    """No observation is not the same as a flat observation."""
    assert observe(BOARD, None, 1, None) is None


def test_a_non_mapping_message_keeps_the_prior() -> None:
    """A malformed turn must not crash the live loop."""
    assert observe(BOARD, "not a message", 1, None) is None  # type: ignore[arg-type]


def test_an_absent_smell_grid_keeps_the_prior() -> None:
    assert observe(BOARD, {"hint": "somewhere"}, 1, None) is None


def test_a_malformed_smell_grid_keeps_the_prior_instead_of_raising() -> None:
    """`ScentWireError` is caught: a bad observation is no observation, not a crash.

    An uncaught raise here reaches the watchdog as a freeze and scores the technical
    0/0 — strictly worse than ignoring one turn of evidence.
    """
    assert observe(BOARD, {"smell_grid": {"not-a-cell": "not-a-number"}}, 1, None) is None


def test_an_empty_smell_grid_keeps_the_prior() -> None:
    assert observe(BOARD, {"smell_grid": {}}, 1, None) is None


def test_a_stale_previous_observation_is_not_differenced_against() -> None:
    """Only turn `n-1` is a valid baseline; an older one would mis-date the residual."""
    first = observe(BOARD, {"smell_grid": {"3,3": 0.9}}, 1, None)
    assert first is not None
    gapped = observe(BOARD, {"smell_grid": {"3,3": 0.9}}, 5, first[1])
    assert gapped is not None
    assert gapped[1][0] == 5


def test_geometry_localises_a_window_whose_values_carry_no_evidence() -> None:
    """`M11-01`: the shape is the fix, and the shape survives physics we do not share.

    Every value here is identical, so the residual explains nothing and the likelihood
    decoder can only return the flat prior — the exact state that had the Cop touring
    waypoints through a counted series. The key set still names the emitter.
    """
    flat = {f"{row},{col}": 0.5
            for row in range(1, 6) for col in range(2, 7)}
    fresh = observe(BOARD, {"smell_grid": flat}, 1, None)
    assert fresh is not None
    assert fresh[0].most_likely() == (3, 4)


def test_a_window_centred_on_our_own_cell_never_aims_at_it() -> None:
    """The Thief cannot stand where we stand — standing there is capture.

    A peer that publishes what it *observes* rather than what it emits sends a window
    centred on us, and both readings would otherwise agree on the one impossible cell.
    Aiming there is the "already on my target, so STAY" freeze by another route.
    """
    ours = Coordinate(3, 3)
    centred_on_us = {f"{row},{col}": 0.5
                     for row in range(1, 6) for col in range(1, 6)}
    fresh = observe(BOARD, {"smell_grid": centred_on_us}, 1, None, ours)
    assert fresh is not None
    assert fresh[0].most_likely() != (3, 3)
    assert fresh[0].probability((3, 3)) == 0.0


def test_the_self_cell_is_the_only_cell_removed() -> None:
    """The rest of the evidence survives the guard; one turn is not thrown away."""
    grid = {"smell_grid": wire_after(Coordinate(2, 5))}
    fresh = observe(BOARD, grid, 1, None, Coordinate(0, 0))
    assert fresh is not None
    assert fresh[0].most_likely() == (2, 5)


def test_the_belief_is_rebuilt_fresh_rather_than_compounded() -> None:
    """Recursion calcified the belief (measured 40/40 -> 0/40), so each call restarts.

    Observing the same field twice must give the same posterior, not a sharper one.
    """
    grid = {"smell_grid": wire_after(Coordinate(1, 1))}
    once = observe(BOARD, grid, 1, None)
    twice = observe(BOARD, grid, 7, None)
    assert once is not None and twice is not None
    assert once[0].probabilities == twice[0].probabilities
