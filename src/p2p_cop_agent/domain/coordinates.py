"""Immutable board coordinate type for the Cop domain.

The type stores and compares positions only. Board size, boundary legality, and
the screen direction of each move belong to later domain work.
"""

from __future__ import annotations

from dataclasses import dataclass

PAIR_LENGTH = 2


class CoordinateError(ValueError):
    """Raised when a coordinate cannot be constructed from the given input."""


def _require_axis(value: object, axis: str) -> int:
    """Return a validated integer axis, rejecting booleans and non-integers."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise CoordinateError(f"{axis} axis must be an integer, got {value!r}")
    return value


@dataclass(frozen=True, slots=True)
class Coordinate:
    """An immutable, hashable grid cell addressed by two integer axes.

    ``row`` and ``col`` map to config-pair indices 0 and 1 respectively, matching
    the order used by ``thief_start`` and ``cop_start`` in the shared config.
    """

    row: int
    col: int

    def __post_init__(self) -> None:
        _require_axis(self.row, "row")
        _require_axis(self.col, "col")

    @classmethod
    def from_pair(cls, pair: object) -> Coordinate:
        """Build a coordinate from a two-element JSON-style ``[a, b]`` list."""
        if not isinstance(pair, (list, tuple)):
            raise CoordinateError(f"coordinate pair must be a list or tuple, got {pair!r}")
        if len(pair) != PAIR_LENGTH:
            raise CoordinateError(
                f"coordinate pair must have {PAIR_LENGTH} items, got {len(pair)}"
            )
        return cls(_require_axis(pair[0], "row"), _require_axis(pair[1], "col"))

    def as_pair(self) -> tuple[int, int]:
        """Return the ``(row, col)`` pair in config order."""
        return (self.row, self.col)
