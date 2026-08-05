"""M6-11: inbound hints are parsed inertly, tolerated, and weighted by running trust.

A peer's hint is adversarial input. Consumption must never turn it into a move
(`AE-25`), must tolerate every malformed shape (`M6-11c`), must refuse a smuggled
coordinate channel (`AE-27`), and must scale a hint's influence by the Cop's private,
running trust in that peer (`M6-11b`).
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.strategy.hint_consumption import (
    NEUTRAL_TRUST,
    ReceivedHint,
    TrustScore,
    hint_weight,
    receive_hint,
)


def test_a_valid_hint_is_usable_and_stripped() -> None:
    received = receive_hint("  heading toward the old market  ")
    assert received.usable
    assert received.reason == ""
    assert received.text == "heading toward the old market"


@pytest.mark.parametrize("raw", [None, 42, 3.14, ["north"], {"p": "river"}, b"river"])
def test_a_non_string_is_tolerated_as_unusable(raw: object) -> None:
    received = receive_hint(raw)
    assert not received.usable
    assert received.reason == "not text"
    assert received.text == ""


@pytest.mark.parametrize("raw", ["", "   ", "\t\n"])
def test_an_empty_or_whitespace_hint_is_tolerated_as_unusable(raw: str) -> None:
    received = receive_hint(raw)
    assert not received.usable
    assert received.reason == "empty"


def test_an_over_long_hint_is_truncated_not_rejected() -> None:
    received = receive_hint("word " * 30, max_words=15)
    assert received.usable
    assert len(received.text.split()) == 15


@pytest.mark.parametrize("raw", ["meet at 3,4", "go to row 3", "cell 12 now", "2 5"])
def test_a_coordinate_channel_is_refused(raw: str) -> None:
    received = receive_hint(raw)
    assert not received.usable
    assert received.reason == "encodes coordinates"


def test_receiving_never_raises_on_any_input() -> None:
    for raw in (None, "", "  ", "at 3,4", "word " * 40, object(), 0):
        assert isinstance(receive_hint(raw), ReceivedHint)


def test_trust_starts_neutral_and_stays_bounded() -> None:
    assert TrustScore.neutral().value == NEUTRAL_TRUST
    with pytest.raises(ValueError, match="in \\[0, 1\\]"):
        TrustScore(1.5)
    with pytest.raises(ValueError, match="in \\[0, 1\\]"):
        TrustScore(-0.1)


def test_reinforcement_approaches_but_never_reaches_certainty() -> None:
    trust = TrustScore.neutral()
    for _ in range(50):
        trust = trust.reinforced()
        assert trust.value < 1.0
    assert trust.value > 0.9  # converging up


def test_weakening_approaches_but_never_reaches_zero() -> None:
    trust = TrustScore.neutral()
    for _ in range(50):
        trust = trust.weakened()
        assert trust.value > 0.0
    assert trust.value < 0.1  # converging down


def test_trust_updates_are_deterministic() -> None:
    a = TrustScore.neutral().reinforced().weakened()
    b = TrustScore.neutral().reinforced().weakened()
    assert a == b


def test_weight_is_trust_when_usable_and_zero_otherwise() -> None:
    trust = TrustScore(0.8)
    usable = receive_hint("near the river")
    unusable = receive_hint("meet at 3,4")
    assert hint_weight(usable, trust) == pytest.approx(0.8)
    assert hint_weight(unusable, trust) == 0.0


def test_consumption_yields_no_action_attribute() -> None:
    # Parse-not-execute: the result exposes text and a verdict, never a move.
    received = receive_hint("heading north")
    assert not hasattr(received, "action")
    assert not hasattr(received, "move")
