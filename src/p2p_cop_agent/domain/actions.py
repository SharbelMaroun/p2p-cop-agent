"""Immutable movement-action vocabulary for the Cop domain.

The five tokens are the ``Fixed`` Appendix F move set. This module defines only
the vocabulary and its immutability; which cell a move reaches is deferred to
legal-movement work.
"""

from __future__ import annotations

from enum import Enum


class ActionError(ValueError):
    """Raised when a token is not part of the fixed movement vocabulary."""


class Action(str, Enum):
    """The five fixed legal move tokens; diagonals are never represented."""

    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"
    STAY = "STAY"

    @classmethod
    def from_token(cls, token: object) -> Action:
        """Return the action for an exact wire token or reject unknown input."""
        if not isinstance(token, str):
            raise ActionError(f"movement token must be text, got {token!r}")
        try:
            return cls(token)
        except ValueError:
            raise ActionError(f"unknown movement token {token!r}") from None

    @classmethod
    def tokens(cls) -> tuple[str, ...]:
        """Return the fixed wire tokens in canonical declaration order."""
        return tuple(member.value for member in cls)
