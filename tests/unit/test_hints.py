"""M6-05 / M6-10: hint generation is bounded, natural-language, and zero-token.

Two book rules are hard constraints on every provider: the word limit (`AF-t14`) and
the no-coordinate rule (`AE-27`). The default provider is a template, so a series is
playable at zero tokens, and every hint carries an explicit truth/bluff intent.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.strategy.hints import (
    BLUFF,
    TRUTH,
    Hint,
    HintError,
    encodes_coordinates,
    enforce_word_limit,
    hint_max_words,
    template_hint,
    validate_hint,
    within_word_limit,
)


def test_hint_max_words_reads_the_negotiated_limit_or_defaults() -> None:
    assert hint_max_words({"world": {"hint_max_words": 15}}) == 15
    assert hint_max_words({"world": {"hint_max_words": 8}}) == 8
    assert hint_max_words({}) == 15
    assert hint_max_words({"world": {"hint_max_words": 0}}) == 15  # invalid -> default


def test_word_limit_bounds_and_truncates() -> None:
    assert within_word_limit("a b c", 3)
    assert not within_word_limit("a b c d", 3)
    assert enforce_word_limit("one two three four", 2) == "one two"


@pytest.mark.parametrize("text", ["at 3,4", "3 4", "(2, 5)", "row 3", "cell 12", "COL 7"])
def test_a_coordinate_protocol_is_detected(text: str) -> None:
    assert encodes_coordinates(text)


@pytest.mark.parametrize("text", [
    "near the old library", "heading north-east", "three blocks past the market", "by the river",
])
def test_natural_language_is_not_flagged_as_coordinates(text: str) -> None:
    assert not encodes_coordinates(text)


def test_validate_hint_rejects_overlong_and_coordinate_hints() -> None:
    with pytest.raises(HintError, match="words"):
        validate_hint("w " * 20, max_words=15)
    with pytest.raises(HintError, match="coordinate"):
        validate_hint("meet at 3,4")
    assert validate_hint("near the park") == "near the park"


def test_a_truthful_template_hint_is_valid_and_flagged() -> None:
    hint = template_hint("old market", bluff=False)
    assert isinstance(hint, Hint)
    assert hint.intent == TRUTH
    assert "old market" in hint.text
    assert within_word_limit(hint.text, 15) and not encodes_coordinates(hint.text)


def test_a_bluffed_template_hint_carries_the_bluff_intent() -> None:
    assert template_hint("river", bluff=True).intent == BLUFF


def test_the_template_is_deterministic_per_variant() -> None:
    assert template_hint("park", variant=1).text == template_hint("park", variant=1).text


def test_a_template_fed_a_coordinate_is_refused_not_emitted() -> None:
    with pytest.raises(HintError):
        template_hint("sector 3,4")
