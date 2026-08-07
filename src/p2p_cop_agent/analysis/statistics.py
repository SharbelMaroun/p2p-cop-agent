"""Summary statistics for the parameter research (`M9-06c`).

`M9-06c` asks for "experiment tables with **run counts**, not anecdotes", and the book is
blunter still: the research must be "based on numbers and not on guesses" (p.142/266). So
every figure this project reports carries the number of runs behind it, and a mean never
appears without its spread.

**The five-number summary is here because §9.3 asks for box plots** — "Box plots for
distributions" — and a box plot is exactly a five-number summary drawn.

**The sign test is here because a mean can lie.** Comparing two strategies by their means
alone hides whether one wins consistently or wins hugely once. The comparison protocol
already pairs the arms — the same seed gives every arm the identical opponent trajectory —
so a paired test is available for free, and paired evidence is much harder to argue with
than two averages that happen to differ.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Summary:
    """A measured quantity, never separated from how many runs produced it."""

    runs: int
    mean: float
    stdev: float
    minimum: float
    q1: float
    median: float
    q3: float
    maximum: float

    @property
    def five_number(self) -> tuple[float, float, float, float, float]:
        """What a box plot draws: min, Q1, median, Q3, max."""
        return (self.minimum, self.q1, self.median, self.q3, self.maximum)

    def as_dict(self) -> dict[str, float | int]:
        return {
            "runs": self.runs, "mean": round(self.mean, 4), "stdev": round(self.stdev, 4),
            "min": round(self.minimum, 4), "q1": round(self.q1, 4),
            "median": round(self.median, 4), "q3": round(self.q3, 4),
            "max": round(self.maximum, 4),
        }


def quantile(values: Sequence[float], fraction: float) -> float:
    """Linear-interpolated quantile.

    Interpolating rather than picking the nearest sample matters at the run counts this
    project uses: with 30 seeds a nearest-rank Q1 jumps in steps of 3.3 percentage points,
    which would make two genuinely different configurations look identical.
    """
    if not values:
        raise ValueError("cannot take a quantile of no values")
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return float(ordered[lower] * (1 - weight) + ordered[upper] * weight)


def summarise(values: Sequence[float]) -> Summary:
    """Reduce measurements to a reportable summary. Refuses an empty sample."""
    if not values:
        raise ValueError("a summary of zero runs would be an anecdote, not a measurement")
    runs = len(values)
    mean = sum(values) / runs
    # Sample standard deviation: these are runs drawn from a process, not a whole
    # population, so the n-1 denominator is the honest one. With a single run there is no
    # spread to report and 0.0 says exactly that.
    variance = sum((value - mean) ** 2 for value in values) / (runs - 1) if runs > 1 else 0.0
    return Summary(
        runs=runs, mean=mean, stdev=sqrt(variance),
        minimum=float(min(values)), q1=quantile(values, 0.25),
        median=quantile(values, 0.5), q3=quantile(values, 0.75),
        maximum=float(max(values)),
    )


@dataclass(frozen=True)
class PairedResult:
    """A per-seed comparison of two arms facing the identical opponent."""

    pairs: int
    wins: int
    losses: int
    ties: int

    @property
    def decisive(self) -> int:
        return self.wins + self.losses

    @property
    def win_share(self) -> float:
        """Share of the *decisive* pairs won. Ties carry no information either way."""
        return self.wins / self.decisive if self.decisive else 0.0

    def as_dict(self) -> dict[str, float | int]:
        return {"pairs": self.pairs, "wins": self.wins, "losses": self.losses,
                "ties": self.ties, "win_share_of_decisive": round(self.win_share, 4)}


def paired_compare(candidate: Sequence[float], baseline: Sequence[float]) -> PairedResult:
    """Compare two arms seed by seed. Refuses unequal arms rather than truncating.

    Equal lengths are load-bearing: the arms are only comparable because seed *i* gave both
    the same opponent trajectory, so silently zipping a short arm against a long one would
    pair unrelated matches and produce a number that looks like evidence.
    """
    if len(candidate) != len(baseline):
        raise ValueError(
            f"{len(candidate)} candidate runs against {len(baseline)} baseline runs; "
            "a paired comparison needs the same seeds on both sides"
        )
    wins = sum(1 for a, b in zip(candidate, baseline, strict=True) if a > b)
    losses = sum(1 for a, b in zip(candidate, baseline, strict=True) if a < b)
    return PairedResult(pairs=len(candidate), wins=wins, losses=losses,
                        ties=len(candidate) - wins - losses)
