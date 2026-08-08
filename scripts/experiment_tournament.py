"""The tournament grid: the interception stack against the strong-classmate archetypes (M6-25).

The opponent grid froze the incumbent's boundary — barrier_stack converts flee_greedy
40/40 and flee_smart 0/40, oracle included, so the gap is structural rather than
perceptual. Tracing showed the structure: the flight-centroid chase ties against an
edge oscillator and the fixed tie-break mirrors it to the horizon. This grid measures
the interception stack (summed-distance chase under the shipped wall layers) against
that boundary and against two archetypes the league is likelier to field:

- **flee_deadend** — the companion repository's shipped shape (dead-end refusal, then
  distance plus mobility), i.e. what a strong classmate Thief actually runs;
- **flee_territory** — the strongest simple evader we can define: maximise the ground
  reached sooner than the Cop, the exact quantity the shrink minimises.

Run:

    uv run python scripts/experiment_tournament.py [seeds] [grid_size]

writes results/tournament_grid.json (40 seeds, negotiated board by default).
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from p2p_cop_agent.domain.movement import Action  # noqa: E402
from p2p_cop_agent.domain.scoring import Outcome  # noqa: E402
from p2p_cop_agent.orchestration.harness import run_sub_game  # noqa: E402
from p2p_cop_agent.strategy.barrier_policy import MoveIntent  # noqa: E402
from p2p_cop_agent.strategy.shrink import shrinking_turn_intent  # noqa: E402
from scripts.experiment_arena import CONFIG, SEEDS, Trace, config_with  # noqa: E402
from scripts.experiment_opponents import COP_ARMS, _decoded  # noqa: E402
from scripts.experiment_thieves import (  # noqa: E402
    flee_deadend,
    flee_greedy,
    flee_smart,
    flee_territory,
)

RESULTS = ROOT / "results"


def _shrink_stack(trace: Trace, _rng: random.Random):
    """The live stack: decoded belief feeding the interception chase under the walls."""
    memory = {"previous": None, "belief": None, "observed": None}

    def policy(cop):
        believed = _decoded(trace, memory)
        if believed is None:
            return Action.STAY
        intent = shrinking_turn_intent(cop.board, cop.position, believed,
                                       cop.barriers, memory["previous"])
        memory["previous"] = cop.position if isinstance(intent, MoveIntent) else None
        return intent
    return policy


def _oracle_shrink(trace: Trace, _rng: random.Random):
    """The shrink stack aimed with referee truth: its structural ceiling."""
    memory = {"previous": None}

    def policy(cop):
        if trace.thief is None:
            return Action.STAY
        intent = shrinking_turn_intent(cop.board, cop.position, trace.thief,
                                       cop.barriers, memory["previous"])
        memory["previous"] = cop.position if isinstance(intent, MoveIntent) else None
        return intent
    return policy


ARMS = {"barrier_stack": COP_ARMS["barrier_stack"], "shrink_stack": _shrink_stack,
        "oracle_shrink": _oracle_shrink}
THIEVES = {"random": None, "flee_greedy": flee_greedy, "flee_smart": flee_smart,
           "flee_deadend": flee_deadend, "flee_territory": flee_territory}


def play_cell(config: dict, arm: str, thief: str, seeds) -> dict:
    """Paired sub-games of one Cop arm against one Thief archetype under one config."""
    captures, scores, turns = 0, 0, 0
    for seed in seeds:
        trace = Trace(config, random.Random(seed), chooser=THIEVES[thief])
        policy = ARMS[arm](trace, random.Random(seed + 10_000))
        result = run_sub_game(config, policy, trace.thief_policy)
        captures += result.outcome is Outcome.CAPTURE
        scores += result.score.cop
        turns += result.turns
    games = len(seeds)
    return {"games": games, "captures": captures,
            "capture_rate": round(captures / games, 4),
            "mean_cop_score": round(scores / games, 2),
            "mean_turns": round(turns / games, 2)}


def tournament_grid(config: dict, seeds) -> dict:
    return {"seeds": len(seeds),
            "grid_size": config["board_and_agents"]["grid_size"],
            "arms": {arm: {thief: play_cell(config, arm, thief, seeds)
                           for thief in THIEVES} for arm in ARMS}}


def main() -> int:
    seeds = SEEDS[: int(sys.argv[1])] if len(sys.argv) > 1 else SEEDS
    config = CONFIG
    if len(sys.argv) > 2:
        config = config_with("board_and_agents", "grid_size", int(sys.argv[2]))
    payload = tournament_grid(config, seeds)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "tournament_grid.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", "utf-8")
    for arm, row in payload["arms"].items():
        cells = "  ".join(f"{thief}: {cell['captures']}/{cell['games']}"
                          for thief, cell in row.items())
        print(f"{arm:13s} {cells}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
