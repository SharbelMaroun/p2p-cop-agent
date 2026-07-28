"""Capture conditions for the Cop domain.

The Final Project Book (authority 1; PDF section 3.4 and the section 3.5 scoring
table) defines three capture conditions:

1. the Cop lands on the Thief's cell (the primary "Capture Claim");
2. the Cop places a barrier on the Thief's current cell;
3. the Thief is trapped: every adjacent cell is blocked by a barrier or lies at
   the edge of the board (off the board).

The book's precise wording of condition 3 settles the STAY question that the
shared-rules paraphrase ("a Thief with no legal move") left open: STAY does not
rescue a Thief whose four cardinal neighbours are all off-board or barriered.
This is a Cop-local rules implementation following the highest authority; it does
not alter the unfrozen shared-contract text.
"""

from __future__ import annotations

from enum import Enum

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import destination

_CARDINAL_DIRECTIONS = (Action.NORTH, Action.SOUTH, Action.EAST, Action.WEST)


class CaptureReason(str, Enum):
    """The book-defined reason a Thief is captured, in checking precedence."""

    COP_ON_THIEF = "cop_on_thief"
    BARRIER_ON_THIEF = "barrier_on_thief"
    THIEF_TRAPPED = "thief_trapped"


def captured_by_cop(cop: Coordinate, thief: Coordinate) -> bool:
    """Return whether the Cop occupies the Thief's cell."""
    return cop == thief


def captured_by_barrier(thief: Coordinate, barriers: BarrierField) -> bool:
    """Return whether a barrier occupies the Thief's current cell."""
    return barriers.has_barrier(thief)


def is_trapped(board: Board, thief: Coordinate, barriers: BarrierField) -> bool:
    """Return whether every cardinal neighbour is off-board or barriered."""
    for action in _CARDINAL_DIRECTIONS:
        neighbour = destination(board, thief, action)
        if board.contains(neighbour) and not barriers.has_barrier(neighbour):
            return False
    return True


def capture_reason(
    board: Board,
    cop: Coordinate,
    thief: Coordinate,
    barriers: BarrierField,
) -> CaptureReason | None:
    """Return the single deterministic capture reason, or None if uncaptured.

    Precedence, when more than one condition holds: cop-on-thief, then
    barrier-on-thief, then trapped.
    """
    if captured_by_cop(cop, thief):
        return CaptureReason.COP_ON_THIEF
    if captured_by_barrier(thief, barriers):
        return CaptureReason.BARRIER_ON_THIEF
    if is_trapped(board, thief, barriers):
        return CaptureReason.THIEF_TRAPPED
    return None


def is_captured(
    board: Board,
    cop: Coordinate,
    thief: Coordinate,
    barriers: BarrierField,
) -> bool:
    """Return whether any book-defined capture condition holds."""
    return capture_reason(board, cop, thief, barriers) is not None
