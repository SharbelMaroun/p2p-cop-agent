"""M6-08: the scent observation survives the wire, and a hostile one does not pass.

The grid arrives from an opponent, so every parse failure here is an attack surface
rather than a formatting nicety.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.protocol.scent_wire import (
    WIRE_PRECISION,
    ScentWireError,
    decode_scent,
    encode_scent,
    saturation_limit,
)
from p2p_cop_agent.strategy.scent_field import ScentField

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")
LIMITS = {"min_index": BOARD.min_index, "max_index": BOARD.max_index}


def _sent_window() -> dict:
    trail = ScentField(board=BOARD)
    trail.advance(Coordinate(3, 3))
    return encode_scent(trail.window(Coordinate(3, 3)))


def test_the_keys_are_row_comma_col_in_position_axis_order() -> None:
    """`M6-08a`: the reference's shape — row first, the same order as a position."""
    grid = encode_scent({(1, 4): 0.62})
    assert grid == {"1,4": 0.62}


def test_a_full_window_round_trips_without_loss() -> None:
    """`M6-08`: what we send is what a conformant peer reads back."""
    sent = _sent_window()
    back = decode_scent(sent, **LIMITS)
    assert back[(3, 3)] == pytest.approx(0.9)
    assert len(back) == len(sent) == 25


def test_silent_cells_are_transmitted_rather_than_omitted() -> None:
    """The reference includes zeros so the receiver sees a fixed-size window."""
    assert "0,0" in encode_scent({(0, 0): 0.0, (1, 1): 0.5})


def test_a_peer_that_omits_its_zeros_is_still_read_correctly() -> None:
    """Generous inbound: an absent cell and a zero cell mean the same thing."""
    sparse = decode_scent({"2,2": 0.9}, **LIMITS)
    assert sparse == {(2, 2): 0.9}


def test_the_wire_precision_is_pinned() -> None:
    """`M6-08c`: repeated decay yields 0.7290000000000001; the wire does not."""
    assert encode_scent({(0, 0): 0.7290000000000001}) == {"0,0": 0.729}
    assert len(str(encode_scent({(0, 0): 1 / 3})["0,0"]).split(".")[1]) <= WIRE_PRECISION


def test_an_absent_grid_is_no_evidence_not_an_error() -> None:
    assert decode_scent(None, **LIMITS) == {}
    assert decode_scent({}, **LIMITS) == {}


@pytest.mark.parametrize(
    ("label", "grid"),
    [
        ("a non-object grid", [1, 2, 3]),
        ("a non-string key", {3: 0.5}),
        ("a key that is not row,col", {"3-4": 0.5}),
        ("a key with a negative index", {"-1,2": 0.5}),
        ("a non-numeric intensity", {"3,3": "0.9"}),
        ("a boolean intensity", {"3,3": True}),
        ("a NaN intensity", {"3,3": float("nan")}),
        ("an infinite intensity", {"3,3": float("inf")}),
        ("a negative intensity", {"3,3": -0.1}),
        ("more scent than the model can saturate to", {"3,3": 12.0}),
        ("an off-board cell", {"9,9": 0.5}),
    ],
)
def test_a_hostile_or_malformed_grid_is_refused(label: str, grid: object) -> None:
    """`M6-08b`: every one of these would otherwise reach the belief update."""
    with pytest.raises(ScentWireError):
        decode_scent(grid, **LIMITS)


def test_a_legitimately_accumulated_cell_is_accepted() -> None:
    """A peer that stood still has a cell above 0.9, and that is the formula working.

    An earlier parser capped at the centre intensity and would have refused our own
    two-turn trail (1.458). The bound is the model's saturation point, not its deposit.
    """
    assert decode_scent({"3,3": 1.458}, **LIMITS) == {(3, 3): 1.458}
    assert decode_scent({"3,3": 8.9}, **LIMITS) == {(3, 3): 8.9}


def test_a_refusal_names_what_was_wrong() -> None:
    """A peer can only fix what we tell it; an opaque refusal helps nobody."""
    with pytest.raises(ScentWireError, match="off a board"):
        decode_scent({"9,9": 0.5}, **LIMITS)
    with pytest.raises(ScentWireError, match="negative"):
        decode_scent({"3,3": -1.0}, **LIMITS)


def test_a_corrupt_grid_raises_rather_than_degrading_to_no_evidence() -> None:
    """Scent is the one channel that cannot be faked; losing it silently is worse."""
    with pytest.raises(ScentWireError):
        decode_scent({"3,3": 0.5, "bad": 0.1}, **LIMITS)


def test_a_degenerate_model_cannot_bound_a_field() -> None:
    """A zero decay rate never saturates, so there is no ceiling to check against."""
    with pytest.raises(ScentWireError, match="decay rate must be positive"):
        saturation_limit(decay=0.0)


def test_the_saturation_limit_is_derived_from_the_agreed_constants() -> None:
    assert saturation_limit() == pytest.approx(9.0)
    assert saturation_limit(centre=0.5, decay=0.25) == pytest.approx(2.0)
