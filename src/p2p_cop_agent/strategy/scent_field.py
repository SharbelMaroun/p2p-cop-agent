"""The Cop's own accumulated scent trail across the board (M6-09).

`scent.py` gives the one-turn emission shape and the decay formula; this lays them onto
the whole board and keeps the trail between turns. It is the field the opponent reads,
so it is the one thing about us we cannot lie about.

**Emission is involuntary, by construction (M6-09a, M6-09c).** The book is explicit
(`inst/police_thief_p2p_Summary.md:895`): the scent "is emitted by the **movement or the
stay itself**, and no agent can plant a misleading trail -- each side emits its own
scent, and each side reads the scent field of its opponent only." And `:917`: "Every
time an agent moves or remains in its location, a scent field is created around its
location."

So :meth:`ScentField.advance` takes a **cell**, never an action, and carries no
suppression flag. A `STAY` lands on the same cell and emits again, at the full centre
intensity; there is no branch that can skip it, because there is no parameter that could
select one. A Thief cannot hide by standing still, and neither can we.

**Order is the book's, not the reference's.** The book's update is decay-then-add --
``τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ)`` (`:1038`) -- whereas the reference deposits first
and decays the whole field afterwards, which yields ``(τ + Δτ)·(1-ρ)`` and quietly
attenuates the fresh deposit. The book governs on rules (`C-009`, `ADR-005`), so a cell
just stepped on reads the full centre intensity here, exactly as `:1017`'s worked example
expects when it predicts ``0.9 * (1 - 0.1) = 0.81`` for a **one-turn-old** trail.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.scent import (
    DECAY_RATE,
    DEFAULT_OUTER_RING_DELTA,
    FIELD_SIZE,
    decay,
    emission_offsets,
)

Cell = tuple[int, int]

# Below this a cell is treated as silent and dropped, so a decayed trail does not grow
# an unbounded tail of 1e-17 values through the log and the wire. Well under the
# smallest emission the book names (0.04).
SILENCE_FLOOR = 1e-6


@dataclass(slots=True)
class ScentField:
    """This peer's own trail: cell -> intensity, advanced once per full turn.

    Cells are absolute board coordinates. A cell not present is silent (0.0) rather than
    absent-meaning-unknown -- the book calls an empty cell "an absence of information,
    never a negative one".
    """

    board: Board
    outer_ring: float = DEFAULT_OUTER_RING_DELTA
    decay_rate: float = DECAY_RATE
    intensities: dict[Cell, float] = field(default_factory=dict)

    def intensity(self, cell: Cell) -> float:
        """Return the trail strength at ``cell`` (0.0 where nothing was deposited)."""
        return self.intensities.get(cell, 0.0)

    def advance(self, occupied: Coordinate) -> None:
        """Decay the whole board one turn, then emit around ``occupied`` (M6-09a).

        Takes the agent's **cell**, never its action, and has no flag that could skip
        the emission -- so a `STAY`, a move, and a barrier placement all deposit
        identically. Suppression is not refused here; it is unrepresentable.

        Runs once per **full** turn, after both sides have acted, never per half-turn.
        """
        self.board.require_on_board(occupied)
        emitted = emission_offsets(self.outer_ring)
        centre = (occupied.row, occupied.col)
        cells = set(self.intensities) | {
            (centre[0] + d_row, centre[1] + d_col) for d_row, d_col in emitted
        }
        advanced: dict[Cell, float] = {}
        for cell in cells:
            if not self._on_board(cell):
                continue  # the board is the world; scent does not spill off it
            offset = (cell[0] - centre[0], cell[1] - centre[1])
            value = decay(
                self.intensity(cell), emitted.get(offset, 0.0), rho=self.decay_rate
            )
            if value > SILENCE_FLOOR:
                advanced[cell] = value
        self.intensities = advanced

    def snapshot(self) -> dict[Cell, float]:
        """The whole accumulated trail -- **what actually goes on the wire** (`C-052`).

        The reference transmits its persistent field, not a slice of it: `Trail.full_turn`
        merges this turn's stamp into `self.field` and decays it in place, and `snapshot`
        returns "only cells that still carry something", up to the whole board. Verified in
        `sparring/rules/scent.py` and `sparring/turnloop.py`, which sends
        ``smell_grid=self.engine.trail.full_turn(self.engine.position)``. `smell_grid_size`
        parameterises the **emission kernel** (`Trail(..., field_size=cfg.smell_grid_size)`),
        not the size of the transmitted dict.

        **We transmitted a 5x5 window until 2026-08-15, and that was the deviation.** Group
        `yanell11` pointed at the reference source rather than arguing it. Two costs, both
        ours: it departs from the Option-B profile we adopted, and it is *harder for an
        opponent to invert than what the reference sends*, so we were handicapping their
        belief as well as failing to conform. Measured on our own decoder against a
        reference-generated trail: **16/16 turns localised from the trail, 12/16 from the
        window** -- a window is 25 cells, the `C-048` clamp saturates half of them, and ~12
        surviving constraints is too few. A trail carries 46.
        """
        return dict(self.intensities)

    def window(self, centre: Coordinate, size: int = FIELD_SIZE) -> dict[Cell, float]:
        """Return the ``size``×``size`` view of the trail around ``centre``.

        A local view for the GUI and for callers that want one; **not** the wire shape --
        see :meth:`snapshot`, which is. Cells inside the window but off the board are
        omitted; there is no such place.
        """
        half = size // 2
        return {
            (row, col): self.intensity((row, col))
            for row in range(centre.row - half, centre.row + half + 1)
            for col in range(centre.col - half, centre.col + half + 1)
            if self._on_board((row, col))
        }

    def _on_board(self, cell: Cell) -> bool:
        return (
            self.board.min_index <= cell[0] <= self.board.max_index
            and self.board.min_index <= cell[1] <= self.board.max_index
        )
