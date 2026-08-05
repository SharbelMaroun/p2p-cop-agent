"""Fold one turn's observation into belief: scent first, then the hint (M6-02, M6-11).

The book's order, from chapter 4.4's case study: the pursuer measures the scent, tests
the verbal claim against it, adjusts the trust coefficient, and only then updates the
probability matrix (`inst/police_thief_p2p_Summary.md:1017-1020`).

That order is load-bearing. Scent **cannot be falsified** -- it is "an involuntary
byproduct of movement" (`:1022`) -- while a hint is a claim by an opponent who is allowed
to lie. Applying the unfalsifiable evidence first means the hint is judged against a
belief the Thief could not manipulate, so a lie is measured rather than absorbed.

Trust runs *forward* between turns: the returned trust is the input to the next call, so
a peer that lies repeatedly is believed less each time. Nothing here is on the wire --
belief and trust are Cop-private (M6-18) -- so this is strategy, not contract.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from p2p_cop_agent.strategy.belief import Belief, Cell, scent_likelihood
from p2p_cop_agent.strategy.hint_decode import decode_hint
from p2p_cop_agent.strategy.hints import HINT_MAX_WORDS_DEFAULT
from p2p_cop_agent.strategy.trust import corroboration, trust_weighted, update_trust


@dataclass(frozen=True, slots=True)
class Perception:
    """One turn's updated belief and the running trust in the opponent's word."""

    belief: Belief
    trust: float
    support: float


def consume_turn(
    belief: Belief,
    *,
    observed_scent: Mapping[Cell, float],
    hint: object,
    observer: Cell,
    grid_size: int,
    trust: float,
    start: int = 0,
    max_words: int = HINT_MAX_WORDS_DEFAULT,
) -> Perception:
    """Return the belief and trust after one turn of scent and one hint.

    ``observed_scent`` is the opponent's emitted field as parsed from the wire, never
    its position, so objective truth cannot enter (`AE-8`, `AE-9`). ``hint`` is raw and
    may be anything at all -- absent, empty, non-text, over-long, or hostile; it is only
    ever read for direction words (M6-11a, M6-11c).
    """
    after_scent = belief.updated(
        scent_likelihood(observed_scent, grid_size, start=start)
    )
    claim = decode_hint(
        hint, observer=observer, grid_size=grid_size, max_words=max_words, start=start
    )
    support = corroboration(claim, observed_scent)
    running = update_trust(trust, support)
    return Perception(
        belief=after_scent.updated(trust_weighted(claim, running)),
        trust=running,
        support=support,
    )
