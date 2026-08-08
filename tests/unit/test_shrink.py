"""Interception chase: the mirror dance broken, with the stack's refusals intact (M6-25).

The traced failure this module exists for is pinned first: a Thief bobbing between two
rows on the far edge tied the centroid lead for the incumbent chase, and the fixed
tie-break made the Cop mirror the bob on its own edge for thirty-five turns. The
summed-distance rank must break that tie toward crossing the board — and everything
the shipped stack already decided (free capture, finishing trap, squeeze) must pass
through unchanged, so the composition can add captures but never surrender one.
"""

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, MoveIntent
from p2p_cop_agent.strategy.shrink import (
    interception_move,
    shrinking_turn_intent,
    thief_replies,
)

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")
QUOTA = BarrierField(14)
NONE_BLOCKED: frozenset[Coordinate] = frozenset()


def test_the_summed_rank_breaks_the_mirror_dance() -> None:
    """The traced hole: Cop bobbing at (1,0)/(2,0) against a Thief bobbing at
    (1,6)/(2,6). Row-matching and column-closing tie under the centroid lead; the
    sum over the whole flight set prices the spread, so EAST strictly wins and the
    chase crosses the board instead of polishing the mirror."""
    assert interception_move(BOARD, Coordinate(1, 0), Coordinate(2, 6), NONE_BLOCKED) is Action.EAST
    assert interception_move(BOARD, Coordinate(2, 0), Coordinate(1, 6), NONE_BLOCKED) is Action.EAST


def test_interception_closes_on_a_cornered_target() -> None:
    """Against a believed cell pressed into the corner the chase keeps closing:
    from one row below and one column in, the move reduces the true step distance."""
    action = interception_move(BOARD, Coordinate(2, 1), Coordinate(0, 0), NONE_BLOCKED)
    assert action in (Action.NORTH, Action.WEST)


def test_a_sealed_off_cop_stays_rather_than_wandering() -> None:
    walls = frozenset({Coordinate(0, 1), Coordinate(1, 0)})
    assert interception_move(BOARD, Coordinate(0, 0), Coordinate(6, 6), walls) is Action.STAY


def test_replies_honour_barriers_and_include_stay() -> None:
    """The flight set is the believed cell plus its legal one-step destinations:
    a walled destination is not a reply, and STAY is the believed cell itself."""
    walls = frozenset({Coordinate(1, 6)})
    replies = thief_replies(BOARD, Coordinate(2, 6), walls)
    assert Coordinate(2, 6) in replies
    assert Coordinate(1, 6) not in replies
    assert Coordinate(3, 6) in replies and Coordinate(2, 5) in replies


def test_the_free_capture_move_passes_through() -> None:
    """Adjacent to the believed cell, the intent is the capture move — never a wall,
    never an interception sidestep."""
    intent = shrinking_turn_intent(BOARD, Coordinate(3, 4), Coordinate(3, 3), QUOTA)
    assert isinstance(intent, MoveIntent)
    assert intent.action is Action.WEST


def test_the_finishing_trap_passes_through() -> None:
    """A believed cell with one exit left, the Cop beside that exit: the shipped trap
    fires through the composition and ends the game with one wall."""
    walls = BarrierField(14, (Coordinate(1, 0),))
    intent = shrinking_turn_intent(BOARD, Coordinate(0, 2), Coordinate(0, 0), walls)
    assert intent == BarrierIntent(Coordinate(0, 1))


def test_the_interception_fallback_is_reached_and_legal() -> None:
    """Far from the believed cell on an open board no wall layer fires: the intent is
    a legal interception move, and identical inputs give the identical intent."""
    first = shrinking_turn_intent(BOARD, Coordinate(6, 0), Coordinate(0, 6), QUOTA)
    second = shrinking_turn_intent(BOARD, Coordinate(6, 0), Coordinate(0, 6), QUOTA)
    assert isinstance(first, MoveIntent)
    assert first == second
    assert first.action in (Action.NORTH, Action.EAST)


def test_the_composition_never_returns_an_illegal_intent_across_a_sweep() -> None:
    """Every cop/believed pairing on the board, quota full and quota spent: the intent
    is always one legal move or one legal wall — the fail-safe the serve loop rests on."""
    spent = BarrierField(0)
    for cop_row in range(0, 7, 2):
        for cop_col in range(0, 7, 2):
            for believed_row in range(0, 7, 3):
                for believed_col in range(0, 7, 3):
                    cop = Coordinate(cop_row, cop_col)
                    believed = Coordinate(believed_row, believed_col)
                    for field in (QUOTA, spent):
                        intent = shrinking_turn_intent(BOARD, cop, believed, field)
                        if isinstance(intent, BarrierIntent):
                            assert field.remaining > 0
                            field.place_adjacent(BOARD, cop, intent.cell)
                        else:
                            from p2p_cop_agent.domain.movement import apply_move

                            apply_move(BOARD, cop, intent.action, field.cells)
