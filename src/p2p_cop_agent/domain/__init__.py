"""Cop domain types: coordinates, board, movement, barriers, capture, actions."""

from p2p_cop_agent.domain.actions import Action, ActionError
from p2p_cop_agent.domain.barriers import BarrierError, BarrierField
from p2p_cop_agent.domain.board import Board, BoardError, validate_start_coordinates
from p2p_cop_agent.domain.capture import (
    CaptureReason,
    capture_reason,
    captured_by_barrier,
    captured_by_cop,
    is_captured,
    is_trapped,
)
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
    "BarrierError",
    "BarrierField",
    "Board",
    "BoardError",
    "CaptureReason",
    "Coordinate",
    "CoordinateError",
    "MovementError",
    "apply_move",
    "capture_reason",
    "captured_by_barrier",
    "captured_by_cop",
    "destination",
    "is_captured",
    "is_legal_move",
    "is_trapped",
    "legal_moves",
    "validate_start_coordinates",
]
