"""C-042: every sealed movement record carries the agreed cross-repo shape.

After a completed, cryptographically verified game 2, `uoh-ay26`'s replay converter
read `payload["state"]` and crashed -- KeyError -- because this repository's Police
sealed `{step, move, position, barriers, intent, hint}` while the companion Thief
seals the book-shaped record with `state` (the commit covers State||Move||Intent).
Their coordinator then stopped the series. Same disease as `C-041`: the two repos
independently drifting on a shape the wire treats as one.

These tests drive the REAL producer (`live_decide`), not a fixture -- the C-041
lesson -- and pin the exact `state` string format the Thief has proven against a
live opponent across two full series.
"""

import re

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.orchestration.live_policy import live_decide

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")
GAME = {"world": {"map_area": "New York", "hint_max_words": 15},
        "movement_and_barriers": {"max_barriers": 14}}

AGREED_FIELDS = {"step", "state", "position", "move", "intent", "hint"}
STATE_FORMAT = re.compile(r"^grid=\d+x\d+;self=\[\d+, \d+\];barriers=\[.*\]$")


def sealed(step: int = 1) -> dict:
    decide = live_decide(BOARD, Coordinate(0, 0), GAME)
    payload, _public = decide(
        {"step": step, "sender": "thief", "hint": "x", "smell_grid": {"3,3": 0.9},
         "commit": "0" * 64, "timestamp": "t"})
    return payload


def test_every_agreed_field_is_present() -> None:
    payload = sealed()
    assert set(payload) >= AGREED_FIELDS, f"missing: {AGREED_FIELDS - set(payload)}"


def test_the_state_string_matches_the_thief_proven_format() -> None:
    """`grid=7x7;self=[r, c];barriers=[...]` -- exactly `state_str`'s output."""
    assert STATE_FORMAT.fullmatch(sealed()["state"])


def test_state_self_equals_the_post_move_position() -> None:
    """The accepted convention is post-move: `state.self` == `position`."""
    payload = sealed()
    row, col = payload["position"]
    assert f"self=[{row}, {col}]" in payload["state"]


def test_verdict_mirrors_intent() -> None:
    payload = sealed()
    assert payload["verdict"] == payload["intent"]
    assert payload["intent"] in ("truth", "bluff")
