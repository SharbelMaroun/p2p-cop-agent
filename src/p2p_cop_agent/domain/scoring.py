"""Fixed sub-game scoring and the technical-loss sanction.

Values are read from the negotiated match configuration rather than hard-coded
(``PS-006``). The shared schema pins them to the Appendix F table 17 constants,
so the configuration stays the single source and the schema is the guard.

This module maps an already-decided outcome to points. It does not decide which
outcome occurred, when a tie applies, or who falsified an audit: those belong to
the rules harness, the series layer, and the audit layer respectively.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

_FIELDS = (
    "capture_cop",
    "capture_thief",
    "survival_cop",
    "survival_thief",
    "tie_score",
    "technical_loss",
)


class ScoringError(ValueError):
    """Raised when the configured scoring block is missing or malformed."""


class Outcome(StrEnum):
    """A decided sub-game outcome that maps to a fixed score pair."""

    CAPTURE = "capture"
    SURVIVAL = "survival"
    TIE = "tie"
    TECHNICAL_LOSS = "technical_loss"


@dataclass(frozen=True, slots=True)
class ScoreLine:
    """Points awarded to each role for one decided outcome."""

    cop: int
    thief: int

    def as_pair(self) -> tuple[int, int]:
        """Return the ``(cop, thief)`` pair."""
        return (self.cop, self.thief)


def _require_int(value: object, name: str) -> int:
    """Return a validated integer field, rejecting booleans and non-integers."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ScoringError(f"{name} must be an integer, got {value!r}")
    return value


@dataclass(frozen=True, slots=True)
class ScoringTable:
    """An immutable score table taken from the negotiated match configuration."""

    capture_cop: int
    capture_thief: int
    survival_cop: int
    survival_thief: int
    tie_score: int
    technical_loss: int

    @classmethod
    def from_config(cls, game_config: Mapping[str, object]) -> ScoringTable:
        """Build the table from the match config ``scoring`` section."""
        section = game_config.get("scoring")
        if not isinstance(section, Mapping):
            raise ScoringError("game config is missing a scoring object")
        return cls(**{name: _require_int(section.get(name), name) for name in _FIELDS})

    def award(self, outcome: Outcome) -> ScoreLine:
        """Return the score pair for a decided outcome.

        ``TIE`` returns the symmetric tie award. Whether a tie is decided per
        sub-game or only on the aggregated series is a series-layer question and
        is deliberately not fixed here.
        """
        if outcome is Outcome.CAPTURE:
            return ScoreLine(cop=self.capture_cop, thief=self.capture_thief)
        if outcome is Outcome.SURVIVAL:
            return ScoreLine(cop=self.survival_cop, thief=self.survival_thief)
        if outcome is Outcome.TIE:
            return ScoreLine(cop=self.tie_score, thief=self.tie_score)
        if outcome is Outcome.TECHNICAL_LOSS:
            return ScoreLine(cop=self.technical_loss, thief=self.technical_loss)
        raise ScoringError(f"unknown outcome {outcome!r}")

    def technical_loss_award(self) -> int:
        """Return the technical-loss award, which is the same for both peers.

        Chapter 3 table 2 (PDF p. 38) prints the technical-loss row as ``0 | 0``
        and Appendix E rule 48 writes it as "technical loss 0/0", so the sanction
        is symmetric: a technical loss scores zero for the falsifying peer *and*
        its opponent. ``award(Outcome.TECHNICAL_LOSS)`` returns the same value as
        the explicit pair. Closes ``U-026``.
        """
        return self.technical_loss
