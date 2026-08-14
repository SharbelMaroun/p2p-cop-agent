"""The plausible-Thief set: motion-constrained belief support, never weaker than argmax.

These pin the two hard filters `belief_set` adds on top of `Belief.most_likely`: a
high-mass support that collapses to a singleton when the decode is certain, and a motion
reachability constraint that narrows a live belief but never empties it.
"""

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.belief_set import (
    belief_from,
    high_probability_cells,
    motion_reachable,
    plausible_states,
)

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def _c(row: int, col: int) -> Coordinate:
    return Coordinate(row, col)


def test_a_dominant_cell_yields_a_singleton_support() -> None:
    """A peaked decode stays certain: one cell covers the mass, so the set is just it."""
    belief = Belief({(3, 3): 0.9, (3, 4): 0.05, (0, 0): 0.05})
    cells = high_probability_cells(belief, _c(3, 3))
    assert cells == (_c(3, 3),)


def test_the_argmax_is_always_included() -> None:
    """Even an argmax outside the high-mass set is appended -- the caller relies on it."""
    belief = Belief({(3, 3): 0.9, (3, 4): 0.1})
    cells = high_probability_cells(belief, _c(6, 6))
    assert _c(3, 3) in cells and _c(6, 6) in cells


def test_the_cap_bounds_the_support() -> None:
    """A flat-ish belief is truncated at the cap rather than returning the whole board."""
    belief = Belief({(0, 0): 0.5, (0, 1): 0.3, (0, 2): 0.15, (0, 3): 0.05})
    cells = high_probability_cells(belief, _c(0, 0), mass_threshold=0.99, cap=2)
    assert cells == (_c(0, 0), _c(0, 1))


def test_motion_reachable_seeds_from_support_on_the_first_turn() -> None:
    """With no prior set the constraint cannot apply, so the raw support passes through."""
    support = (_c(3, 3), _c(0, 0))
    assert motion_reachable(None, BOARD, frozenset(), support) == frozenset(support)


def test_motion_reachable_drops_cells_a_step_cannot_reach() -> None:
    """A support cell not one legal step from the prior set is physically impossible now."""
    reachable = motion_reachable(
        {_c(3, 3)}, BOARD, frozenset(), (_c(3, 3), _c(3, 4), _c(0, 0)))
    assert _c(3, 4) in reachable and _c(3, 3) in reachable
    assert _c(0, 0) not in reachable


def test_motion_reachable_never_empties_a_live_belief() -> None:
    """A contradictory intersection discards stale history rather than zeroing the belief."""
    reachable = motion_reachable({_c(0, 0)}, BOARD, frozenset(), (_c(6, 6),))
    assert reachable == frozenset({_c(6, 6)})


def test_motion_reachable_respects_barriers() -> None:
    """A blocked support cell is unreachable, and a step cannot pass onto a barrier."""
    blocked = frozenset({_c(3, 4)})
    reachable = motion_reachable({_c(3, 3)}, BOARD, blocked, (_c(3, 4), _c(3, 2)))
    assert _c(3, 4) not in reachable
    assert _c(3, 2) in reachable


def test_motion_reachable_skips_a_barriered_prior_cell() -> None:
    """A cell in the prior set that is now walled cannot be a source of new positions."""
    reachable = motion_reachable(
        {_c(3, 3), _c(2, 2)}, BOARD, frozenset({_c(2, 2)}), (_c(3, 4), _c(2, 1)))
    assert _c(3, 4) in reachable  # reachable from the live (3,3)
    assert _c(2, 1) not in reachable  # only reachable from the dead (2,2)


def test_plausible_states_without_a_belief_is_the_single_argmax() -> None:
    """No distribution means exact localization -- the set must not be diluted."""
    plausible, reachable = plausible_states(
        None, _c(2, 2), BOARD, frozenset(), None)
    assert plausible == (_c(2, 2),)
    assert reachable == frozenset({_c(2, 2)})


def test_plausible_states_returns_a_sorted_nonempty_set() -> None:
    """The set is row-major sorted for a deterministic downstream tie-break, and non-empty."""
    belief = Belief({(1, 1): 0.5, (0, 0): 0.5})
    plausible, reachable = plausible_states(
        belief, _c(1, 1), BOARD, frozenset(), None)
    assert plausible == tuple(sorted(plausible, key=lambda c: (c.row, c.col)))
    assert set(plausible) == set(reachable) and plausible


def test_belief_from_adapts_a_raw_map_or_none() -> None:
    assert belief_from(None) is None
    adapted = belief_from({(0, 0): 1.0})
    assert isinstance(adapted, Belief) and adapted.most_likely() == (0, 0)
