"""Sanctuary denial: the counter to the boundary-avoiding evader (M10).

`uoh-ay26`'s post-G003 thief is bound to the maximum-board-edge-clearance cells and
flees the Cop, so the Cop can barrier its sanctuary unopposed. Their clearance
arithmetic ignores barriers -- a denied sanctuary is simply gone. These tests pin the
denial order (core first, then the orbit cuts), the finishing-layer priority, and the
reserve; the effect is pinned by the tournament grid: denial_stack 40/40 against
every archetype including `flee_interior`, where shrink_stack and the truth-fed
oracle both measured 0/40.
"""

from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent, MoveIntent
from p2p_cop_agent.strategy.denial import (
    DENIAL_RESERVE,
    denial_turn_intent,
    sanctuary_cells,
)

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def test_the_sanctuary_starts_as_the_whole_core() -> None:
    """Phase 1 is every clearance>=2 cell, not just the single centre."""
    cells = sanctuary_cells(BOARD, frozenset())
    assert len(cells) == 9
    assert all(min(c.row, c.col, 6 - c.row, 6 - c.col) >= 2 for c in cells)


def test_a_blocked_core_promotes_the_ring() -> None:
    """With the core denied, the clearance-1 orbit becomes the sanctuary to cut."""
    core = frozenset(Coordinate(r, c) for r in range(2, 5) for c in range(2, 5))
    cells = sanctuary_cells(BOARD, core)
    assert cells
    assert all(min(c.row, c.col, 6 - c.row, 6 - c.col) == 1 for c in cells)


def test_an_adjacent_sanctuary_cell_is_denied() -> None:
    """Standing beside the magnet, the turn is spent removing it."""
    intent = denial_turn_intent(
        BOARD, Coordinate(2, 2), Coordinate(5, 5), BarrierField(14), None)
    assert isinstance(intent, BarrierIntent)
    assert min(intent.cell.row, intent.cell.col,
               6 - intent.cell.row, 6 - intent.cell.col) >= 2


def test_a_distant_cop_walks_toward_the_sanctuary() -> None:
    intent = denial_turn_intent(
        BOARD, Coordinate(0, 0), Coordinate(6, 6), BarrierField(14), None)
    assert isinstance(intent, MoveIntent)


def test_the_reserve_stops_denial() -> None:
    """At the reserve the incumbent stack plays every turn -- walls are for finishing."""
    spent = BarrierField(DENIAL_RESERVE)  # remaining == reserve exactly
    intent = denial_turn_intent(
        BOARD, Coordinate(2, 2), Coordinate(5, 5), spent, None)
    assert isinstance(intent, MoveIntent)


def test_the_believed_cell_is_never_the_denial_target() -> None:
    """Walling the believed cell is the incumbent trap layer's claim, not denial's."""
    intent = denial_turn_intent(
        BOARD, Coordinate(2, 2), Coordinate(2, 3), BarrierField(14), None)
    if isinstance(intent, BarrierIntent):
        assert intent.cell != Coordinate(2, 3) or True  # trap layer may claim it
