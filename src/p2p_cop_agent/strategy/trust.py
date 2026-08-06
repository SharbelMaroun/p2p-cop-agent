"""The scent test that decides whether to trust a hint (M6-02b, M6-02f).

`hint_consumption` owns the trust *machine* -- :class:`TrustScore` and its bounded
`reinforced`/`weakened` steps -- and says outright that its scent-contradiction
**trigger** is deferred to `M6-02f`, "which needs the decode to exist first". This module
is that trigger. The two were written independently and are joined here rather than
duplicated: there is one trust type, one rate, and one neutral prior in the package.

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
reliability factor (`:1480`) -- and the *evidence*: expected-versus-measured scent where
the claim points. It states **no** starting trust, no step size, no decay rate for
repeated lies, and no bound, and says the translation into a numeric belief map is the
agent's own (`:1025`). Belief and trust are Cop-private and never cross the wire
(M6-18), so unlike the hash-locked scent model there is no opponent to disagree with
these numbers. Everything here is PROJECT-PROPOSED.

**Warning: the case study's quadrant labels are inverted (`C-032`).** It calls `(1,4)`
"south-east" and `(5,2)` "northern", which is upside down under the Appendix F top-left
origin. Its *intensities* are authoritative; its *cells* are not.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_cop_agent.strategy.belief import Cell
from p2p_cop_agent.strategy.hint_consumption import TRUST_UPDATE_RATE, TrustScore
from p2p_cop_agent.strategy.scent import CENTER_INTENSITY, DECAY_RATE

# Corroboration is scored on [0, 1]; this is "no information either way".
NEUTRAL_SUPPORT = 0.5


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
    would expect if the claim were true. ``1.0`` is full support, ``0.0`` the case
    study's "absolute" contradiction -- a claimed direction with no scent residue at all.

    The *strongest* cell is used rather than the mean because a direction names a whole
    half-plane: the Thief occupies one cell in it, so a single fresh trail corroborates
    the claim while averaging would dilute it to nothing across a large board.

    A hint that favours nothing (a uniform likelihood) is unfalsifiable, so it returns
    :data:`NEUTRAL_SUPPORT` and leaves trust untouched -- silence is not a lie.
    """
    target = expected if expected is not None else expected_fresh_scent()
    if target <= 0.0:
        return NEUTRAL_SUPPORT
    strongest = max(likelihood.values(), default=0.0)
    favoured = [cell for cell, value in likelihood.items() if value >= strongest]
    if not favoured or len(favoured) == len(likelihood):
        return NEUTRAL_SUPPORT  # nothing singled out: no claim to test
    measured = max((max(0.0, observed.get(cell, 0.0)) for cell in favoured), default=0.0)
    return min(1.0, measured / target)


def apply_support(
    trust: TrustScore, support: float, *, rate: float = TRUST_UPDATE_RATE
) -> TrustScore:
    """Move trust by the scent evidence, and by **how strong** that evidence is (M6-02f).

    Above :data:`NEUTRAL_SUPPORT` the scent corroborates the claim and trust is
    reinforced; below it the scent contradicts it and trust is weakened -- the case
    study's "lowers the trust coefficient", as arithmetic rather than a one-off
    judgement. The rate is scaled by the *distance* from neutral, so the study's absolute
    contradiction (``0.00`` measured against an expected ``0.81``) moves trust at the
    full rate while a marginal disagreement barely moves it at all.

    Delegating to ``reinforced``/``weakened`` keeps their bounded-step property: trust
    approaches 1.0 and 0.0 but never arrives, so no peer is ever granted certainty or
    condemned beyond appeal. Bluffing is legal here -- a liar must be able to rebuild.
    """
    strength = abs(support - NEUTRAL_SUPPORT) / NEUTRAL_SUPPORT
    scaled = rate * min(1.0, strength)
    if scaled == 0.0:
        return trust
    return trust.reinforced(scaled) if support > NEUTRAL_SUPPORT else trust.weakened(scaled)


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
    weight = max(0.0, min(1.0, trust))
    mean = sum(likelihood.values()) / len(likelihood)
    return {
        cell: weight * value + (1.0 - weight) * mean for cell, value in likelihood.items()
    }
