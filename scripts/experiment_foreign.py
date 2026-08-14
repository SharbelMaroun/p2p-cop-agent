"""Does the Cop still see when the Thief's scent is not *our* scent? (M11-01)

Every arena in this repo hands the Cop a window produced by `ScentField` -- our own
emitter -- so `emitter_decoder`, which inverts exactly that model, localises perfectly by
construction. That is why the tournament grid reads 40/40 against every archetype while
live play produced a near-identical blind move sequence in every counted sub-game against
both opponents. The instrument could not express the failure it was meant to measure.

This arena fixes the instrument. The Thief emits through **foreign** models -- a peer's
legitimate but different reading of the same book -- and the Cop observes through the real
`orchestration.live_observation.observe`, the same call the wire path makes. The arm is
the live stack: observe, `patrol.aim`, `denial_turn_intent`. Nothing is fed truth.

    uv run python scripts/experiment_foreign.py        # writes results/foreign_grid.json
"""

from __future__ import annotations

import json
import sys
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from p2p_cop_agent.domain.board import Board  # noqa: E402
from p2p_cop_agent.domain.coordinates import Coordinate  # noqa: E402
from p2p_cop_agent.domain.movement import Action, apply_move  # noqa: E402
from p2p_cop_agent.domain.scoring import Outcome  # noqa: E402
from p2p_cop_agent.orchestration.harness import run_sub_game  # noqa: E402
from p2p_cop_agent.orchestration.live_observation import observe  # noqa: E402
from p2p_cop_agent.protocol.scent_wire import encode_scent  # noqa: E402
from p2p_cop_agent.strategy.barrier_policy import MoveIntent  # noqa: E402
from p2p_cop_agent.strategy.belief import Belief  # noqa: E402
from p2p_cop_agent.strategy.denial import denial_turn_intent  # noqa: E402
from p2p_cop_agent.strategy.patrol import aim  # noqa: E402
from scripts.experiment_arena import CONFIG, config_with  # noqa: E402
from scripts.experiment_emitters import EMITTERS  # noqa: E402
from scripts.experiment_thieves import (  # noqa: E402
    flee_deadend,
    flee_greedy,
    flee_interior,
    flee_smart,
    flee_territory,
)

RESULTS = ROOT / "results"
THIEVES = {"flee_greedy": flee_greedy, "flee_smart": flee_smart,
           "flee_deadend": flee_deadend, "flee_territory": flee_territory,
           "flee_interior": flee_interior}


def openings(board: Board) -> tuple[tuple[int, int], ...]:
    """Return the Cop starts a trial sweeps: every perimeter cell of the board.

    Seeds are not variety here -- a deterministic archetype replays the identical game
    for all forty of them (`experiment_arena.SEEDS`). The opening is the real degree of
    freedom, so it is what varies.
    """
    low, high = board.min_index, board.max_index
    edge = range(low, high + 1)
    return tuple(dict.fromkeys(
        [(low, c) for c in edge] + [(high, c) for c in edge]
        + [(r, low) for r in edge] + [(r, high) for r in edge]))


class ForeignTrace:
    """The opponent: it moves, then publishes a window through a foreign emitter."""

    def __init__(self, config: dict, chooser, emitter) -> None:
        agents = config["board_and_agents"]
        self.board = Board(agents["grid_size"], agents["axis_start_index"],
                           agents["axis_origin_corner"])
        self.emitter = emitter(self.board)
        self.chooser = chooser
        self.thief: Coordinate | None = None

    def thief_policy(self, board, thief, cop, barriers) -> Action:
        action = self.chooser(board, thief, cop, barriers.cells)
        self.thief = apply_move(board, thief, action, barriers.cells)
        self.emitter.advance(self.thief)
        return action

    def incoming(self) -> dict | None:
        """Return the wire message the Cop would have received this turn."""
        if self.thief is None:
            return None
        return {"smell_grid": encode_scent(self.emitter.window(self.thief))}


def live_stack(trace: ForeignTrace, board: Board, observation=observe, chooser=None,
               *, wants_belief: bool = False):
    """The arm the wire actually serves: observe, aim, then the configured chooser.

    `chooser` defaults to the shipped `denial_turn_intent`; passing
    `strategy.engine.engine_turn_intent` measures the search through the same live path.
    A `wants_belief` chooser (the Phase-B robust arm) is additionally handed the full
    belief and its own carried reachable set -- the one arm that plans against the whole
    plausible set rather than the argmax `target` that every other chooser receives.
    """
    choose = chooser or denial_turn_intent
    state = {"belief": Belief.uniform(board.grid_size, start=board.min_index),
             "seen": None, "count": 0, "previous": None, "reachable": None}

    def policy(cop):
        state["count"] += 1
        fresh = observation(board, trace.incoming(), state["count"], state["seen"],
                            cop.position)
        if fresh is not None:
            state["belief"], state["seen"] = fresh
        seen_turn = state["seen"][0] if state["seen"] else None
        target = aim(board, state["belief"], seen_turn, state["count"], cop.position)
        if wants_belief:
            intent, state["reachable"] = choose(
                board, cop.position, target, cop.barriers, state["previous"],
                belief=state["belief"], reachable=state["reachable"])
        else:
            intent = choose(board, cop.position, target, cop.barriers, state["previous"])
        state["previous"] = cop.position if isinstance(intent, MoveIntent) else None
        return intent
    return policy


def play_cell(emitter_name: str, thief_name: str, observation=observe, chooser=None,
              *, wants_belief: bool = False) -> dict:
    """One trial: every perimeter opening, one emitter, one Thief archetype."""
    board = Board(CONFIG["board_and_agents"]["grid_size"],
                  CONFIG["board_and_agents"]["axis_start_index"],
                  CONFIG["board_and_agents"]["axis_origin_corner"])
    captures, turns = 0, 0
    starts = openings(board)
    for start in starts:
        if list(start) == CONFIG["board_and_agents"]["thief_start"]:
            continue
        config = config_with("board_and_agents", "cop_start", list(start))
        trace = ForeignTrace(config, THIEVES[thief_name], EMITTERS[emitter_name])
        result = run_sub_game(
            config, live_stack(trace, board, observation, chooser, wants_belief=wants_belief),
            trace.thief_policy)
        captures += result.outcome is Outcome.CAPTURE
        turns += result.turns
    games = sum(1 for s in starts if list(s) != CONFIG["board_and_agents"]["thief_start"])
    return {"games": games, "captures": captures,
            "capture_rate": round(captures / games, 4),
            "mean_turns": round(turns / games, 2)}


def _chooser(name: str):
    """Resolve a CLI chooser name to `(callable, wants_belief)`; robust arms plan on a set."""
    if name == "denial":
        return denial_turn_intent, False
    from p2p_cop_agent.strategy.robust_pursuit import robust_turn_intent  # noqa: PLC0415
    return partial(robust_turn_intent, aggregation=name.removeprefix("robust_")), True


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    name = sys.argv[1] if len(sys.argv) > 1 else "denial"
    chooser, wants_belief = _chooser(name)
    grid = {emitter: {thief: play_cell(emitter, thief, chooser=chooser,
                                       wants_belief=wants_belief) for thief in THIEVES}
            for emitter in EMITTERS}
    tag = "" if name == "denial" else f"_{name}"
    (RESULTS / f"foreign_grid{tag}.json").write_text(
        json.dumps({"chooser": name, "emitters": grid}, indent=2, sort_keys=True) + "\n",
        "utf-8")
    print(f"{'emitter':16s}" + "  ".join(f"{n:>14s}" for n in THIEVES) + f"   [{name}]")
    for emitter, row in grid.items():
        cells = "  ".join(f"{cell['captures']:>7d}/{cell['games']:<6d}"
                          for cell in row.values())
        print(f"{emitter:16s}{cells}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
