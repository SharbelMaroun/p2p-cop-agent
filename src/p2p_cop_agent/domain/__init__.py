"""Cop domain types: coordinates, board geometry, and action vocabulary."""

from p2p_cop_agent.domain.actions import Action, ActionError
from p2p_cop_agent.domain.board import Board, BoardError
from p2p_cop_agent.domain.coordinates import Coordinate, CoordinateError

__all__ = [
    "Action",
    "ActionError",
    "Board",
    "BoardError",
    "Coordinate",
    "CoordinateError",
]
