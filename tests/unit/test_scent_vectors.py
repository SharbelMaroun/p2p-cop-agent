"""`M6-19`: stored vectors guard the scent field against silent physics drift.

Rule 23 locks the scent model, and its sanction is that a deviation from the formula
**cancels the game**. The lock is a hash over the source; these are the other half — a hash
proves the file did not change, and vectors prove the *behaviour* did not.

The distinction matters because the two can move independently. A refactor that keeps the
formula and changes the emission order produces an identical formula, a different hash, and
different physics; a dependency upgrade can change floating-point accumulation with no source
change at all. Neither shows up in any test that only asserts "the field has some scent in it".

The walk **returns to its start**, which is the case worth storing. Re-emitting onto a cell
that has already decayed is where the two halves of `τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ)`
interact, and a change to either one moves the number there first.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.scent_field import DECAY_RATE, ScentField

VECTORS = json.loads(
    (pathlib.Path(__file__).resolve().parents[1] / "conformance" / "scent_field.vectors.json")
    .read_text(encoding="utf-8")
)


def replay() -> list[dict[str, float]]:
    """Re-run the stored walk against the live field."""
    board = Board(grid_size=VECTORS["board_size"], axis_start_index=0,
                  axis_origin_corner="top-left")
    field = ScentField(board=board)
    frames = []
    for row, col in VECTORS["walk"]:
        field.advance(Coordinate(row, col))
        frames.append({f"{k[0]},{k[1]}": round(v, 10)
                       for k, v in sorted(field.window(Coordinate(3, 3)).items()) if v > 0})
    return frames


def test_the_stored_decay_rate_is_the_one_the_code_uses() -> None:
    """ρ = 0.10 is the book's value (p.27/115) and rule 23 locks it. A vector file recording
    a different rate would be checking someone else's physics."""
    assert VECTORS["decay_rate"] == pytest.approx(DECAY_RATE)


@pytest.mark.parametrize("index", range(len(VECTORS["frames_after_each_step"])))
def test_each_step_reproduces_its_stored_field(index: int) -> None:
    """Parametrised per step so a failure says *when* the physics changed. "The vectors
    differ" sends someone through five frames by hand."""
    assert replay()[index] == VECTORS["frames_after_each_step"][index]


def test_the_revisited_cell_is_covered() -> None:
    """The walk ends where it began, so the final centre value is the product of four decays
    and two emissions. That number moves if either half of the formula moves."""
    assert VECTORS["walk"][0] == VECTORS["walk"][-1]
    assert VECTORS["frames_after_each_step"][-1]["3,3"] > 0


def test_the_vectors_are_not_vacuous() -> None:
    """A stored file of empty frames would pass forever. The failure mode of a golden test
    is golden data that asserts nothing."""
    frames = VECTORS["frames_after_each_step"]
    assert len(frames) == len(VECTORS["walk"])
    assert all(frame for frame in frames), "a frame carries no scent at all"
    assert len({json.dumps(f, sort_keys=True) for f in frames}) > 1, "every frame is identical"
