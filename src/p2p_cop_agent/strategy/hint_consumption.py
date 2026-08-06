"""Inbound hint consumption: parse defensively, weight by running trust (M6-11).

The receiving half of the verbal layer. A peer's hint is **untrusted input from an
adversary** -- it may be absent, empty, over-long, non-textual, a bluff, or a covert
coordinate channel -- so consumption is built to never let any of that reach a move
`[AE-25]`:

* **Parse, never execute (M6-11a).** ``receive_hint`` returns an inert
  :class:`ReceivedHint` -- text plus a usability verdict. It touches no domain layer and
  yields no action; the move always comes from the pure-Python pursuit, and the hint can
  at most colour *belief*, never the policy directly.
* **Weight by the sender's running trust (M6-11b).** A hint's influence is scaled by a
  local :class:`TrustScore` -- the Cop's private, running assessment of this peer. Trust
  is Cop-private (never on the wire, M6-18), so its arithmetic is a local project choice.
* **Tolerate anything (M6-11c).** ``None``, an empty or whitespace string, a non-string,
  or an over-long hint never raises: the first three are marked unusable with a reason,
  and an over-long hint is silently truncated to the word limit -- we bound a verbose
  peer, we do not reject it.

The inbound coordinate guard is the **same** :func:`~p2p_cop_agent.strategy.hints.
encodes_coordinates` our own generator must pass: if the opponent smuggles a coordinate
protocol `[AE-27]`, we refuse to decode it as a covert channel rather than trusting a
convention. So "our hints are coordinate-free" and "we never read a coordinate channel"
are one rule, not two.

**Deferred, by design.** This module produces a scalar *weight* and an inert *text*; it
does not yet map that text into belief-space cells (``M6-02e``) -- that needs a
coordinate-free landmark protocol agreed with the opponent -- nor does it auto-lower
trust when scent contradicts a hint (``M6-02f``), which needs the decode to exist first.
The trust *machine* (``reinforced``/``weakened``) is here; its scent-contradiction
*trigger* is deferred to ``M6-02f``.
"""

from __future__ import annotations

from dataclasses import dataclass

from p2p_cop_agent.strategy.hints import (
    HINT_MAX_WORDS_DEFAULT,
    encodes_coordinates,
    enforce_word_limit,
)

NEUTRAL_TRUST = 0.5
TRUST_UPDATE_RATE = 0.25

_REASON_NOT_TEXT = "not text"
_REASON_EMPTY = "empty"
_REASON_COORDINATES = "encodes coordinates"


@dataclass(frozen=True, slots=True)
class ReceivedHint:
    """A parsed inbound hint and whether it may inform belief.

    Inert by construction: it carries text and a verdict, never a move. ``reason`` is
    empty exactly when ``usable`` is ``True``.
    """

    text: str
    usable: bool
    reason: str = ""


@dataclass(frozen=True, slots=True)
class TrustScore:
    """The Cop's private, running trust in one peer, a probability in ``[0, 1]``.

    Updated by a bounded step toward a bound, so repeated reinforcement approaches -- but
    never reaches -- certainty: we never grant a peer absolute trust or absolute
    suspicion. Immutable; every update returns a new score, keeping the strategy layer
    reproducible.
    """

    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"trust must be in [0, 1], got {self.value}")

    @classmethod
    def neutral(cls) -> TrustScore:
        """Return the prior for an un-assessed peer (no reason to trust or doubt)."""
        return cls(NEUTRAL_TRUST)

    def reinforced(self, rate: float = TRUST_UPDATE_RATE) -> TrustScore:
        """Return trust moved a fraction ``rate`` toward 1.0 (a hint that held up)."""
        return TrustScore(self.value + rate * (1.0 - self.value))

    def weakened(self, rate: float = TRUST_UPDATE_RATE) -> TrustScore:
        """Return trust moved a fraction ``rate`` toward 0.0 (a hint scent contradicted).

        The update mechanism. Its trigger lives in ``M6-02f``'s
        :func:`~p2p_cop_agent.strategy.trust.corroboration`, which measures the claim
        against the scent; ``M6-12b`` proves the pair behaves as `:508` requires.
        """
        return TrustScore(self.value - rate * self.value)


def receive_hint(raw: object, max_words: int = HINT_MAX_WORDS_DEFAULT) -> ReceivedHint:
    """Parse an untrusted inbound hint into an inert :class:`ReceivedHint` (M6-11a/c).

    Never raises and never yields a move. A non-string, an empty or whitespace-only
    string, or a coordinate-encoding string is marked unusable with a reason; a valid
    hint is stripped and truncated to ``max_words`` and marked usable.
    """
    if not isinstance(raw, str):
        return ReceivedHint("", usable=False, reason=_REASON_NOT_TEXT)
    text = raw.strip()
    if not text:
        return ReceivedHint("", usable=False, reason=_REASON_EMPTY)
    if encodes_coordinates(text):
        return ReceivedHint(text, usable=False, reason=_REASON_COORDINATES)
    return ReceivedHint(enforce_word_limit(text, max_words), usable=True)


def hint_weight(received: ReceivedHint, trust: TrustScore) -> float:
    """Return the scalar weight a hint's evidence should carry (M6-11b).

    The sender's running trust when the hint is usable, else ``0.0`` -- an unusable hint
    contributes no evidence. This is the seam ``M6-02e`` will multiply into the
    hint-derived likelihood once free text can be mapped to belief cells; until then the
    weight is computed but has no cell-likelihood to scale.
    """
    return trust.value if received.usable else 0.0
