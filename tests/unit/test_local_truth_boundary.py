"""`M8-01d`: the objective board is not merely undisplayed — it is unrepresentable.

The most expensive rule in the project sits here. Rule 9 (Prohibited): "Do not display the
full objective board state in the live user interface. Sanction: **Project disqualification**
due to unfair advantage." Not a lost game — the project. Rule 8 adds "display true local
information only", sanction "disqualification due to data breach".

**Why the field set is pinned by a test.** Our own process legitimately holds the
opponent's revealed positions once the audit runs, so a screen that renders "what the
runtime has" would leak them while looking like ordinary code. The failure is silent, the
sanction is terminal, and no screenshot taken afterwards can prove what was on screen
during the match. The only durable defence is that there is nowhere to put the value —
so the test that matters here is the one that fails when someone adds a field.

`:1647`: each interface shows "only the information accessible to it … and never the full
objective board state. There is no 'bird's-eye view' showing the positions of both sides."
"""

from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

import pytest

from p2p_cop_agent.live import LocalTruth, TurnState, frame_of, local_truth

SRC = Path(__file__).resolve().parents[2] / "src" / "p2p_cop_agent"

# Every name the screen is allowed to know. Each is something this agent observed or was
# told; none can hold where the opponent actually is.
PERMITTED_FIELDS = {
    "grid_size", "own_position", "turn_state", "step",
    "disclosed_barriers", "visited", "belief", "hints", "score",
}


def _truth(**overrides) -> LocalTruth:
    base = {"grid_size": 4, "own_position": (0, 0),
            "turn_state": TurnState.YOUR_TURN, "step": 1}
    return local_truth(**{**base, **overrides})


def test_the_snapshot_carries_exactly_the_permitted_fields_and_no_others() -> None:
    """**The test this module exists for.** Adding a field to `LocalTruth` fails here, which
    is the point: a new field is exactly how the opponent's position would arrive."""
    actual = {f.name for f in dataclasses.fields(LocalTruth)}
    assert actual == PERMITTED_FIELDS, (
        "the live snapshot's field set changed; rule 9's sanction is project "
        f"disqualification, so justify each addition. Added: {actual - PERMITTED_FIELDS}, "
        f"removed: {PERMITTED_FIELDS - actual}"
    )


def test_no_field_name_suggests_objective_or_opponent_state() -> None:
    """A weaker check than the one above, kept because it catches the *plausible* mistake:
    a field named for the opponent that someone adds believing it holds a belief."""
    forbidden = ("opponent", "thief_position", "true_", "actual_", "objective", "real_")
    for field in dataclasses.fields(LocalTruth):
        assert not any(word in field.name for word in forbidden), field.name


def test_the_snapshot_is_frozen_so_a_widget_cannot_write_into_it() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        _truth().own_position = (1, 1)  # type: ignore[misc]


def test_the_builder_is_keyword_only_so_nothing_is_passed_positionally() -> None:
    """Positional arguments are how a wrong value slides into the right slot. Naming every
    piece of information the screen is given makes an over-share a visible edit."""
    with pytest.raises(TypeError):
        local_truth(4, (0, 0), TurnState.YOUR_TURN, 1)  # type: ignore[misc]


def test_the_live_package_never_imports_the_runtime_or_the_opponents_state() -> None:
    """Structural, because a single import is all it would take. The live view-model may
    depend on nothing that knows where the opponent is — not the peer runtime, not the
    orchestration layer, not the protocol's audit reveal."""
    allowed = ("p2p_cop_agent.live",)
    for module in sorted((SRC / "live").glob("*.py")):
        tree = ast.parse(module.read_text("utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("p2p_cop"):
                assert (node.module or "").startswith(allowed), (
                    f"{module.name} imports {node.module}; the live view must not be able "
                    "to reach objective state [AE-8] [AE-9]"
                )


def test_the_widget_layer_imports_only_the_view_model() -> None:
    """The same boundary one layer out: the window may not bypass the snapshot.

    `ui.style` is admitted alongside the view model because it is chrome — colours
    and canvas geometry — and the next test pins that it stays chrome: a style module
    that imported any project code could smuggle exactly what this boundary refuses.
    """
    allowed = ("p2p_cop_agent.live", "p2p_cop_agent.ui.style")
    tree = ast.parse((SRC / "ui" / "live_app.py").read_text("utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("p2p_cop"):
            assert (node.module or "").startswith(allowed), node.module


def test_the_style_module_is_stateless_chrome() -> None:
    """The admission above is safe only while style imports nothing of the project."""
    tree = ast.parse((SRC / "ui" / "style.py").read_text("utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert not (node.module or "").startswith("p2p_cop"), node.module
        if isinstance(node, ast.Import):
            assert all(not alias.name.startswith("p2p_cop") for alias in node.names)


# --- what the screen may show is a belief, never a truth ---------------------------------


def test_the_marked_cell_is_our_inference_not_a_reported_position() -> None:
    """`most_likely` is what *we* think, computed from our own belief. Rules 8 and 9 forbid
    displaying the opponent's truth; they do not forbid displaying a guess — that guess is
    the entire purpose of the trust map (`:1660`)."""
    truth = _truth(belief={(0, 1): 0.1, (2, 2): 0.7, (3, 3): 0.2})
    assert truth.most_likely == (2, 2)
    assert frame_of(truth).at((2, 2)).mark == "T?"


def test_an_empty_belief_marks_nothing_rather_than_guessing() -> None:
    """Before any evidence there is no inference to draw, and inventing one would put a
    mark on the board that no observation supports."""
    truth = _truth()
    assert truth.most_likely is None
    assert all(view.mark in ("", "C") for view in frame_of(truth).cells)


def test_a_position_off_the_board_is_refused() -> None:
    """A snapshot describing an impossible board is a bug upstream, and rendering it would
    put our own marker somewhere the game does not have."""
    with pytest.raises(ValueError, match="off a 4x4 board"):
        _truth(own_position=(9, 9))
    with pytest.raises(ValueError, match="grid_size must be positive"):
        _truth(grid_size=0)
