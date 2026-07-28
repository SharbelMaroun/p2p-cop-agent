"""Barrier inventory, placement legality, and disclosure for the Cop domain.

Barriers are placed on board cells up to the negotiated ``max_barriers`` quota
(Appendix F Minimum 14). Every placement is disclosed truthfully: the ordered
``placements`` tuple is the public disclosure log. This module enforces board
legality, uniqueness, and the quota only; the capture effect of a barrier on the
Thief's cell is applied by capture work.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate


class BarrierError(ValueError):
    """Raised for an illegal barrier placement or a malformed barrier field."""


def _require_nonneg_int(value: object, name: str) -> int:
    """Return a validated non-negative integer, rejecting booleans."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise BarrierError(f"{name} must be an integer, got {value!r}")
    if value < 0:
        raise BarrierError(f"{name} must not be negative, got {value}")
    return value


@dataclass(frozen=True, slots=True)
class BarrierField:
    """An immutable, disclosed set of barrier cells bounded by a quota."""

    max_barriers: int
    placements: tuple[Coordinate, ...] = field(default=())

    def __post_init__(self) -> None:
        _require_nonneg_int(self.max_barriers, "max_barriers")
        seen: set[Coordinate] = set()
        for cell in self.placements:
            if not isinstance(cell, Coordinate):
                raise BarrierError(f"barrier placement must be a Coordinate, got {cell!r}")
            if cell in seen:
                raise BarrierError(f"duplicate barrier at {cell.as_pair()}")
            seen.add(cell)
        if len(self.placements) > self.max_barriers:
            raise BarrierError(
                f"barrier count {len(self.placements)} exceeds quota {self.max_barriers}"
            )

    @property
    def count(self) -> int:
        """Return the number of barriers placed so far."""
        return len(self.placements)

    @property
    def remaining(self) -> int:
        """Return how many more barriers may still be placed."""
        return self.max_barriers - self.count

    @property
    def cells(self) -> frozenset[Coordinate]:
        """Return the set of occupied barrier cells for membership tests."""
        return frozenset(self.placements)

    def has_barrier(self, cell: Coordinate) -> bool:
        """Return whether a barrier occupies the given cell."""
        return cell in self.placements

    def place(self, board: Board, cell: Coordinate) -> BarrierField:
        """Return a new field with a disclosed barrier or reject the placement."""
        if not board.contains(cell):
            raise BarrierError(f"barrier at {cell.as_pair()} is outside board bounds")
        if self.has_barrier(cell):
            raise BarrierError(f"barrier already placed at {cell.as_pair()}")
        if self.remaining <= 0:
            raise BarrierError(f"barrier quota {self.max_barriers} is exhausted")
        return BarrierField(self.max_barriers, (*self.placements, cell))

    @classmethod
    def from_config(cls, game_config: Mapping[str, object]) -> BarrierField:
        """Build an empty field with the configured quota from the shared config."""
        section = game_config.get("movement_and_barriers")
        if not isinstance(section, Mapping):
            raise BarrierError("game config is missing a movement_and_barriers object")
        return cls(max_barriers=_require_nonneg_int(section.get("max_barriers"), "max_barriers"))
