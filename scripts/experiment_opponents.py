"""The opponent grid: every Cop arm against every Thief archetype (M9-30).

The forty-seed arena measured three Cop arms against **one** opponent — a seeded
random walk. That is the weakest plausible Thief, and a capture rate earned against
it says nothing about the league: the companion repository's evasion escapes a
current-cell pursuer 23 times in 24. So the opponent model was the untested half of
every published Cop number, exactly the "one Cop" threat its own research report
records from the other side.

Two stronger archetypes join the walk, both deterministic, both emitting through the
same `Trace` machinery so only the brain differs:

- **flee-greedy** — steps to maximise Manhattan distance from the Cop's cell: the
  reference simulator's own `ThiefBrain` shape, and the likeliest classmate default.
- **flee-smart** — maximises distance *plus* onward mobility, refusing corners a pure
  distance-maximiser backs into: the strong-classmate shape.

Both read the Cop's true cell — the harness is a referee and may hand it to a test
double `[AE-8]` binds the *agents*, not the instruments. Run:

    uv run python scripts/experiment_opponents.py     # writes results/opponent_grid.json
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from p2p_cop_agent.domain.movement import Action, apply_move, legal_moves  # noqa: E402
from p2p_cop_agent.domain.scoring import Outcome  # noqa: E402
from p2p_cop_agent.orchestration.harness import run_sub_game  # noqa: E402
from p2p_cop_agent.strategy.anticipation import (  # noqa: E402
    anticipating_action,
    predictive_turn_intent,
)
from p2p_cop_agent.strategy.belief import Belief, scent_likelihood  # noqa: E402
from p2p_cop_agent.strategy.belief_pursuit import pursue_belief  # noqa: E402
from scripts.experiment_arena import ARMS, CONFIG, SEEDS, Trace  # noqa: E402

RESULTS = ROOT / "results"


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


def _believed(trace: Trace, cop, carried: dict | None = None):
    """The belief argmax, rebuilt fresh per observation, carried only across silence.

    The Bayes-recursive variant was measured here and reverted: with no motion model
    in the likelihood, the carried prior calcifies on the trail's history and the
    argmax stops tracking — flee_greedy went from 40/40 captures to 0/40 on nothing
    but that change. The live loop follows the same fresh-per-observation rule.
    """
    from p2p_cop_agent.domain.coordinates import Coordinate  # noqa: PLC0415

    observed = trace.field.window(trace.thief) if trace.thief is not None else {}
    if observed:
        belief = Belief.uniform(trace.board.grid_size).updated(
            scent_likelihood(observed, trace.board.grid_size))
        if carried is not None:
            carried["belief"] = belief
    elif carried is not None and carried.get("belief") is not None:
        belief = carried["belief"]
    else:
        return None
    return Coordinate.from_pair(belief.most_likely())


def _anticipating(trace: Trace, _rng: random.Random):
    """The belief arm with the predictive aim: chase the flight set, not the sighting."""
    def policy(cop):
        believed = _believed(trace, cop)
        if believed is None:
            return Action.STAY
        return anticipating_action(cop.board, cop.position, believed, cop.blocked)
    return policy


def _barrier_stack(trace: Trace, _rng: random.Random):
    """The live stack: trap, squeeze, ratchet, or predictively chase.

    This is what `orchestration/live_policy.py` actually serves. Every barrier-free
    arm captures a fleeing archetype 0/40, so this arm is the one whose number is a
    league expectation rather than a random-walk artifact. `previous` mirrors the
    live loop's own memory of the cell it just vacated — the containment ratchet.
    """
    memory = {"previous": None, "belief": None}

    def policy(cop):
        believed = _believed(trace, cop, memory)
        if believed is None:
            return Action.STAY
        intent = predictive_turn_intent(cop.board, cop.position, believed,
                                        cop.barriers, memory["previous"])
        from p2p_cop_agent.strategy.barrier_policy import MoveIntent  # noqa: PLC0415

        memory["previous"] = cop.position if isinstance(intent, MoveIntent) else None
        return intent
    return policy


def _oracle_stack(trace: Trace, _rng: random.Random):
    """The barrier stack aimed with referee truth: separates belief lag from structure."""
    memory = {"previous": None}

    def policy(cop):
        if trace.thief is None:
            return Action.STAY
        believed = trace.thief
        intent = predictive_turn_intent(cop.board, cop.position, believed,
                                        cop.barriers, memory["previous"])
        from p2p_cop_agent.strategy.barrier_policy import MoveIntent  # noqa: PLC0415

        memory["previous"] = cop.position if isinstance(intent, MoveIntent) else None
        return intent
    return policy


COP_ARMS = {"belief": ARMS["belief"], "anticipating": _anticipating,
            "barrier_stack": _barrier_stack, "oracle": ARMS["oracle"],
            "oracle_stack": _oracle_stack}
THIEVES = {"random": None, "flee_greedy": flee_greedy, "flee_smart": flee_smart}


def play_cell(arm: str, thief: str, seeds=SEEDS) -> dict:
    """Forty paired sub-games of one Cop arm against one Thief archetype."""
    captures, scores, turns = 0, 0, 0
    for seed in seeds:
        trace = Trace(CONFIG, random.Random(seed), chooser=THIEVES[thief])
        policy = COP_ARMS[arm](trace, random.Random(seed + 10_000))
        result = run_sub_game(CONFIG, policy, trace.thief_policy)
        captures += result.outcome is Outcome.CAPTURE
        scores += result.score.cop
        turns += result.turns
    games = len(seeds)
    return {"games": games, "captures": captures,
            "capture_rate": round(captures / games, 4),
            "mean_cop_score": round(scores / games, 2),
            "mean_turns": round(turns / games, 2)}


def opponent_grid() -> dict:
    """The full grid; `pursue_belief` is imported so the belief arm is the shipped one."""
    assert pursue_belief is not None
    grid = {arm: {thief: play_cell(arm, thief) for thief in THIEVES} for arm in COP_ARMS}
    return {"seeds": len(SEEDS), "arms": grid}


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    payload = opponent_grid()
    (RESULTS / "opponent_grid.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", "utf-8")
    for arm, row in payload["arms"].items():
        cells = "  ".join(f"{thief}: {cell['captures']}/{cell['games']}"
                          for thief, cell in row.items())
        print(f"{arm:13s} {cells}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
