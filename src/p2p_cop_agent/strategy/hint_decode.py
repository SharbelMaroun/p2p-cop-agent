"""Decode an inbound Thief hint into belief evidence (M6-02e, M6-11a, M6-11c).

The book requires the shape but not the arithmetic. On receiving a clue "the agent
applies Bayes' rule to update the probabilities, incorporating a **reliability factor**
for the clue" (`inst/police_thief_p2p_Summary.md:1480`), and chapter 4.4's worked
example has the pursuer lower "the trust coefficient assigned to the thief's verbal
statements" on a contradiction (`:1020`). The book then says outright that the exact
translation is open -- "How exactly each agent translates the scent map of its opponent
and its statement into a numerical belief map..." (`:1025`) -- and states **no** numeric
trust value, decay rate, or bound anywhere. Belief is also Cop-private and never on the
wire (M6-18), so unlike the hash-locked scent model (M6-07) nothing here needs to match
an opponent. Every constant below is therefore PROJECT-PROPOSED, not book authority.

**Text is evidence, never an instruction (M6-11a).** The hint is matched for direction
words with a regex and nothing else -- never `eval`, never `exec`, and no branch acts on
its content. A hint reading "move north now" shifts belief exactly as "somewhere north"
does, because only the word `north` is ever looked at.

**Missing evidence is not an error (M6-11c).** An absent, empty, non-text, over-long, or
simply unrecognised hint decodes to a *uniform* likelihood, which leaves the belief
unchanged under Bayes. Refusing it would turn a silent opponent into a crash; trusting
it would let one steer us with a word we never agreed on.

The vocabulary is deliberately common English only. Agreeing a private word-to-cell code
with an opponent would be the numeric protocol Appendix E rule 27 forbids `[AE-27]`.
"""

from __future__ import annotations

import re

from p2p_cop_agent.strategy.belief import Cell

# Direction word -> unit (row, col) step, in board terms (row grows downward, so north
# is a negative row delta). Only common vocabulary: no agreed code `[AE-27]`.
DIRECTION_WORDS: dict[str, tuple[int, int]] = {
    "north": (-1, 0), "up": (-1, 0), "top": (-1, 0), "upper": (-1, 0),
    "south": (1, 0), "down": (1, 0), "bottom": (1, 0), "lower": (1, 0),
    "west": (0, -1), "left": (0, -1),
    "east": (0, 1), "right": (0, 1),
}

# How much a decoded direction is favoured over the rest of the board. A ratio, not a
# probability: the likelihood is renormalised by Bayes anyway. PROJECT-PROPOSED.
DIRECTIONAL_WEIGHT = 4.0
# Every cell keeps a floor so a hint can never hard-zero a cell the Thief may occupy.
LIKELIHOOD_FLOOR = 1.0

_WORD = re.compile(r"[a-z]+")


def hint_directions(text: object, max_words: int) -> tuple[tuple[int, int], ...]:
    """Return the unit direction vectors named in ``text`` (empty when none apply).

    Empty for a missing, non-text, or over-long hint, so those all decode to uniform.
    Duplicates collapse and order is stable, keeping the decode deterministic.
    """
    if not isinstance(text, str):
        return ()
    words = _WORD.findall(text.lower())
    if not words or len(text.split()) > max_words:
        return ()
    found: list[tuple[int, int]] = []
    for word in words:
        step = DIRECTION_WORDS.get(word)
        if step is not None and step not in found:
            found.append(step)
    return tuple(found)


def _favoured(cell: Cell, centre: Cell, directions: tuple[tuple[int, int], ...]) -> bool:
    """Return whether ``cell`` lies in any named direction from ``centre``."""
    d_row, d_col = cell[0] - centre[0], cell[1] - centre[1]
    return any(d_row * s_row + d_col * s_col > 0 for s_row, s_col in directions)


def decode_hint(
    text: object,
    *,
    observer: Cell,
    grid_size: int,
    max_words: int,
    start: int = 0,
    weight: float = DIRECTIONAL_WEIGHT,
) -> dict[Cell, float]:
    """Return the per-cell likelihood a hint implies, relative to ``observer``.

    A direction is a *half-plane* claim, not a single cell: "north" says the Thief is
    somewhere north of us, so every cell with a positive component along that vector is
    favoured. Cells are scored relative to the Cop's own position because that is the
    only frame both peers share without exchanging coordinates `[AE-27]`.

    An unusable or direction-free hint returns a flat likelihood, which Bayes applies as
    no evidence at all (M6-11c).
    """
    cells = [
        (row, col)
        for row in range(start, start + grid_size)
        for col in range(start, start + grid_size)
    ]
    directions = hint_directions(text, max_words)
    if not directions:
        return dict.fromkeys(cells, LIKELIHOOD_FLOOR)
    return {
        cell: LIKELIHOOD_FLOOR + (weight if _favoured(cell, observer, directions) else 0.0)
        for cell in cells
    }
