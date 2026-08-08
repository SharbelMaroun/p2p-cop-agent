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
from p2p_cop_agent.strategy.pursuit import step_distances  # noqa: E402


def _distance(a, b) -> int:
    return abs(a.row - b.row) + abs(a.col - b.col)

def _mobility(board, cell, blocked) -> int:
    return sum(1 for action in legal_moves(board, cell, blocked) if action is not Action.STAY)

def _territory(board, thief, cop, blocked) -> int:
    """Count the cells the thief reaches strictly before the cop — its owned ground."""
    far = board.grid_size * board.grid_size + 1
    cop_steps = step_distances(board, cop, blocked)
    return sum(1 for cell, steps in step_distances(board, thief, blocked).items()
               if steps < cop_steps.get(cell, far))


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


def flee_deadend(board, thief, cop, blocked) -> Action:
    """The companion-shaped archetype: refuse dead ends first, then distance plus mobility."""
    def rank(action: Action):
        destination = apply_move(board, thief, action, blocked)
        gain = _distance(destination, cop) + _mobility(board, destination, blocked)
        return (_mobility(board, destination, blocked) <= 1, -gain, action.name)
    return min(legal_moves(board, thief, blocked), key=rank)


def flee_territory(board, thief, cop, blocked) -> Action:
    """The tournament archetype: hold the most sooner-reached ground, then run wide."""
    def rank(action: Action):
        destination = apply_move(board, thief, action, blocked)
        gain = _distance(destination, cop) + _mobility(board, destination, blocked)
        return (-_territory(board, destination, cop, blocked), -gain, action.name)
    return min(legal_moves(board, thief, blocked), key=rank)
