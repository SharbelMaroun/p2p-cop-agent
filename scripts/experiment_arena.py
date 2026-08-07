"""The arena every experiment plays in: the opponent, and the three Cop arms.

Split out of `run_experiments.py` when that file passed the length cap. The seam is real —
this is what *playing* means, and `run_experiments.py` is what *measuring* means. Keeping
them together mixed a definition of the game with a definition of the study.

`compare_strategies.py` has an equivalent arena, but its board is bound at import to the
fixture's 7x7. A sweep changes the grid, so this one takes its board from the config under
test — otherwise the Thief walks off the edge of a board that is no longer the one being
played, which is exactly how the first sweep run failed.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p2p_cop_agent.domain.board import Board  # noqa: E402
from p2p_cop_agent.domain.movement import Action, apply_move, legal_moves  # noqa: E402
from p2p_cop_agent.domain.scoring import Outcome  # noqa: E402
from p2p_cop_agent.orchestration.harness import run_sub_game  # noqa: E402
from p2p_cop_agent.strategy.belief import Belief, scent_likelihood  # noqa: E402
from p2p_cop_agent.strategy.belief_pursuit import pursue_belief  # noqa: E402
from p2p_cop_agent.strategy.pursuit import choose_action  # noqa: E402
from p2p_cop_agent.strategy.scent_field import ScentField  # noqa: E402

# Forty seeds. The paired design means each one is a matched trial across every arm and
# every configuration, so this is the run count every table in the research report quotes.
SEEDS = tuple(range(40))
CONFIG = json.loads(
    (ROOT / "shared_contract" / "fixtures" / "match_config.example.json").read_text("utf-8"))


class Trace:
    """The opponent, and the only channel the Cop legitimately observes.

    `compare_strategies.py` has an equivalent, but its board is bound at import to the
    fixture's 7x7. A sweep changes the grid, so this one takes its board from the config
    under test — otherwise the Thief walks off the edge of a board that is no longer the
    one being played, which is exactly how the first run failed.
    """

    def __init__(self, config: dict, rng: random.Random) -> None:
        agents = config["board_and_agents"]
        self.board = Board(agents["grid_size"], agents["axis_start_index"],
                           agents["axis_origin_corner"])
        self.field = ScentField(self.board)
        self.thief: tuple[int, int] | None = None
        self.rng = rng

    def thief_policy(self, board, thief, _cop, barriers):
        """A seeded random legal walk that also emits, exactly as a real Thief would."""
        blocked = barriers.cells
        action = self.rng.choice(
            sorted(legal_moves(board, thief, blocked), key=lambda a: a.name))
        self.thief = apply_move(board, thief, action, blocked)
        self.field.advance(self.thief)  # `:917`: moving or staying creates scent
        return action


def _blind(_trace: Trace, rng: random.Random):
    def policy(cop):
        return rng.choice(sorted(legal_moves(cop.board, cop.position, cop.blocked),
                                 key=lambda a: a.name))
    return policy


def _belief(trace: Trace, _rng: random.Random):
    size = trace.board.grid_size

    def policy(cop):
        observed = trace.field.window(trace.thief) if trace.thief is not None else {}
        if not observed:
            return Action.STAY
        belief = Belief.uniform(size).updated(scent_likelihood(observed, size))
        return pursue_belief(cop.board, cop.position, belief)
    return policy


def _oracle(trace: Trace, _rng: random.Random):
    def policy(cop):
        if trace.thief is None:
            return Action.STAY
        return choose_action(cop.board, cop.position, trace.thief, cop.blocked)
    return policy


ARMS = {"blind": _blind, "belief": _belief, "oracle": _oracle}


def play(config: dict, arm: str, seeds=SEEDS) -> list[tuple[bool, int, int]]:
    """Play one arm over every seed under `config`; return (captured, turns, cop score)."""
    rows = []
    for seed in seeds:
        trace = Trace(config, random.Random(seed))
        policy = ARMS[arm](trace, random.Random(seed + 10_000))
        result = run_sub_game(config, policy, trace.thief_policy)
        rows.append((result.outcome is Outcome.CAPTURE, result.turns, result.score.cop))
    return rows


def config_with(section: str, key: str, value: object) -> dict:
    game = json.loads(json.dumps(CONFIG))
    game[section][key] = value
    return game
