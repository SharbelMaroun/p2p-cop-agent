"""Holdout benchmark for the robust-pursuit work (cop competitive optimization v2).

Phase A measurement: no strategy behaviour changes here. It plays the shipped choosers
(and the Phase-B robust arm) through the live `M6-24` decode -- decoded belief, never
truth -- against a wider evader panel than the tournament grid, including the two modelled
`uoh-ay26` brains and seeded stochastic wrappers the stack was never tuned against, and
across **swept start cells** so a deterministic evader is measured as many scenarios
rather than one game repeated (the grid's real overfit).

Run::

    uv run python scripts/experiment_robust.py [seeds] [arms] [fixed]

`arms` is a comma list from {denial,engine,robust_worst,robust_expected,robust_lcb}
(default denial). A third arg `fixed` pins the real-game start as a regression scenario.
Writes results/robust_holdout_<arms>.json. `engine` is slow; keep its seed count low.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from p2p_cop_agent.domain.movement import Action, legal_moves  # noqa: E402
from p2p_cop_agent.domain.scoring import Outcome  # noqa: E402
from p2p_cop_agent.orchestration.harness import run_sub_game  # noqa: E402
from p2p_cop_agent.strategy.barrier_policy import MoveIntent  # noqa: E402
from scripts.experiment_arena import CONFIG, SEEDS, Trace, config_with  # noqa: E402
from scripts.experiment_opponents import _decoded  # noqa: E402
from scripts.experiment_thieves import (  # noqa: E402
    flee_deadend,
    flee_enclosure,
    flee_greedy,
    flee_interior,
    flee_smart,
    flee_territory,
)

RESULTS = ROOT / "results"

# Deterministic panel (`None` = the arena's seeded random walk) plus stochastic wrappers.
DETERMINISTIC = {
    "random": None, "flee_greedy": flee_greedy, "flee_smart": flee_smart,
    "flee_deadend": flee_deadend, "flee_territory": flee_territory,
    "flee_interior": flee_interior, "flee_enclosure": flee_enclosure,
}


def _stochastic(base, epsilon: float):
    """`base`, but a seeded random legal step `epsilon` of the time (real agents are noisy)."""
    def make(seed: int):
        rng = random.Random(seed ^ 0x5EED)

        def chooser(board, thief, cop, blocked) -> Action:
            options = sorted(legal_moves(board, thief, blocked), key=lambda a: a.name)
            return rng.choice(options) if rng.random() < epsilon else base(
                board, thief, cop, blocked)
        return chooser
    return make


THIEVES = {name: (lambda c: (lambda _s: c))(chooser)
           for name, chooser in DETERMINISTIC.items()}
THIEVES["stochastic_smart"] = _stochastic(flee_smart, 0.15)
THIEVES["stochastic_territory"] = _stochastic(flee_territory, 0.15)


def _intent_fn(arm: str, horizon: int):
    """Return `(chooser, wants_belief)` for an arm; robust arms consume the belief set."""
    if arm == "denial":
        from p2p_cop_agent.strategy.denial import denial_turn_intent  # noqa: PLC0415
        return denial_turn_intent, False
    if arm == "engine":
        from functools import partial  # noqa: PLC0415

        from p2p_cop_agent.strategy.engine import engine_turn_intent  # noqa: PLC0415
        return partial(engine_turn_intent, horizon=horizon), False
    from functools import partial  # noqa: PLC0415

    from p2p_cop_agent.strategy.robust_pursuit import robust_turn_intent  # noqa: PLC0415
    return partial(robust_turn_intent, aggregation=arm.removeprefix("robust_")), True


def _build_arm(arm: str, horizon: int):
    """A per-match cop policy for `arm`, decoding belief exactly as the live loop does."""
    choose, wants_belief = _intent_fn(arm, horizon)

    def build(trace: Trace):
        memory = {"previous": None, "belief": None, "observed": None, "reachable": None}

        def policy(cop):
            believed = _decoded(trace, memory)
            if believed is None:
                return Action.STAY
            if wants_belief:
                intent, memory["reachable"] = choose(
                    cop.board, cop.position, believed, cop.barriers, memory["previous"],
                    belief=memory["belief"], reachable=memory["reachable"])
            else:
                intent = choose(cop.board, cop.position, believed,
                                cop.barriers, memory["previous"])
            memory["previous"] = cop.position if isinstance(intent, MoveIntent) else None
            return intent
        return policy
    return build


def _seeded_config(seed: int) -> dict:
    """A config with `seed`-drawn start cells (kept >=3 apart), so trials are new scenarios."""
    rng = random.Random(seed ^ 0xC0FFEE)
    size = CONFIG["board_and_agents"]["grid_size"]
    cells = [(r, c) for r in range(size) for c in range(size)]
    while True:
        cop, thief = rng.choice(cells), rng.choice(cells)
        if abs(cop[0] - thief[0]) + abs(cop[1] - thief[1]) >= 3:
            break
    game = config_with("board_and_agents", "cop_start", list(cop))
    game["board_and_agents"]["thief_start"] = list(thief)
    return game


def play_cell(build, thief: str, seeds, *, sweep_starts: bool) -> dict:
    """Paired sub-games of one prebuilt Cop arm against one evader factory."""
    captures, scores, turns = 0, 0, 0
    for seed in seeds:
        config = _seeded_config(seed) if sweep_starts else CONFIG
        trace = Trace(config, random.Random(seed), chooser=THIEVES[thief](seed))
        result = run_sub_game(config, build(trace), trace.thief_policy)
        captures += result.outcome is Outcome.CAPTURE
        scores += result.score.cop
        turns += result.turns
    games = len(seeds)
    return {"games": games, "captures": captures,
            "capture_rate": round(captures / games, 4),
            "mean_cop_score": round(scores / games, 2),
            "mean_turns": round(turns / games, 2)}


def run(arms, seeds, horizon: int, *, sweep_starts: bool) -> dict:
    grid = {arm: {thief: play_cell(_build_arm(arm, horizon), thief, seeds,
                                   sweep_starts=sweep_starts) for thief in THIEVES}
            for arm in arms}
    return {"seeds": len(seeds), "grid_size": CONFIG["board_and_agents"]["grid_size"],
            "sweep_starts": sweep_starts, "arms": grid}


def main() -> int:
    seeds = SEEDS[: int(sys.argv[1])] if len(sys.argv) > 1 else SEEDS
    arms = sys.argv[2].split(",") if len(sys.argv) > 2 else ["denial"]
    sweep_starts = not (len(sys.argv) > 3 and sys.argv[3] == "fixed")
    horizon = int(CONFIG["movement_and_barriers"]["survival_threshold"])
    payload = run(arms, seeds, horizon, sweep_starts=sweep_starts)
    RESULTS.mkdir(exist_ok=True)
    tag = "_".join(arms) + ("" if sweep_starts else "_fixed")
    out = RESULTS / f"robust_holdout_{tag}.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", "utf-8")
    print(f"{'arm':<16}" + "  ".join(f"{t[:9]:>9}" for t in THIEVES))
    for arm, row in payload["arms"].items():
        cells = "  ".join(f"{row[t]['captures']:>4}/{row[t]['games']:<4}" for t in THIEVES)
        print(f"{arm:<16}{cells}")
    print(f"\nwrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
