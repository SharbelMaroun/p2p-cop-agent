"""The model-matched emitter decoder, Cop side (M6-24).

The opponent grid carries the motivation: with the decoded belief the live stack
captures 40/40 on every winnable cell, equal to the truth-aimed oracle stack. These
tests pin the properties that equality rests on.
"""

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.emitter_decoder import emitter_likelihood, match_error, residual
from p2p_cop_agent.strategy.scent import emission_offsets
from p2p_cop_agent.strategy.scent_field import ScentField

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def field_after(cells: list[Coordinate]) -> ScentField:
    trail = ScentField(board=BOARD)
    for cell in cells:
        trail.advance(cell)
    return trail


def snapshot(trail: ScentField) -> dict:
    return {(r, c): trail.intensity((r, c))
            for r in range(7) for c in range(7) if trail.intensity((r, c)) > 0}


def argmax(likelihood: dict) -> tuple[int, int]:
    return max(sorted(likelihood), key=likelihood.__getitem__)


def test_the_residual_is_exactly_the_newest_stamp() -> None:
    first = snapshot(field_after([Coordinate(3, 3)]))
    second = snapshot(field_after([Coordinate(3, 3), Coordinate(3, 4)]))
    stamp = emission_offsets()
    delta = residual(second, first)
    for (row, col), value in delta.items():
        assert abs(value - stamp.get((row - 3, col - 4), 0.0)) < 1e-9


def test_the_true_emitter_scores_zero_and_rivals_do_not() -> None:
    first = snapshot(field_after([Coordinate(2, 2)]))
    second = snapshot(field_after([Coordinate(2, 2), Coordinate(2, 3)]))
    delta = residual(second, first)
    assert match_error(delta, (2, 3), grid_size=7) < 1e-12
    for rival in ((2, 2), (2, 4), (1, 3), (0, 0)):
        assert match_error(delta, rival, grid_size=7) > 0.05


def test_the_decoder_tracks_a_walk_with_revisits_exactly() -> None:
    """Revisited cells stack scent and are precisely where raw intensity lags."""
    walk = [Coordinate(3, 3), Coordinate(3, 4), Coordinate(4, 4), Coordinate(4, 3),
            Coordinate(3, 3), Coordinate(3, 3), Coordinate(2, 3)]
    previous = None
    for length in range(1, len(walk) + 1):
        now = snapshot(field_after(walk[:length]))
        likelihood = emitter_likelihood(now, previous, grid_size=7)
        assert argmax(likelihood) == (walk[length - 1].row, walk[length - 1].col)
        previous = now


def test_the_first_observation_alone_is_exact() -> None:
    now = snapshot(field_after([Coordinate(5, 1)]))
    assert argmax(emitter_likelihood(now, None, grid_size=7)) == (5, 1)


def test_a_partial_window_decodes_with_the_trusted_intersection() -> None:
    trail_a = field_after([Coordinate(3, 3)])
    trail_b = field_after([Coordinate(3, 3), Coordinate(3, 4)])
    before = trail_a.window(Coordinate(3, 3))
    now = trail_b.window(Coordinate(3, 4))
    trusted = set(now) & set(before)
    got = argmax(emitter_likelihood(now, before, grid_size=7, trusted=trusted))
    assert got == (3, 4)


def test_an_inexplicable_field_is_no_information_not_a_wrong_answer() -> None:
    nonsense = {(0, 0): 3.0, (6, 6): 2.5, (3, 3): 9.9}
    likelihood = emitter_likelihood(nonsense, None, grid_size=7)
    assert sum(likelihood.values()) > 0.0
    assert len(set(likelihood.values())) == 1


def test_empty_and_identical_inputs_behave() -> None:
    flat = emitter_likelihood({}, None, grid_size=7)
    assert len(set(flat.values())) == 1
    now = snapshot(field_after([Coordinate(1, 5)]))
    assert emitter_likelihood(now, None, grid_size=7) == \
        emitter_likelihood(now, None, grid_size=7)
