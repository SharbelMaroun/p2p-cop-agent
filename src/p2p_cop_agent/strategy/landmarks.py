"""Turn our own cell into a natural-language place descriptor (M6-10e).

A hint is a claim about **the sender's own** position. That is not a style choice — it
is what makes the whole deception mechanism testable. Chapter 4.4's case study has the
Thief say "I am moving North" (`inst/police_thief_p2p_Summary.md:1016`), and the pursuer
catches the lie because "the physical evidence (the scent map) contradicts the verbal
claim, **revealing the thief's true location**" (`:1020`). You can only test a claim
against the scent of the peer who made it, so a hint about *the opponent's* position
would be unfalsifiable and therefore pointless.

**It would also be a leak.** A place derived from our belief argmax would publish our
private inference on the wire — precisely what `M6-18` exists to prevent. The reference
agrees by construction: asked directly, its `place` descriptor "is derived from the
negotiated `setting`… **not derived from the belief heatmap**". So `place_for` takes our
*own* cell and never a belief.

**The map area dresses it, and never changes what it means.** `:1584`: "When a location
is defined, hints are generated based on real-world landmarks (e.g., 'near Times
Square'), which makes the verbal layer of the game richer and more suggestive."
`:1585`: "If no specific configuration is set, the system defaults to **generic
landmarks**", and page 51/131 confirms "in the absence of a definition (default empty
= ''), generic bearings are used". So an unset `map_area` is an ordinary supported
configuration, not a gap.

The vocabularies below are our own; only the *mechanism* is taken from the reference,
per `ADR-008`. Every entry is a bare place name so the composed hint stays inside the
15-word limit and carries no digit that `encodes_coordinates` would refuse `[AE-27]`.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate

# Landmarks per agreed map area. Team-authored; the reference's own lists are not copied.
LANDMARKS: dict[str, tuple[str, ...]] = {
    "new york": ("the waterfront", "the museum steps", "the old subway line", "the park gates"),
    "london": ("the river walk", "the market arches", "the clock tower", "the canal path"),
    "paris": ("the cathedral square", "the left bank", "the flower market", "the hill steps"),
}
# Used when no map area is agreed: bearings rather than places (`:1585`, p. 51/131).
GENERIC_BEARINGS: tuple[str, ...] = (
    "the north edge", "the east side", "the south edge", "the west side", "the middle",
)


def map_area(game_config: Mapping[str, object]) -> str:
    """Return the agreed map area, or an empty string when none was negotiated."""
    world = game_config.get("world")
    if isinstance(world, Mapping):
        value = world.get("map_area")
        if isinstance(value, str):
            return value.strip()
    return ""


def vocabulary(area: str) -> tuple[str, ...]:
    """Return the place words for an agreed area, falling back to generic bearings.

    An unknown area name is not an error: a classmate may agree "Haifa" with us, and a
    generic bearing is a truthful, legal hint in any city.
    """
    return LANDMARKS.get(area.strip().lower(), GENERIC_BEARINGS)


def _quadrant(board: Board, cell: Coordinate) -> int:
    """Return a stable index for the region of the board a cell sits in.

    Deliberately coarse. A hint that pinned an exact cell would be a coordinate protocol
    in words, which rule 27 forbids just as firmly as digits.
    """
    span = max(1, board.grid_size)
    row_half = (cell.row - board.min_index) * 2 // span
    col_half = (cell.col - board.min_index) * 2 // span
    return (row_half * 2 + col_half) % 4


def place_for(board: Board, own_cell: Coordinate, game_config: Mapping[str, object]) -> str:
    """Return the place descriptor for a hint about **our own** position (M6-10e).

    Takes ``own_cell``, never a belief and never the opponent's cell — a signature test
    pins that, because the parameter list is what makes the leak impossible rather than
    a convention someone could quietly break.
    """
    board.require_on_board(own_cell)
    words = vocabulary(map_area(game_config))
    return words[_quadrant(board, own_cell) % len(words)]
