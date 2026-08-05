"""Fold one turn's observation into belief: scent first, then the hint (M6-02, M6-11).

The book's order, from chapter 4.4's case study: the pursuer measures the scent, tests
the verbal claim against it, adjusts the trust coefficient, and only then updates the
probability matrix (`inst/police_thief_p2p_Summary.md:1017-1020`).

That order is load-bearing. Scent **cannot be falsified** -- it is "an involuntary
byproduct of movement" (`:1022`) -- while a hint is a claim by an opponent who is allowed
to lie. Applying the unfalsifiable evidence first means the hint is judged against a
belief the Thief could not manipulate, so a lie is measured rather than absorbed.

This is the one pipeline, assembled from both halves of the verbal layer:

    receive_hint   -- defensive parse, coordinate guard  (M6-11a/c)
      -> decode_hint    -- free text to a cell likelihood    (M6-02e)
      -> corroboration  -- the scent test for a lie          (M6-02f)
      -> apply_support  -- move the running TrustScore       (M6-02b)
      -> trust_weighted -> Bayes

**The coordinate guard is not optional and runs first.** An opponent that smuggles a
``3,4`` into its hint is attempting the numeric protocol Appendix E rule 27 forbids, and
the answer is to refuse to read it at all rather than to parse it as ordinary words. The
guard is the *same* :func:`~p2p_cop_agent.strategy.hints.encodes_coordinates` our own
generator must pass, so "our hints carry no coordinates" and "we never read a coordinate
channel" are one rule rather than two that can drift apart.

Trust runs *forward* between turns: the returned score is the input to the next call, so
a peer that lies repeatedly is believed less each time. Nothing here is on the wire --
belief and trust are Cop-private (M6-18) -- so this is strategy, not contract.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from p2p_cop_agent.strategy.belief import Belief, Cell, scent_likelihood
from p2p_cop_agent.strategy.hint_consumption import (
    ReceivedHint,
    TrustScore,
    receive_hint,
)
from p2p_cop_agent.strategy.hint_decode import decode_hint
from p2p_cop_agent.strategy.hints import HINT_MAX_WORDS_DEFAULT
from p2p_cop_agent.strategy.trust import (
    NEUTRAL_SUPPORT,
    apply_support,
    corroboration,
    trust_weighted,
)


@dataclass(frozen=True, slots=True)
class Perception:
    """One turn's updated belief, the running trust, and why it moved.

    ``received`` is kept so a caller can log *why* a hint was ignored -- "encodes
    coordinates" is a materially different event from "the scent contradicted it", and
    collapsing both into a number would hide an attempted rule-27 channel.
    """

    belief: Belief
    trust: TrustScore
    support: float
    received: ReceivedHint


def consume_turn(
    belief: Belief,
    *,
    observed_scent: Mapping[Cell, float],
    hint: object,
    observer: Cell,
    grid_size: int,
    trust: TrustScore,
    start: int = 0,
    max_words: int = HINT_MAX_WORDS_DEFAULT,
) -> Perception:
    """Return the belief and trust after one turn of scent and one hint.

    ``observed_scent`` is the opponent's emitted field as parsed from the wire, never
    its position, so objective truth cannot enter (`AE-8`, `AE-9`). ``hint`` is raw and
    may be anything at all -- absent, empty, non-text, over-long, or hostile.

    An **unusable** hint leaves trust untouched. Refusing to read a message is not the
    same as catching a lie, and punishing a peer for a hint we declined to parse would
    let our own strictness masquerade as their dishonesty.
    """
    after_scent = belief.updated(
        scent_likelihood(observed_scent, grid_size, start=start)
    )
    received = receive_hint(hint, max_words)
    if not received.usable:
        return Perception(after_scent, trust, NEUTRAL_SUPPORT, received)

    claim = decode_hint(
        received.text,
        observer=observer,
        grid_size=grid_size,
        max_words=max_words,
        start=start,
    )
    support = corroboration(claim, observed_scent)
    running = apply_support(trust, support)
    return Perception(
        belief=after_scent.updated(trust_weighted(claim, running.value)),
        trust=running,
        support=support,
        received=received,
    )
