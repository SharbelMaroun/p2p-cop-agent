"""Parameter research: real sweeps through the real referee (`M9-06`, `M9-07`).

Guidelines §9.1 asks for "systematic experiments with controlled changes to parameters",
and `M9-06c` for "experiment tables with **run counts**, not anecdotes". The book sets the
standard plainly — the research must be "based on numbers and not on guesses" (p.142/266).

Every figure here comes from `orchestration.harness.run_sub_game` refereeing a real match.
Nothing is illustrative, and no value is written by hand.

    uv run python scripts/run_experiments.py

**The protocol is `compare_strategies.py`'s, deliberately reused.** Same board fixture,
same seeded random-walk Thief, same paired design: for a given seed every arm and every
configuration faces the *identical* opponent trajectory, so a difference between two
sweep points is a difference in the parameter and not in the luck of the draw.

**Which parameters may legitimately move.** Appendix F marks each row Fixed, Minimum or
Negotiation. Asked directly: Fixed "may not be changed; deviation leads to
disqualification"; Minimum "may be raised by agreement but never lowered"; Negotiation is
"any value agreed upon by both sides". Board size (7x7), obstacle quota (14), step limit
(35) and survival threshold (35) are all **Minimum** — so this sweeps them *upward from*
their minima, which is the range a real negotiation can reach. Sweeping below would study
a configuration rule 12 forbids, and `results/` says so rather than quietly omitting it.

The scent parameters are **Fixed** (0.9 source, 0.10 decay, 5x5 field), so `M9-06b`'s
sweep of them is sensitivity analysis of a value we cannot ship. The decay curve is
reported for exactly that reason: it explains the model without implying we may retune it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from experiment_arena import ARMS, CONFIG, SEEDS, config_with, play  # noqa: E402
from experiment_diagnostics import (  # noqa: E402
    board_reach,
    decision_cost,
    decision_mix,
    scent_decay,
)

from p2p_cop_agent.analysis import paired_compare, summarise  # noqa: E402

RESULTS = ROOT / "results"
# Appendix F minima. Sweeps run upward from each, because rule 12 (Mandatory) permits
# raising a minimum by agreement and never lowering it.
MINIMA = {"grid_size": 7, "max_barriers": 14, "max_moves": 35, "survival_threshold": 35}


def sweep(section: str, key: str, values, arm: str = "belief") -> dict:
    """One-at-a-time: move a single parameter, hold everything else at the fixture."""
    points = []
    for value in values:
        rows = play(config_with(section, key, value), arm)
        points.append({
            "value": value,
            "capture_rate": round(sum(r[0] for r in rows) / len(rows), 4),
            "turns": summarise([r[1] for r in rows]).as_dict(),
            "cop_score": summarise([float(r[2]) for r in rows]).as_dict(),
        })
    return {"parameter": f"{section}.{key}", "arm": arm,
            "appendix_f_status": "Minimum" if key in MINIMA else "see Appendix F",
            "minimum": MINIMA.get(key), "runs_per_point": len(SEEDS), "points": points}


def arms_comparison() -> dict:
    """`M9-07a`: baseline against belief-driven pursuit, paired seed by seed."""
    played = {name: play(CONFIG, name) for name in ARMS}
    report = {
        name: {"capture_rate": round(sum(r[0] for r in rows) / len(rows), 4),
               "turns": summarise([r[1] for r in rows]).as_dict(),
               "cop_score": summarise([float(r[2]) for r in rows]).as_dict()}
        for name, rows in played.items()
    }
    scores = {name: [float(r[2]) for r in rows] for name, rows in played.items()}
    report["paired_belief_vs_blind"] = paired_compare(scores["belief"], scores["blind"]).as_dict()
    report["paired_oracle_vs_belief"] = paired_compare(scores["oracle"], scores["belief"]).as_dict()
    gap = report["oracle"]["cop_score"]["mean"] - report["blind"]["cop_score"]["mean"]
    closed = report["belief"]["cop_score"]["mean"] - report["blind"]["cop_score"]["mean"]
    report["belief_share_of_available_gap"] = round(closed / gap, 4) if gap else None
    report["runs_per_arm"] = len(SEEDS)
    return report


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    produced = {
        "strategy_arms.json": arms_comparison(),
        "sweep_grid_size.json": sweep("board_and_agents", "grid_size", [7, 8, 9, 10, 11, 12]),
        "sweep_barrier_quota.json": sweep("movement_and_barriers", "max_barriers",
                                          [14, 18, 22, 26, 30]),
        "sweep_survival_threshold.json": sweep("movement_and_barriers",
                                               "survival_threshold", [35, 45, 55, 65, 75]),
        "decision_cost.json": decision_cost(),
        "decision_mix.json": decision_mix(),
        "board_reach.json": board_reach(),
        "scent_decay.json": scent_decay(),
    }
    for name, payload in produced.items():
        (RESULTS / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                                    "utf-8")
        print(f"results/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
