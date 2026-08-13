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


def flee_interior(board, thief, cop, blocked) -> Action:
    """`uoh-ay26`'s live evader, modelled from their public `tactical_planner.py` @6e915bb.

    Their patch after losing G003 g02/g04/g06 (their regression tests name those games):
    (1) hard safety filters against capture and proximity; (2) refuse dead ends when a
    safer tier exists; (3) **hard-exclude any move with less boundary clearance than
    the best available** -- "a currently safe boundary move can still hand the Police
    an irreversible two-barrier corner trap"; (4) score survivors by escape space and
    distance. The result in live play: never voluntarily touches an edge, and the
    corner-trap capture engine loses its geometry (the 45-45 series of 2026-08-13).
    """
    def clearance(cell) -> int:
        return min(cell.row, cell.col,
                   board.grid_size - 1 - cell.row, board.grid_size - 1 - cell.col)

    options = [(action, apply_move(board, thief, action, blocked))
               for action in legal_moves(board, thief, blocked)]
    # (1) their 1000x/250x risk weights, as hard tiers: never step onto or beside the Cop.
    safe = [(a, d) for a, d in options if _distance(d, cop) >= 2] or options
    # (2) their trap filter: refuse mobility<=1 when an alternative tier exists.
    open_tier = [(a, d) for a, d in safe if _mobility(board, d, blocked) > 1] or safe
    # (3) their boundary hard-exclusion: only the maximum-clearance tier survives.
    best = max(clearance(d) for _, d in open_tier)
    interior = [(a, d) for a, d in open_tier if clearance(d) == best]
    # (4) their scoring, reduced to the surviving tier: escape space then distance.
    return min(interior, key=lambda ad: (-(_mobility(board, ad[1], blocked)
                                           + _distance(ad[1], cop)), ad[0].name))[0]


def flee_enclosure(board, thief, cop, blocked) -> Action:
    """`uoh-ay26`'s evader at `5ca6c515` -- `flee_interior` plus their G005 patch.

    Committed 2026-08-13T10:53Z, twelve minutes after losing G005 0-6, and their comment
    names the game: *"G005 g04 had a last open corridor at (3,2), but the planner
    re-entered (3,3), whose other three exits were already blocked, then STAYed until
    Police sealed the corridor."* Their fix, verbatim in shape:

        current_mobility = sum(move is not STAY for move in legal_moves(own))
        if current_mobility <= 2 and safety_pool:
            best = max(item.mobility for item in safety_pool)
            if best > current_mobility:
                keep only the moves whose mobility == best

    The placement is the whole point and is reproduced exactly: it sits **after** the
    trap filter and **before** the boundary hard-exclusion, so in an active enclosure it
    *overrides* their own boundary aversion. That is what makes it dangerous to us --
    `flee_interior` would refuse an edge cell and get sealed; this one takes the edge
    when the edge has the most exits. Our three captures all landed at step 25 with ten
    steps of slack to the horizon, so a rule that buys eleven steps converts a 20-point
    capture into a 5-point non-capture.

    Kept beside `flee_interior` rather than replacing it: the comparison between the two
    is the measurement, and overwriting the archetype we actually beat would destroy the
    baseline.
    """
    def clearance(cell) -> int:
        return min(cell.row, cell.col,
                   board.grid_size - 1 - cell.row, board.grid_size - 1 - cell.col)

    options = [(action, apply_move(board, thief, action, blocked))
               for action in legal_moves(board, thief, blocked)]
    safe = [(a, d) for a, d in options if _distance(d, cop) >= 2] or options
    open_tier = [(a, d) for a, d in safe if _mobility(board, d, blocked) > 1] or safe
    # NEW at 5ca6c515: in an active enclosure, maximise immediate open exits and let that
    # beat the boundary rule. `current_mobility` is the cell we stand on, not a destination.
    current_mobility = _mobility(board, thief, blocked)
    if current_mobility <= 2 and open_tier:
        best_mobility = max(_mobility(board, d, blocked) for _, d in open_tier)
        if best_mobility > current_mobility:
            open_tier = [(a, d) for a, d in open_tier
                         if _mobility(board, d, blocked) == best_mobility]
            return min(open_tier, key=lambda ad: (-(_mobility(board, ad[1], blocked)
                                                    + _distance(ad[1], cop)), ad[0].name))[0]
    best = max(clearance(d) for _, d in open_tier)
    interior = [(a, d) for a, d in open_tier if clearance(d) == best]
    return min(interior, key=lambda ad: (-(_mobility(board, ad[1], blocked)
                                           + _distance(ad[1], cop)), ad[0].name))[0]
