"""Legal orthogonal movement and STAY for the Cop domain.

Compass directions map to index deltas under the natural convention that each
axis increases away from the ``axis_origin_corner``. For the negotiated default
``top-left`` this makes NORTH decrease the row, SOUTH increase it, EAST increase
the column, and WEST decrease it. STAY never changes the cell. Diagonal and
multi-step transitions are not representable: every action moves at most one
cell along a single axis.
"""

from __future__ import annotations

from collections.abc import Set as AbstractSet

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate

_NO_BARRIERS: frozenset[Coordinate] = frozenset()

# Index change for a single SOUTH step and a single EAST step per origin corner.
_SOUTH_STEP = {"top": 1, "bottom": -1}
_EAST_STEP = {"left": 1, "right": -1}


class MovementError(ValueError):
    """Raised for an unsupported origin corner or an illegal transition."""


def _deltas(axis_origin_corner: str) -> dict[Action, tuple[int, int]]:
    """Return the per-action (row, col) delta for one origin corner."""
    try:
        vertical, horizontal = axis_origin_corner.split("-")
        south = _SOUTH_STEP[vertical]
        east = _EAST_STEP[horizontal]
    except (ValueError, KeyError):
        raise MovementError(f"unsupported axis_origin_corner {axis_origin_corner!r}") from None
    return {
        Action.NORTH: (-south, 0),
        Action.SOUTH: (south, 0),
        Action.EAST: (0, east),
        Action.WEST: (0, -east),
        Action.STAY: (0, 0),
    }


def destination(board: Board, cell: Coordinate, action: Action) -> Coordinate:
    """Return the cell reached by one action; it may fall off the board."""
    row_delta, col_delta = _deltas(board.axis_origin_corner)[action]
    return Coordinate(cell.row + row_delta, cell.col + col_delta)


def is_legal_move(
    board: Board,
    cell: Coordinate,
    action: Action,
    blocked: AbstractSet[Coordinate] = _NO_BARRIERS,
) -> bool:
    """Return whether the action reaches a free cell on the board.

    A barrier is impassable for both players, so a directional move onto a
    ``blocked`` cell is illegal. STAY never enters a cell and stays legal while
    the current cell is on the board.
    """
    target = destination(board, cell, action)
    if action is Action.STAY:
        return board.contains(target)
    return board.contains(target) and target not in blocked


def legal_moves(
    board: Board,
    cell: Coordinate,
    blocked: AbstractSet[Coordinate] = _NO_BARRIERS,
) -> tuple[Action, ...]:
    """Return every action that stays on the board and clears barriers."""
    return tuple(action for action in Action if is_legal_move(board, cell, action, blocked))


def apply_move(
    board: Board,
    cell: Coordinate,
    action: Action,
    blocked: AbstractSet[Coordinate] = _NO_BARRIERS,
) -> Coordinate:
    """Return the destination cell or reject an off-board or barriered move."""
    if not is_legal_move(board, cell, action, blocked):
        raise MovementError(f"{action.value} from {cell.as_pair()} is not a legal move")
    return destination(board, cell, action)
