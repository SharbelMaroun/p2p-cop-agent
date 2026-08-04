"""Cop-local belief over the Thief's cell (M6-02).

A board-sized probability distribution the Cop maintains from **observation only** --
the opponent's emitted scent, and later its hints -- never the Thief's true position
`[AE-8]` `[AE-9]`. Belief is Cop-private and never crosses the wire beyond the agreed
observation fields (M6-18), so unlike the scent *model* (agreed and hash-locked
cross-peer, M6-07) the likelihood/trust math here is a **local project decision**, not
a book-fixed, interop-critical value -- there is no opponent to disagree with it.

The update is Bayesian: ``posterior(c) ∝ prior(c)·likelihood(c)``, renormalised. A
zero-evidence update -- an observation that supports no cell at all -- returns the prior
unchanged rather than dividing by zero, so a valid distribution is never destroyed
(M6-02c).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

Cell = tuple[int, int]

DEFAULT_LIKELIHOOD_FLOOR = 0.01


class BeliefError(ValueError):
    """Raised when a belief cannot be constructed."""


@dataclass(frozen=True, slots=True)
class Belief:
    """A normalised probability distribution over board cells (its values sum to 1)."""

    probabilities: Mapping[Cell, float]

    @classmethod
    def uniform(cls, grid_size: int, *, start: int = 0) -> Belief:
        """Return a uniform belief over a ``grid_size``×``grid_size`` board (M6-02a).

        Sized to the negotiated ``grid_size``, never the book's 10×10 illustration.
        """
        if grid_size < 1:
            raise BeliefError(f"grid_size must be positive, got {grid_size}")
        cells = [
            (row, col)
            for row in range(start, start + grid_size)
            for col in range(start, start + grid_size)
        ]
        share = 1.0 / len(cells)
        return cls(dict.fromkeys(cells, share))

    def probability(self, cell: Cell) -> float:
        """Return the belief mass on ``cell`` (0 for a cell off this distribution)."""
        return self.probabilities.get(cell, 0.0)

    def updated(self, likelihood: Mapping[Cell, float]) -> Belief:
        """Return the Bayesian posterior for an observation ``likelihood``, safely.

        ``posterior(c) ∝ prior(c)·likelihood(c)``. If the total evidence is zero, the
        prior is returned unchanged, so a distribution is never invalidated by a
        divide-by-zero (M6-02c). Negative likelihoods are clipped to 0 -- evidence
        cannot be less than absent.
        """
        weighted = {
            cell: prior * max(0.0, likelihood.get(cell, 0.0))
            for cell, prior in self.probabilities.items()
        }
        total = sum(weighted.values())
        if total <= 0.0:
            return self
        return Belief({cell: mass / total for cell, mass in weighted.items()})

    def most_likely(self) -> Cell:
        """Return the argmax cell, ties broken in row-major order (deterministic)."""
        return max(sorted(self.probabilities), key=self.probabilities.__getitem__)


def scent_likelihood(
    observed: Mapping[Cell, float],
    grid_size: int,
    *,
    start: int = 0,
    floor: float = DEFAULT_LIKELIHOOD_FLOOR,
) -> dict[Cell, float]:
    """Map observed opponent scent to a per-cell likelihood over the board.

    Every cell gets a small non-zero ``floor`` so belief never hard-zeros a cell the
    Thief could still occupy; a cell carrying observed scent is boosted by its
    intensity. Input is the *observed* field only -- never the Thief's position -- so
    this cannot leak objective truth into belief (M6-02d). The floor is a local tuning
    choice, since belief is private.
    """
    return {
        (row, col): floor + max(0.0, observed.get((row, col), 0.0))
        for row in range(start, start + grid_size)
        for col in range(start, start + grid_size)
    }
