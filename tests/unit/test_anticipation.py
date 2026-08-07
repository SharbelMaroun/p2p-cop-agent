"""Predictive pursuit and the combined intent stack (M6-22).

The opponent grid is the motivation on record: every barrier-free arm — the oracle
included — captures a fleeing archetype 0/40, and the stack built here converts the
reference-shaped one 40/40. These tests pin the mechanics that produced that number.
"""

from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.anticipation import (
    anticipating_action,
    flight_cells,
    predictive_turn_intent,
)
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, MoveIntent

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def test_flight_cells_are_the_believed_cell_and_its_legal_exits() -> None:
    cells = flight_cells(BOARD, Coordinate(0, 0))
    assert set(cells) == {Coordinate(0, 0), Coordinate(0, 1), Coordinate(1, 0)}


def test_flight_cells_honour_our_barriers() -> None:
    cells = flight_cells(BOARD, Coordinate(0, 0), frozenset({Coordinate(0, 1)}))
    assert Coordinate(0, 1) not in cells


def test_on_the_open_interior_anticipation_decays_to_pursuit() -> None:
    """A symmetric flight set centres on the believed cell: same aim as plain chase."""
    from p2p_cop_agent.domain.actions import Action

    assert anticipating_action(BOARD, Coordinate(3, 0), Coordinate(3, 5)) is Action.EAST


def test_at_a_wall_anticipation_leads_into_the_open_side() -> None:
    """The believed Thief hugs the top edge; its flight set leans south. A pure chase
    from the west ties north/south by distance — anticipation must break the tie
    toward where the Thief can actually run."""
    cop, believed = Coordinate(2, 0), Coordinate(0, 2)
    chased = anticipating_action(BOARD, cop, believed)
    from p2p_cop_agent.domain.movement import apply_move

    destination = apply_move(BOARD, cop, chased, frozenset())
    assert destination.row <= 2, "closing, not retreating"
    assert destination in (Coordinate(1, 0), Coordinate(2, 1))


def test_the_stack_still_captures_when_adjacent() -> None:
    intent = predictive_turn_intent(
        BOARD, Coordinate(3, 3), Coordinate(3, 4), BarrierField(14))
    assert isinstance(intent, MoveIntent)


def test_the_stack_ratchets_the_vacated_cell_in_a_locked_cyclic_pocket() -> None:
    """Endgame shape: pocket small and still cyclic, we just moved, the vacated cell
    touches it. The stack spends the turn walling behind us instead of orbiting."""
    ladder = BarrierField(14, (Coordinate(1, 1),))
    intent = predictive_turn_intent(
        BOARD, Coordinate(0, 3), Coordinate(0, 0), ladder, Coordinate(0, 2))
    assert intent == BarrierIntent(Coordinate(0, 2))


def test_the_ratchet_never_fires_without_a_vacated_cell() -> None:
    cop, believed = Coordinate(2, 2), Coordinate(0, 0)
    intent = predictive_turn_intent(BOARD, cop, believed, BarrierField(14), None)
    assert isinstance(intent, MoveIntent)


def test_identical_inputs_give_identical_intents() -> None:
    args = (BOARD, Coordinate(5, 5), Coordinate(1, 1), BarrierField(14), Coordinate(5, 6))
    assert predictive_turn_intent(*args) == predictive_turn_intent(*args)
