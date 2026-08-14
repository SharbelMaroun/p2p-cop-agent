"""Robust pursuit: re-rank the chase across a plausible set, never touch the finisher.

These pin the safety contract first -- a barrier, a capturing step, an exact
localization, or an absent belief all return the incumbent reply unchanged -- and then
the one behaviour the layer adds: when several cells are plausible, pick the developing
move with the best worst-case (or expected) value across them, chosen only from moves the
incumbent itself proposes for some plausible world.
"""

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, MoveIntent
from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.robust_pursuit import robust_turn_intent

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def _c(row: int, col: int) -> Coordinate:
    return Coordinate(row, col)


def _fixed(intent):
    """A base chooser that always returns the same intent, ignoring its target."""
    return lambda *_args, **_kw: intent


def _table(replies):
    """A base chooser returning a per-believed-cell reply from a lookup table."""
    return lambda _b, _cop, believed, _bar, _prev: replies[(believed.row, believed.col)]


def test_a_barrier_reply_is_returned_untouched() -> None:
    """The finisher's wall is the scoring engine; robustness must never override it."""
    belief = Belief({(3, 5): 0.5, (3, 1): 0.5})
    intent, _ = robust_turn_intent(
        BOARD, _c(3, 3), _c(3, 5), BarrierField(14), None,
        belief=belief, reachable=None, base_chooser=_fixed(BarrierIntent(_c(3, 4))))
    assert intent == BarrierIntent(_c(3, 4))


def test_a_capturing_step_is_returned_untouched() -> None:
    """A move that lands on the believed cell captures -- never trade it for a hedge."""
    belief = Belief({(3, 4): 0.5, (0, 0): 0.5})
    base = _fixed(MoveIntent(Action.EAST))  # (3,3) -> (3,4) == believed
    intent, _ = robust_turn_intent(
        BOARD, _c(3, 3), _c(3, 4), BarrierField(14), None,
        belief=belief, reachable=None, base_chooser=base)
    assert intent == MoveIntent(Action.EAST)


def test_no_belief_degrades_to_the_incumbent() -> None:
    """With no distribution the set is the single argmax, so the base reply stands."""
    base = _fixed(MoveIntent(Action.WEST))
    intent, carry = robust_turn_intent(
        BOARD, _c(3, 3), _c(3, 5), BarrierField(14), None,
        belief=None, reachable=None, base_chooser=base)
    assert intent == MoveIntent(Action.WEST)
    assert carry == frozenset({_c(3, 5)})


def test_an_exact_localization_is_not_diluted() -> None:
    """A belief spiked on one cell is a singleton set -- certainty stays certain."""
    base = _fixed(MoveIntent(Action.WEST))
    intent, _ = robust_turn_intent(
        BOARD, _c(3, 3), _c(3, 5), BarrierField(14), None,
        belief=Belief({(3, 5): 1.0}), reachable=None, base_chooser=base)
    assert intent == MoveIntent(Action.WEST)


def test_worst_case_re_ranks_toward_a_reachable_capture() -> None:
    """Two cells plausible: the move that captures one and stays near the other wins.

    The incumbent's argmax reply here is a deliberately poor WEST (away from both). The
    layer gathers the incumbent's own reply for the other plausible cell -- EAST, which
    lands on it -- and worst-case prefers it, so the chase flips to EAST.
    """
    replies = {(3, 5): MoveIntent(Action.WEST), (3, 4): MoveIntent(Action.EAST)}
    belief = Belief({(3, 5): 0.5, (3, 4): 0.5})
    intent, carry = robust_turn_intent(
        BOARD, _c(3, 3), _c(3, 5), BarrierField(14), None,
        belief=belief, reachable=None, aggregation="worst", base_chooser=_table(replies))
    assert intent == MoveIntent(Action.EAST)
    assert carry == frozenset({_c(3, 5), _c(3, 4)})


def test_expected_and_lcb_aggregations_return_a_legal_move() -> None:
    """The probability-weighted and lower-confidence aggregations both run and pick a move."""
    replies = {(2, 5): MoveIntent(Action.EAST), (5, 2): MoveIntent(Action.SOUTH)}
    belief = Belief({(2, 5): 0.7, (5, 2): 0.3})
    for mode in ("expected", "lcb"):
        intent, _ = robust_turn_intent(
            BOARD, _c(2, 2), _c(2, 5), BarrierField(14), None, belief=belief,
            reachable=None, aggregation=mode, base_chooser=_table(replies))
        assert isinstance(intent, MoveIntent)
        assert intent.action in {Action.EAST, Action.SOUTH}


def test_the_carried_reachable_constrains_the_next_turn() -> None:
    """Feeding the returned set back as `reachable` narrows the plausible set by motion."""
    belief = Belief({(3, 5): 0.5, (3, 1): 0.5})
    base = _fixed(MoveIntent(Action.EAST))
    # First turn seeds both cells; carry them forward from a cop far from both.
    _, carry = robust_turn_intent(
        BOARD, _c(0, 0), _c(3, 5), BarrierField(14), None,
        belief=belief, reachable=None, base_chooser=base)
    assert carry == frozenset({_c(3, 5), _c(3, 1)})
    # Next turn, only cells one step from the carried set survive; (3,1) is far from (3,5).
    peaked = Belief({(3, 6): 0.5, (3, 5): 0.5})
    _, carry2 = robust_turn_intent(
        BOARD, _c(0, 0), _c(3, 6), BarrierField(14), None,
        belief=peaked, reachable=carry, base_chooser=base)
    assert carry2 <= frozenset({_c(3, 6), _c(3, 5), _c(3, 4), _c(2, 5), _c(4, 5)})
