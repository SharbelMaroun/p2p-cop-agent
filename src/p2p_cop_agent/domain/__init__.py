"""Cop domain types: coordinates, board geometry, movement, and actions."""

from p2p_cop_agent.domain.actions import Action, ActionError
from p2p_cop_agent.domain.board import Board, BoardError
from p2p_cop_agent.domain.coordinates import Coordinate, CoordinateError
from p2p_cop_agent.domain.movement import (
    MovementError,
    apply_move,
    destination,
    is_legal_move,
    legal_moves,
)

__all__ = [
    "Action",
    "ActionError",
    "Board",
    "BoardError",
    "Coordinate",
    "CoordinateError",
    "MovementError",
    "apply_move",
    "destination",
    "is_legal_move",
    "legal_moves",
]
