"""The Thief archetypes the opponent grid measures against (M9-30).

Both deterministic, both emitting through the arena's `Trace` so only the brain
differs. They read the Cop's true cell — the harness is a referee and may hand it to
a test double; `[AE-8]` binds the *agents*, not the instruments.

- **flee-greedy** — maximise Manhattan distance from the Cop: the reference
  simulator's own `ThiefBrain` shape, and the likeliest classmate default.
- **flee-smart** — distance *plus* onward mobility, refusing the corners a pure
  distance-maximiser backs into: the strong-classmate shape, and the measured
  structural boundary no Cop arm corners (the truth-aimed stack included).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from p2p_cop_agent.domain.movement import Action, apply_move, legal_moves  # noqa: E402


def _distance(a, b) -> int:
    return abs(a.row - b.row) + abs(a.col - b.col)

def _mobility(board, cell, blocked) -> int:
    return sum(1 for action in legal_moves(board, cell, blocked) if action is not Action.STAY)


def flee_greedy(board, thief, cop, blocked) -> Action:
    """The reference archetype: the legal step that maximises distance from the Cop."""
    return min(
        legal_moves(board, thief, blocked),
        key=lambda action: (-_distance(apply_move(board, thief, action, blocked), cop),
                            action.name),
    )


def flee_smart(board, thief, cop, blocked) -> Action:
    """The strong-classmate archetype: distance plus mobility, summed not ranked."""
    def rank(action: Action):
        destination = apply_move(board, thief, action, blocked)
        return (-(_distance(destination, cop) + _mobility(board, destination, blocked)),
                action.name)
    return min(legal_moves(board, thief, blocked), key=rank)
