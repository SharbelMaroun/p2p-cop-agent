"""Phase-C v5 additive-barrier matrix: contain_add vs denial (structural pursuit gap).

Paired, identical scenarios: both arms play the SAME starts, quota, horizon, evader and
seed; only the chooser differs. Perfect-localization first (the oracle arm feeds the true
Thief cell every turn) so belief quality cannot hide or invent the structural effect.

    uv run python scripts/experiment_contain.py [mode] [seeds]

mode `perfect` (default) sweeps the 24 perimeter openings -- the development gate.
mode `holdout` sweeps `seeds` unseen random start pairs (default 100) on a disjoint seed
stream -- run once, only after PASS, never tuned against.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from p2p_cop_agent.domain.board import Board  # noqa: E402
from p2p_cop_agent.domain.movement import Action  # noqa: E402
from p2p_cop_agent.domain.scoring import Outcome  # noqa: E402
from p2p_cop_agent.orchestration.harness import run_sub_game  # noqa: E402
from p2p_cop_agent.strategy.barrier_policy import MoveIntent  # noqa: E402
from p2p_cop_agent.strategy.contain_add import contain_add_turn_intent  # noqa: E402
from p2p_cop_agent.strategy.denial import denial_turn_intent  # noqa: E402
from scripts.experiment_arena import CONFIG, Trace, config_with  # noqa: E402
from scripts.experiment_foreign import openings  # noqa: E402
from scripts.experiment_thieves import (  # noqa: E402
    flee_deadend,
    flee_enclosure,
    flee_greedy,
    flee_interior,
    flee_smart,
    flee_territory,
)

RESULTS = ROOT / "results"
ARMS = {"denial": denial_turn_intent, "contain_add": contain_add_turn_intent}
THIEVES = {"flee_greedy": flee_greedy, "flee_smart": flee_smart,
           "flee_deadend": flee_deadend, "flee_territory": flee_territory,
           "flee_interior": flee_interior, "flee_enclosure": flee_enclosure}
BOARD = Board(CONFIG["board_and_agents"]["grid_size"],
              CONFIG["board_and_agents"]["axis_start_index"],
              CONFIG["board_and_agents"]["axis_origin_corner"])


def oracle_policy(chooser, trace: Trace):
    """A Cop arm fed the true Thief cell every turn (perfect localization)."""
    memory = {"previous": None}

    def policy(cop):
        if trace.thief is None:
            return Action.STAY
        intent = chooser(cop.board, cop.position, trace.thief, cop.barriers, memory["previous"])
        memory["previous"] = cop.position if isinstance(intent, MoveIntent) else None
        return intent
    return policy


def _starts(mode: str, count: int):
    """Return the paired start pairs (cop_start, thief_start) both arms share."""
    if mode == "perfect":
        thief = CONFIG["board_and_agents"]["thief_start"]
        return [(list(s), thief) for s in openings(BOARD) if list(s) != thief]
    size = BOARD.grid_size
    cells = [(r, c) for r in range(size) for c in range(size)]
    # Disjoint seed stream from every earlier experiment: these starts are unseen.
    pairs, rng = [], random.Random(0x5EED5)
    while len(pairs) < count:
        cop, thief = rng.choice(cells), rng.choice(cells)
        if abs(cop[0] - thief[0]) + abs(cop[1] - thief[1]) >= 3:
            pairs.append((list(cop), list(thief)))
    return pairs


def play_cell(arm: str, thief_name: str, starts) -> dict:
    """One arm against one evader over the shared start list, perfect localization."""
    captures = turns = 0
    for cop_start, thief_start in starts:
        config = config_with("board_and_agents", "cop_start", cop_start)
        config["board_and_agents"]["thief_start"] = thief_start
        trace = Trace(config, random.Random(0), chooser=THIEVES[thief_name])
        result = run_sub_game(config, oracle_policy(ARMS[arm], trace), trace.thief_policy)
        captures += result.outcome is Outcome.CAPTURE
        turns += result.turns
    return {"games": len(starts), "captures": captures,
            "mean_turns": round(turns / len(starts), 2)}


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "perfect"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    starts = _starts(mode, count)
    grid = {arm: {t: play_cell(arm, t, starts) for t in THIEVES} for arm in ARMS}
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"contain_add_{mode}.json").write_text(
        json.dumps({"mode": mode, "localization": "perfect", "starts": len(starts),
                    "arms": grid}, indent=2, sort_keys=True) + "\n", "utf-8")
    print(f"perfect-localization {mode} ({len(starts)} starts)")
    print(f"{'thief':16s}" + "  ".join(f"{a:>13s}" for a in ARMS) + "   delta")
    for t in THIEVES:
        cells = "  ".join(f"{grid[a][t]['captures']:>4}/{grid[a][t]['games']:<7}" for a in ARMS)
        delta = grid["contain_add"][t]["captures"] - grid["denial"][t]["captures"]
        print(f"{t:16s}{cells}   {delta:+d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
