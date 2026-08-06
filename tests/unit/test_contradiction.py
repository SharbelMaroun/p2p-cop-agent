"""M6-12b: when a hint contradicts the scent, the physical evidence wins.

Two sentences in the book specify this, and they ask for different things.

**`inst/police_thief_p2p_Summary.md:508`** states the obligation: "If a verbal hint
(e.g., 'I moved north') contradicts the scent map, the agent **must reduce their trust
level and update their map**." Two clauses joined by *and* — lowering trust is not
enough on its own, and neither is moving belief. Both are asserted separately below.

**`:1020`** states the behaviour, and its verb is the precise one: "The pursuer
**ignores** the verbal claim and **continues** to track the actual scent source." Not
*redirects* — **continues**. A lie that merely failed to win would still have deflected
the pursuit a little; the book says the pursuit does not bend at all. So the sharpest
test here is not "the target is near the scent" but
:func:`test_the_lie_does_not_deflect_the_pursuit_at_all`, which pins the target against
the same turn run with **no hint whatsoever**.

*Two things the book does not say,* checked rather than assumed. There is no numbered
Appendix E rule with a sanction behind any of this — `:508` is body text, and the
override falls out of the Bayesian update rather than being decreed. And nothing in the
sources defines a trust floor or an "ignore a liar after N turns" rule. Our clamp to
`[0, 1]` and our multiplicative decay are therefore **engineering, not scripture**, and
no test here claims the book's authority for them.

*Nothing could be copied here.* The reference implementation never applies a hint to
belief at all: it has no trust coefficient, and its hint is logged and displayed but
"never enters the mathematical belief-update pipeline". Its own README describes a
fusion of scent and hints that its code does not perform.

``test_evidence_priority.py`` carries the companion half — *why* scent wins, and the
tie-break where a claim still gets to decide.
"""

from __future__ import annotations

from p2p_cop_agent.domain import Action, Board, Coordinate
from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.belief_pursuit import belief_target, pursue_belief
from p2p_cop_agent.strategy.consume import consume_turn
from p2p_cop_agent.strategy.hint_consumption import NEUTRAL_TRUST, TrustScore

BOARD = Board(7, 0, "top-left")
GRID = 7
COP = Coordinate(3, 3)

# Scent mass in the north-west, exactly the book's shape: a 0.9 centre and its cross.
NORTH_SCENT: dict[tuple[int, int], float] = {(0, 0): 0.9, (0, 1): 0.62, (1, 0): 0.62}
# ...and a hint claiming the opposite pole. Legal to send: rules 16 and 22 forbid lying
# about an obstacle and about a capture, but a positional hint may bluff.
THE_LIE = "I am heading south toward the far edge"
THE_TRUTH = "I am heading north toward the far edge"


def _turn(hint: object, trust: TrustScore, belief: Belief | None = None):
    return consume_turn(
        Belief.uniform(GRID) if belief is None else belief,
        observed_scent=NORTH_SCENT,
        hint=hint,
        observer=(COP.row, COP.col),
        grid_size=GRID,
        trust=trust,
    )


def test_a_hint_the_scent_contradicts_lowers_trust() -> None:
    """`:508`, first clause: the agent *must reduce their trust level*."""
    assert _turn(THE_LIE, TrustScore.neutral()).trust.value < NEUTRAL_TRUST


def test_a_hint_the_scent_corroborates_raises_trust() -> None:
    """The control. Without it the test above would pass on a function that only ever
    punishes — which would not be a lie detector, just a pessimist."""
    assert _turn(THE_TRUTH, TrustScore.neutral()).trust.value > NEUTRAL_TRUST


def test_the_map_is_updated_too_and_not_only_the_trust() -> None:
    """`:508`, second clause: *and update their map*. Both halves, or the rule is half
    kept — an agent that lowered trust and left belief alone would have learned nothing
    from the turn it just survived."""
    prior = Belief.uniform(GRID)
    assert _turn(THE_LIE, TrustScore.neutral()).belief.probability((0, 0)) > prior.probability(
        (0, 0)
    )


def test_the_pursuit_tracks_the_scent_source_and_not_the_claim() -> None:
    """`:1020`: the pursuer "continues to track the actual scent source"."""
    assert belief_target(_turn(THE_LIE, TrustScore.neutral()).belief) == Coordinate(0, 0)


def test_the_lie_does_not_deflect_the_pursuit_at_all() -> None:
    """`:1020` says *continues*, not *redirects* — so the target must be identical to the
    one we would have chosen having heard nothing at all.

    The strongest form of "the physical evidence wins": not that the lie loses, but that
    it never moved the needle.
    """
    lied_to = _turn(THE_LIE, TrustScore.neutral())
    unaddressed = _turn(None, TrustScore.neutral())
    assert belief_target(lied_to.belief) == belief_target(unaddressed.belief)
    assert pursue_belief(BOARD, COP, lied_to.belief) == pursue_belief(
        BOARD, COP, unaddressed.belief
    )


def test_an_unreadable_hint_is_not_punished_as_a_lie() -> None:
    """Refusing to read a message is not the same as catching one out. Punishing a peer
    for a hint *we* declined to parse would let our own strictness pose as their
    dishonesty. `"3,4"` is refused by the rule-27 coordinate guard, not disbelieved."""
    after = _turn("3,4", TrustScore.neutral())
    assert not after.received.usable
    assert after.trust.value == NEUTRAL_TRUST


def test_the_action_under_contradiction_is_still_legal() -> None:
    """`M6-12`'s parent property: every observation shape yields a member of `Action`."""
    assert pursue_belief(BOARD, COP, _turn(THE_LIE, TrustScore.neutral()).belief) in set(Action)


def test_the_contradicted_turn_is_byte_identical_on_replay() -> None:
    """`M6-12e` under this shape: a contradiction must not introduce non-determinism."""
    first, second = _turn(THE_LIE, TrustScore.neutral()), _turn(THE_LIE, TrustScore.neutral())
    assert first.trust == second.trust
    assert first.support == second.support
    cells = [(r, c) for r in range(GRID) for c in range(GRID)]
    assert [first.belief.probability(x) for x in cells] == [
        second.belief.probability(x) for x in cells
    ]
