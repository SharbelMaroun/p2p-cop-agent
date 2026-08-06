"""M6-12b: *why* the physical evidence wins, and where a hint still gets to decide.

Split from ``test_contradiction.py``, which asserts what the book requires. This file
records what probing the implementation actually showed — the part no source states and
that a reader would otherwise have to guess at.

The ordering turns out to be **lexicographic**, matching every other policy here
(`M6-04`): scent decides wherever it can, and a claim decides only what scent leaves
open. Both halves need pinning. Without the first, a lie could steer the pursuit; without
the second, the verbal layer would be dead code wearing a strategy's clothes.
"""

from __future__ import annotations

from p2p_cop_agent.domain import Coordinate
from p2p_cop_agent.strategy.belief import Belief, scent_likelihood
from p2p_cop_agent.strategy.belief_pursuit import belief_target
from p2p_cop_agent.strategy.consume import consume_turn
from p2p_cop_agent.strategy.hint_consumption import TrustScore
from p2p_cop_agent.strategy.hint_decode import decode_hint
from p2p_cop_agent.strategy.trust import trust_weighted

GRID = 7
COP = Coordinate(3, 3)
NORTH_SCENT: dict[tuple[int, int], float] = {(0, 0): 0.9, (0, 1): 0.62, (1, 0): 0.62}
THE_LIE = "I am heading south toward the far edge"


def _claim(text: str = THE_LIE) -> dict[tuple[int, int], float]:
    return decode_hint(text, observer=(COP.row, COP.col), grid_size=GRID, max_words=15)


def test_a_wisp_of_scent_still_beats_a_lie_believed_completely() -> None:
    """The dominance is **structural, not a trust effect** — which matters, because it
    means ``test_contradiction.py``'s headline assertions would pass even with the trust
    machinery disabled.

    A located peak concentrates likelihood on one cell; a bearing spreads it across half
    the board. Measured across the range, a `0.04` trace — the faintest value in the
    book's emission table — outweighs this lie held at **complete** trust.

    That does not make those assertions wrong: `:1020`'s case study *is* this regime, an
    absolute contradiction. It makes them incomplete alone, hence the tie-break below.
    """
    for trace in (0.9, 0.2, 0.04):
        belief = Belief.uniform(GRID).updated(scent_likelihood({(0, 0): trace}, GRID))
        assert belief_target(belief.updated(trust_weighted(_claim(), 1.0))) == Coordinate(0, 0)


def test_a_hint_decides_only_what_the_scent_leaves_open() -> None:
    """The other half: two identical peaks, one north of us and one south.

    Scent alone cannot choose between them, and *there* the claim decides — which is the
    whole reason the book gives the game a verbal channel. A hint that could never change
    any decision would be dead code; one that could overrule scent would make the book's
    lie detector pointless. It can do neither.
    """
    tied = Belief.uniform(GRID).updated(scent_likelihood({(0, 3): 0.9, (6, 3): 0.9}, GRID))
    assert belief_target(tied) == Coordinate(0, 3)
    assert belief_target(tied.updated(trust_weighted(_claim(), 1.0))) == Coordinate(6, 3)


def _replay(turns: int) -> list[tuple[float, Coordinate]]:
    """Run ``turns`` turns of the same lie against the same scent, trust running forward."""
    belief, trust, out = Belief.uniform(GRID), TrustScore.neutral(), []
    for _ in range(turns):
        after = consume_turn(
            belief,
            observed_scent=NORTH_SCENT,
            hint=THE_LIE,
            observer=(COP.row, COP.col),
            grid_size=GRID,
            trust=trust,
        )
        belief, trust = after.belief, after.trust
        out.append((trust.value, belief_target(belief)))
    return out


def test_repeated_lying_is_believed_less_each_time() -> None:
    """Trust runs *forward*: the score returned is the next turn's input, so a liar is
    believed less each time. A value recomputed per turn would forgive every lie.

    The book states no such decay — `:508` requires only that trust fall on a
    contradiction, and defines no floor. The schedule is ours.
    """
    scores = [trust for trust, _ in _replay(6)]
    assert scores == sorted(scores, reverse=True)
    assert scores[-1] < scores[0]


def test_a_persistent_liar_never_captures_the_pursuit() -> None:
    """The question repetition actually raises. Trust decays multiplicatively, so it
    approaches zero without reaching it and the lie keeps *some* weight forever; six
    turns accumulate six Bayes multiplications toward the south. Do they ever win?

    They do not. The scent is re-applied every turn as well and, by the first test in
    this file, is the stronger evidence each time whatever trust happens to be — so the
    accumulation never gets a turn unopposed. Asserted rather than assumed, because
    "surely it is fine" is how an accumulating bias survives a review.
    """
    assert all(target == Coordinate(0, 0) for _, target in _replay(6))
