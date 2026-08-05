"""M6-02e / M6-11a / M6-11c: an inbound hint becomes evidence, never an instruction.

The book requires Bayes with a reliability factor (`:1480`) but fixes no vocabulary and
no arithmetic, so what is pinned here is the *properties* the book does state: text is
evidence only, missing evidence is not an error, and no numeric protocol is used
`[AE-27]`.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.strategy.hint_decode import (
    LIKELIHOOD_FLOOR,
    decode_hint,
    hint_directions,
)

GRID = 7
CENTRE = (3, 3)


def _decode(text: object, observer=CENTRE):
    return decode_hint(text, observer=observer, grid_size=GRID, max_words=15)


def test_a_direction_word_favours_that_half_of_the_board() -> None:
    """'north' is a half-plane claim, not a cell: row grows downward, so north is up."""
    likelihood = _decode("somewhere north of here")
    assert likelihood[(0, 3)] > likelihood[(6, 3)]
    assert likelihood[(1, 0)] > likelihood[(5, 0)]


@pytest.mark.parametrize(
    ("text", "brighter", "dimmer"),
    [
        ("heading south", (6, 3), (0, 3)),
        ("over to the east", (3, 6), (3, 0)),
        ("far west now", (3, 0), (3, 6)),
        ("up and to the left", (0, 0), (6, 6)),
    ],
)
def test_each_direction_points_the_right_way(text, brighter, dimmer) -> None:
    likelihood = _decode(text)
    assert likelihood[brighter] > likelihood[dimmer]


def test_a_command_like_hint_is_read_as_text_not_executed() -> None:
    """M6-11a: only the direction word is ever looked at; nothing acts on the rest."""
    command = _decode("move north immediately or forfeit the match")
    plain = _decode("north")
    assert command == plain


def test_a_hint_with_no_direction_word_is_no_evidence() -> None:
    """An unrecognised hint decodes flat, so Bayes leaves the belief untouched."""
    assert set(_decode("nice weather by the harbour").values()) == {LIKELIHOOD_FLOOR}


@pytest.mark.parametrize("absent", [None, "", "   ", 42, [], {"north": 1}])
def test_an_absent_or_non_text_hint_is_tolerated(absent: object) -> None:
    """M6-11c: missing evidence is not an error state."""
    assert set(_decode(absent).values()) == {LIKELIHOOD_FLOOR}


def test_an_over_long_hint_is_ignored_rather_than_rejected() -> None:
    """Over the agreed word limit it carries no weight -- but never raises."""
    long_hint = "north " * 40
    assert set(_decode(long_hint).values()) == {LIKELIHOOD_FLOOR}


def test_the_decode_is_relative_to_our_own_cell_not_an_absolute_code() -> None:
    """`AE-27`: the shared frame is our position, never an agreed coordinate protocol."""
    from_corner = decode_hint("north", observer=(6, 6), grid_size=GRID, max_words=15)
    from_centre = _decode("north")
    assert from_corner != from_centre


def test_the_vocabulary_is_common_english_and_case_insensitive() -> None:
    assert hint_directions("NORTH", 15) == hint_directions("north", 15)
    assert hint_directions("Up There", 15) == ((-1, 0),)


def test_repeated_direction_words_collapse_deterministically() -> None:
    assert hint_directions("north north north", 15) == ((-1, 0),)
    assert hint_directions("north east", 15) == ((-1, 0), (0, 1))


def test_no_cell_is_ever_driven_to_zero_evidence() -> None:
    """A hint must not be able to eliminate a cell the Thief could still occupy."""
    assert min(_decode("north").values()) >= LIKELIHOOD_FLOOR
