"""Cop domain types: immutable coordinate and action vocabulary."""

from p2p_cop_agent.domain.actions import Action, ActionError
from p2p_cop_agent.domain.coordinates import Coordinate, CoordinateError

__all__ = ["Action", "ActionError", "Coordinate", "CoordinateError"]
