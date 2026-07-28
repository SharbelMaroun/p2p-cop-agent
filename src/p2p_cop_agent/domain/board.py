"""Board geometry and boundary validation for the Cop domain.

The board is a square grid with a negotiable origin index and corner. The
Appendix F ``grid_size`` Minimum is a negotiation floor enforced by the shared
contract schema; this geometry type applies only the structural floor of one
cell per axis so it remains usable with any validly negotiated board.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from p2p_cop_agent.domain.coordinates import Coordinate

MIN_GRID_SIZE = 1


class BoardError(ValueError):
    """Raised when board geometry is malformed or a cell is off the board."""


def _require_int(value: object, name: str) -> int:
    """Return a validated integer field, rejecting booleans and non-integers."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise BoardError(f"{name} must be an integer, got {value!r}")
    return value


def _require_corner(value: object) -> str:
    """Return a validated non-empty origin-corner label."""
    if not isinstance(value, str) or not value:
        raise BoardError(f"axis_origin_corner must be a non-empty string, got {value!r}")
    return value


@dataclass(frozen=True, slots=True)
class Board:
    """An immutable square grid addressed by inclusive integer axis indices.

    ``grid_size`` is the number of cells per axis and ``axis_start_index`` is the
    inclusive lowest valid index on each axis. ``axis_origin_corner`` records the
    negotiated corner; its effect on move direction is applied by movement work.
    """

    grid_size: int
    axis_start_index: int
    axis_origin_corner: str

    def __post_init__(self) -> None:
        _require_int(self.grid_size, "grid_size")
        _require_int(self.axis_start_index, "axis_start_index")
        _require_corner(self.axis_origin_corner)
        if self.grid_size < MIN_GRID_SIZE:
            raise BoardError(f"grid_size must be at least {MIN_GRID_SIZE}, got {self.grid_size}")

    @property
    def min_index(self) -> int:
        """Return the inclusive lowest valid index on each axis."""
        return self.axis_start_index

    @property
    def max_index(self) -> int:
        """Return the inclusive highest valid index on each axis."""
        return self.axis_start_index + self.grid_size - 1

    @classmethod
    def from_config(cls, game_config: Mapping[str, object]) -> Board:
        """Build board geometry from the shared config ``board_and_agents`` section."""
        section = game_config.get("board_and_agents")
        if not isinstance(section, Mapping):
            raise BoardError("game config is missing a board_and_agents object")
        return cls(
            grid_size=_require_int(section.get("grid_size"), "grid_size"),
            axis_start_index=_require_int(section.get("axis_start_index"), "axis_start_index"),
            axis_origin_corner=_require_corner(section.get("axis_origin_corner")),
        )

    def contains(self, cell: Coordinate) -> bool:
        """Return whether a coordinate lies within the inclusive board bounds."""
        return (
            self.min_index <= cell.row <= self.max_index
            and self.min_index <= cell.col <= self.max_index
        )

    def require_on_board(self, cell: Coordinate) -> Coordinate:
        """Return the coordinate unchanged or reject an off-board cell."""
        if not self.contains(cell):
            raise BoardError(
                f"{cell.as_pair()} is outside board bounds "
                f"[{self.min_index}, {self.max_index}]"
            )
        return cell


def validate_start_coordinates(
    game_config: Mapping[str, object],
) -> tuple[Coordinate, Coordinate]:
    """Validate configured cop/thief starts against the board and return them.

    Both start cells must parse, lie on the board defined by ``grid_size``,
    ``axis_start_index``, and ``axis_origin_corner``, and be distinct so play does
    not begin in an immediate capture. Returns ``(cop_start, thief_start)``.
    """
    section = game_config.get("board_and_agents")
    if not isinstance(section, Mapping):
        raise BoardError("game config is missing a board_and_agents object")
    board = Board.from_config(game_config)
    cop = board.require_on_board(Coordinate.from_pair(section.get("cop_start")))
    thief = board.require_on_board(Coordinate.from_pair(section.get("thief_start")))
    if cop == thief:
        raise BoardError("cop_start and thief_start must be different cells")
    return cop, thief
