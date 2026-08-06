"""M6-10 / M6-10e: a hint describes OUR OWN place, dressed by the agreed map area.

The subject of a hint is not a detail. Chapter 4.4's lie test works by comparing a
verbal claim against **the claimant's own scent** (`inst/police_thief_p2p_Summary.md:1020`),
so a hint about the opponent's position could never be checked, and a hint derived from
our belief would publish private inference the `M6-18` guard exists to keep off the wire.
"""

from __future__ import annotations

from inspect import signature

import pytest

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.hints import encodes_coordinates, validate_hint
from p2p_cop_agent.strategy.landmarks import (
    GENERIC_BEARINGS,
    LANDMARKS,
    map_area,
    place_for,
    vocabulary,
)

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")
NEW_YORK = {"world": {"map_area": "New York"}}
NO_AREA = {"world": {"map_area": ""}}


def test_an_agreed_map_area_selects_its_landmarks() -> None:
    """`:1584`: with a location defined, hints use real-world landmarks."""
    assert vocabulary("New York") == LANDMARKS["new york"]
    assert place_for(BOARD, Coordinate(0, 0), NEW_YORK) in LANDMARKS["new york"]


def test_an_empty_map_area_falls_back_to_generic_bearings() -> None:
    """`:1585` and p.51/131: absent a definition, generic bearings are used."""
    assert vocabulary("") == GENERIC_BEARINGS
    assert place_for(BOARD, Coordinate(3, 3), NO_AREA) in GENERIC_BEARINGS


def test_an_unknown_map_area_is_not_an_error() -> None:
    """A classmate may agree a city we never listed; a bearing is legal anywhere."""
    assert place_for(BOARD, Coordinate(3, 3), {"world": {"map_area": "Haifa"}}) in GENERIC_BEARINGS


def test_a_missing_world_section_is_tolerated() -> None:
    assert map_area({}) == ""
    assert place_for(BOARD, Coordinate(3, 3), {}) in GENERIC_BEARINGS


def test_the_area_lookup_ignores_case_and_padding() -> None:
    assert vocabulary("  NEW YORK  ") == LANDMARKS["new york"]


def test_the_place_describes_our_own_cell_and_can_take_nothing_else() -> None:
    """The parameter list is the guard: no belief, no opponent cell can enter."""
    names = set(signature(place_for).parameters)
    assert "own_cell" in names
    assert not names & {"belief", "thief", "target", "predicted", "opponent", "truth"}


def test_different_regions_of_the_board_give_different_places() -> None:
    """A hint that never varied would carry no information, true or false."""
    corners = [Coordinate(0, 0), Coordinate(0, 6), Coordinate(6, 0), Coordinate(6, 6)]
    assert len({place_for(BOARD, cell, NEW_YORK) for cell in corners}) > 1


def test_the_place_is_deterministic_for_a_cell() -> None:
    """Replay needs the same state to produce the same hint."""
    assert place_for(BOARD, Coordinate(2, 5), NEW_YORK) == place_for(
        BOARD, Coordinate(2, 5), NEW_YORK
    )


def test_no_place_word_encodes_a_coordinate() -> None:
    """`AE-27`: the vocabulary itself must be safe, not merely filtered later."""
    for words in (*LANDMARKS.values(), GENERIC_BEARINGS):
        for word in words:
            assert not encodes_coordinates(word), word


def test_every_composed_hint_stays_inside_the_word_limit() -> None:
    """`AF-t14`: the place is short enough that the template cannot overrun 15 words."""
    from p2p_cop_agent.strategy.hints import template_hint

    for config in (NEW_YORK, NO_AREA):
        for cell in (Coordinate(0, 0), Coordinate(3, 3), Coordinate(6, 6)):
            place = place_for(BOARD, cell, config)
            for bluff in (False, True):
                validate_hint(template_hint(place, bluff=bluff).text)


def test_an_off_board_cell_is_refused() -> None:
    """A place we cannot occupy is a place we cannot honestly claim."""
    from p2p_cop_agent.domain.board import BoardError

    with pytest.raises(BoardError):
        place_for(BOARD, Coordinate(9, 9), NEW_YORK)


def test_a_non_string_map_area_is_treated_as_unset() -> None:
    """A malformed shared object must not crash the verbal layer mid-match."""
    assert map_area({"world": {"map_area": 42}}) == ""
    assert map_area({"world": "not a section"}) == ""
    assert place_for(BOARD, Coordinate(1, 1), {"world": {"map_area": None}}) in GENERIC_BEARINGS
