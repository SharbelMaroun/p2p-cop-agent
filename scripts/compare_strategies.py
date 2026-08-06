"""M6-20/M6-20a: does belief-driven pursuit actually beat a blind Cop?

`inst/police_thief_p2p_Summary.md:3115` requires the report to present "the empirical
evidence for their success". It specifies **no** run count, seeds, significance test, or
baseline -- the "shipped heuristic" appears only as a config comment (`:3028`) meaning
the bundled default when you supply no brain. The protocol is therefore ours, and lives
in full in `docs/PRD_strategy.md` so the number can be reproduced or disputed.

In short: 7x7 at the negotiated fixture, survival threshold 35, seeds 0-29, and one
fixed opponent -- a seeded random legal walk that does not react to the Cop, so for a
given seed **every arm faces the identical Thief trajectory**. That makes the result a
paired comparison rather than two averages. The Cop observes the real channel: the
Thief's emission advances a `ScentField` and the Cop reads the 5x5 window `M6-08` puts
on the wire.

Arms: `blind` (seeded random legal move -- no scent, no belief), `belief` (what we ship),
and `oracle` (`choose_action` against the true cell). The oracle is **not a legal agent**;
it is the ceiling, so a reader sees how much of the available gap belief closes rather
than only that it beat random.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from p2p_cop_agent.domain.actions import Action  # noqa: E402
from p2p_cop_agent.domain.board import Board  # noqa: E402
from p2p_cop_agent.domain.movement import apply_move, legal_moves  # noqa: E402
from p2p_cop_agent.domain.scoring import Outcome  # noqa: E402
from p2p_cop_agent.orchestration.harness import run_sub_game  # noqa: E402
from p2p_cop_agent.strategy.belief import Belief, scent_likelihood  # noqa: E402
from p2p_cop_agent.strategy.belief_pursuit import pursue_belief  # noqa: E402
from p2p_cop_agent.strategy.pursuit import choose_action  # noqa: E402
from p2p_cop_agent.strategy.scent_field import ScentField  # noqa: E402

CONFIG_FIXTURE = Path(__file__).resolve().parents[1] / "shared_contract" / "fixtures"
CONFIG: dict = json.loads((CONFIG_FIXTURE / "match_config.example.json").read_text("utf-8"))
GRID = CONFIG["board_and_agents"]["grid_size"]
THRESHOLD = CONFIG["movement_and_barriers"]["survival_threshold"]
SEEDS = tuple(range(30))
# Start the two sides at opposite corners. The fixture puts the Thief mid-board, which
# would hand every arm a short chase and compress the differences we are measuring.
CONFIG["board_and_agents"] = {**CONFIG["board_and_agents"], "cop_start": [6, 6],
                              "thief_start": [0, 0]}
BOARD = Board(GRID, CONFIG["board_and_agents"]["axis_start_index"],
              CONFIG["board_and_agents"]["axis_origin_corner"])


class Trace:
    """Shared per-match state: the Thief's emission, and its cell for the oracle arm."""

    def __init__(self, rng: random.Random) -> None:
        self.field = ScentField(BOARD)
        self.thief = None
        self.rng = rng

    def thief_policy(self, board, thief, _cop, barriers):
        """A seeded random legal walk that also emits, exactly as a real Thief would."""
        blocked = barriers.cells
        action = self.rng.choice(sorted(legal_moves(board, thief, blocked), key=lambda a: a.name))
        self.thief = apply_move(board, thief, action, blocked)
        self.field.advance(self.thief)  # `:917`: moving or staying creates scent
        return action


def _blind(rng: random.Random):
    def policy(cop):
        return rng.choice(sorted(legal_moves(cop.board, cop.position, cop.blocked),
                                 key=lambda a: a.name))
    return policy


def _belief(trace: Trace):
    def policy(cop):
        observed = trace.field.window(trace.thief) if trace.thief is not None else {}
        if not observed:
            return Action.STAY
        belief = Belief.uniform(GRID).updated(scent_likelihood(observed, GRID))
        return pursue_belief(cop.board, cop.position, belief)
    return policy


def _oracle(trace: Trace):
    def policy(cop):
        if trace.thief is None:
            return Action.STAY
        return choose_action(cop.board, cop.position, trace.thief, cop.blocked)
    return policy


ARMS = {"blind": _blind, "belief": _belief, "oracle": _oracle}


def run_arm(name: str, seeds=SEEDS) -> list[tuple[bool, int, int]]:
    """Play one arm over every seed; return per-seed (captured, turns, cop score)."""
    out = []
    for seed in seeds:
        trace = Trace(random.Random(seed))
        cop_rng = random.Random(seed + 10_000)  # never share a stream between actors
        builder = ARMS[name]
        policy = builder(cop_rng) if name == "blind" else builder(trace)
        result = run_sub_game(CONFIG, policy, trace.thief_policy)
        out.append((result.outcome is Outcome.CAPTURE, result.turns, result.score.cop))
    return out


def summarise(rows: list[tuple[bool, int, int]]) -> dict[str, float]:
    n = len(rows)
    return {
        "capture_rate": sum(r[0] for r in rows) / n,
        "mean_turns": sum(r[1] for r in rows) / n,
        "mean_cop_score": sum(r[2] for r in rows) / n,
        "matches": n,
    }


def paired(better: list, worse: list) -> dict[str, int]:
    """Per-seed comparison. Every arm met the identical Thief trajectory on a given seed,
    so this is a paired test rather than two independent averages -- a far stronger claim
    than comparing means, and free given the design."""
    # strict=True is load-bearing: unequal arms would silently mis-pair seeds.
    pairs = list(zip(better, worse, strict=True))
    return {
        "seeds_better_captured_only": sum(b[0] and not w[0] for b, w in pairs),
        "seeds_worse_captured_only": sum(w[0] and not b[0] for b, w in pairs),
        "seeds_both_captured": sum(b[0] and w[0] for b, w in pairs),
        "seeds_neither_captured": sum(not b[0] and not w[0] for b, w in pairs),
    }


def main() -> int:
    arms = {name: run_arm(name) for name in ARMS}
    report = {name: summarise(rows) for name, rows in arms.items()}
    report["paired_belief_vs_blind"] = paired(arms["belief"], arms["blind"])
    gap = report["oracle"]["mean_cop_score"] - report["blind"]["mean_cop_score"]
    closed = report["belief"]["mean_cop_score"] - report["blind"]["mean_cop_score"]
    report["belief_share_of_available_gap"] = round(closed / gap, 4) if gap else None
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
