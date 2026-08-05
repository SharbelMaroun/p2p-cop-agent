"""The reliability factor for a Thief's verbal hint (M6-02b, M6-02f, M6-11b).

Chapter 4.4's boxed case study is written from the **pursuer's** side, so it is this
peer's specification almost verbatim (`inst/police_thief_p2p_Summary.md:1007-1022`):

    The thief states "I am moving North". The pursuer expects a fresh trail there of
    "approximately 0.81 (calculated as 0.9 * (1 - 0.1) = 0.81)" and measures 0.00. "The
    discrepancy between the expected 0.81 and the measured 0.00 is absolute." The
    pursuer "lowers the trust coefficient assigned to the thief's verbal statements and
    updates the probability matrix", ignores the claim, and keeps tracking the real
    scent source.

:func:`expected_fresh_scent` is that 0.81, derived from the two Appendix F constants
rather than typed in, so it follows the locked scent model instead of drifting from it.

**What the book fixes, and what it leaves to us.** It fixes the *shape* -- Bayes with a
reliability factor (`:1480`) -- and the *evidence* -- expected-versus-measured scent
where the claim points. It states **no** starting trust, no step size, no decay rate for
repeated lies, and no bound, and says the translation into a numeric belief map is the
agent's own (`:1025`). Belief is Cop-private and never crosses the wire (M6-18), so
unlike the hash-locked scent model there is no opponent to disagree with these numbers.
Every constant here is PROJECT-PROPOSED.

**Trust is per-opponent and persistent within a match, not per-hint.** A liar caught
once should still be doubted on its next sentence -- that is the whole point of a
*running* coefficient, and a value recomputed from scratch each turn would forgive every
lie immediately.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_cop_agent.strategy.belief import Cell
from p2p_cop_agent.strategy.scent import CENTER_INTENSITY, DECAY_RATE

# Trust runs on [0, 1]: 1 believes a hint fully, 0 ignores it entirely.
MIN_TRUST, MAX_TRUST = 0.0, 1.0
# Neutral prior: an unknown classmate is neither trusted nor dismissed. The league is
# played against strangers, so assuming either would be a guess about a specific team.
INITIAL_TRUST = 0.5
# How far one fully corroborated or fully contradicted hint moves trust. At 0.2, five
# consecutive absolute lies reach the floor and an honest peer recovers just as fast --
# a liar is not condemned forever, which matters because bluffing is legal here.
TRUST_STEP = 0.2


def expected_fresh_scent(
    centre: float = CENTER_INTENSITY, decay: float = DECAY_RATE
) -> float:
    """Return the book's expected fresh-trail intensity: ``0.9 * (1 - 0.1) = 0.81``.

    Derived from the locked model's own constants, never hard-coded, so a negotiated
    change to the scent model moves this with it instead of silently disagreeing.
    """
    return centre * (1.0 - decay)


def corroboration(
    likelihood: Mapping[Cell, float],
    observed: Mapping[Cell, float],
    *,
    expected: float | None = None,
) -> float:
    """Return how well the hint's claim is supported by scent, on ``[0, 1]``.

    The measure is the book's: take the cells the hint favours, look at the strongest
    scent actually measured among them, and compare it to the fresh-trail intensity we
    would expect if the claim were true. ``1.0`` is full support, ``0.0`` the case study's
    "absolute" contradiction -- a claimed direction with no scent residue at all.

    The *strongest* cell is used rather than the mean because a direction names a whole
    half-plane: the Thief occupies one cell in it, so a single fresh trail corroborates
    the claim while averaging would dilute it to nothing across a large board.

    A hint that favours nothing (a uniform likelihood) is unfalsifiable, so it returns
    neutral ``0.5`` and leaves trust untouched -- silence is not a lie.
    """
    target = expected if expected is not None else expected_fresh_scent()
    if target <= 0.0:
        return 0.5
    strongest = max(likelihood.values(), default=0.0)
    favoured = [cell for cell, value in likelihood.items() if value >= strongest]
    if not favoured or len(favoured) == len(likelihood):
        return 0.5  # nothing singled out: no claim to test
    measured = max((max(0.0, observed.get(cell, 0.0)) for cell in favoured), default=0.0)
    return min(1.0, measured / target)


def update_trust(trust: float, support: float, *, step: float = TRUST_STEP) -> float:
    """Return the running trust after one hint, clipped to ``[0, 1]`` (M6-02f).

    ``support`` is :func:`corroboration`. Above neutral the hint is corroborated and
    trust rises; below it the scent contradicts the claim and trust falls, which is the
    case study's "lowers the trust coefficient" applied as arithmetic rather than as a
    one-off judgement.
    """
    moved = trust + step * 2.0 * (support - 0.5)
    return max(MIN_TRUST, min(MAX_TRUST, moved))


def trust_weighted(likelihood: Mapping[Cell, float], trust: float) -> dict[Cell, float]:
    """Temper a hint's likelihood toward uniform in proportion to distrust (M6-11b).

    ``L_eff = t·L + (1 - t)·mean(L)``. At ``t = 1`` the hint applies in full; at
    ``t = 0`` it flattens to a constant, which Bayes treats as no evidence -- the case
    study's "the pursuer ignores the verbal claim", reached by arithmetic rather than by
    a special case. A distrusted opponent is never *inverted*: a liar's claim is
    evidence of nothing, not evidence of the opposite, since it may simply be true.
    """
    if not likelihood:
        return {}
    weight = max(MIN_TRUST, min(MAX_TRUST, trust))
    mean = sum(likelihood.values()) / len(likelihood)
    return {
        cell: weight * value + (1.0 - weight) * mean for cell, value in likelihood.items()
    }
