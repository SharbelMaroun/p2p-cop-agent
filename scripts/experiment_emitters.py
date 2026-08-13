"""Foreign scent emitters: the same book, read differently by a classmate (M11-01).

Nothing here is a cheat or a malformed peer. Each model is a defensible implementation
of the book's pheromone section, and the differences are exactly the ones the book
leaves room for -- deposit-then-decay versus decay-then-deposit, whether re-emission
clamps at the centre intensity (the open `U-031`), how many decimals go on the wire, and
whether the zero cells of the window are transmitted at all.

`emitter_decoder` assumes *our* answer to every one of those. This module is how we find
out what that assumption costs, and it is the only honest way to measure a decoder that
otherwise grades its own homework.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from p2p_cop_agent.domain.board import Board  # noqa: E402
from p2p_cop_agent.domain.coordinates import Coordinate  # noqa: E402
from p2p_cop_agent.strategy.scent import (  # noqa: E402
    CENTER_INTENSITY,
    DECAY_RATE,
    DEFAULT_OUTER_RING_DELTA,
    FIELD_SIZE,
    emission_offsets,
)
from p2p_cop_agent.strategy.scent_field import ScentField  # noqa: E402

Cell = tuple[int, int]
HALF = FIELD_SIZE // 2


class BaseEmitter:
    """A peer's trail: `advance` after each of its moves, `window` is what it publishes."""

    def __init__(self, board: Board) -> None:
        self.board = board
        self.intensities: dict[Cell, float] = {}

    def _on_board(self, cell: Cell) -> bool:
        return (self.board.min_index <= cell[0] <= self.board.max_index
                and self.board.min_index <= cell[1] <= self.board.max_index)

    def _deposits(self, centre: Coordinate) -> dict[Cell, float]:
        return {(centre.row + dr, centre.col + dc): value
                for (dr, dc), value in emission_offsets(DEFAULT_OUTER_RING_DELTA).items()}

    def advance(self, occupied: Coordinate) -> None:
        raise NotImplementedError

    def window(self, centre: Coordinate) -> dict[Cell, float]:
        """Publish the full clipped window, zero cells included -- the reference shape."""
        return {(r, c): self.intensities.get((r, c), 0.0)
                for r in range(centre.row - HALF, centre.row + HALF + 1)
                for c in range(centre.col - HALF, centre.col + HALF + 1)
                if self._on_board((r, c))}


class ReferenceOrder(BaseEmitter):
    """Deposit first, then decay the whole field: `(tau + delta) * (1 - rho)`."""

    def advance(self, occupied: Coordinate) -> None:
        deposits = self._deposits(occupied)
        cells = set(self.intensities) | set(deposits)
        self.intensities = {
            cell: (self.intensities.get(cell, 0.0) + deposits.get(cell, 0.0))
            * (1.0 - DECAY_RATE)
            for cell in cells if self._on_board(cell)}


class Clamped(BaseEmitter):
    """Decay then deposit, with re-emission clamped at the centre intensity (`U-031`)."""

    def advance(self, occupied: Coordinate) -> None:
        deposits = self._deposits(occupied)
        cells = set(self.intensities) | set(deposits)
        self.intensities = {
            cell: min(CENTER_INTENSITY,
                      self.intensities.get(cell, 0.0) * (1.0 - DECAY_RATE)
                      + deposits.get(cell, 0.0))
            for cell in cells if self._on_board(cell)}


class Saturating(BaseEmitter):
    """Keep the strongest deposit a cell ever held instead of accumulating onto it."""

    def advance(self, occupied: Coordinate) -> None:
        deposits = self._deposits(occupied)
        cells = set(self.intensities) | set(deposits)
        self.intensities = {
            cell: max(self.intensities.get(cell, 0.0) * (1.0 - DECAY_RATE),
                      deposits.get(cell, 0.0))
            for cell in cells if self._on_board(cell)}


class Ours(BaseEmitter):
    """Our own shipped field -- the control arm, and the only one the decoder was built on."""

    def __init__(self, board: Board) -> None:
        super().__init__(board)
        self.field = ScentField(board=board)

    def advance(self, occupied: Coordinate) -> None:
        self.field.advance(occupied)
        self.intensities = dict(self.field.intensities)


class Coarse(Ours):
    """Ours, rounded to two decimals on the wire -- a peer that prints `%.2f`."""

    def window(self, centre: Coordinate) -> dict[Cell, float]:
        return {cell: round(value, 2) for cell, value in super().window(centre).items()}


class Sparse(Ours):
    """Ours, but the silent cells are omitted rather than transmitted as zeros.

    Our parser accepts this (`scent_wire`'s "generous in what we accept"), and geometry
    must *refuse* it -- an omitted zero makes the key set no longer a window.
    """

    def window(self, centre: Coordinate) -> dict[Cell, float]:
        return {cell: value for cell, value in super().window(centre).items() if value > 0.0}


class Flat(BaseEmitter):
    """A peer whose window carries no gradient at all: every cell the same number.

    Degenerate, and the sharpest test there is: the intensities determine nothing, so a
    likelihood decoder can only return the flat prior, while the shape still fixes the
    emitter exactly.
    """

    def advance(self, occupied: Coordinate) -> None:
        self.intensities = dict.fromkeys(
            self._deposits(occupied), CENTER_INTENSITY)


EMITTERS = {"ours": Ours, "reference_order": ReferenceOrder, "clamped": Clamped,
            "saturating": Saturating, "coarse": Coarse, "sparse": Sparse, "flat": Flat}
