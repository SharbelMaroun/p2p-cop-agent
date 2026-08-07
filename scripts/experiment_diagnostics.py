"""Diagnostics: the measurements that *explain* a sweep rather than produce one.

Split out when `run_experiments.py` passed the length cap, and the seam turned out to be
the honest one. A sweep answers "what happens when this parameter moves"; everything here
answers "why did that sweep say what it said" — and two of these exist only because two
sweeps came back suspiciously flat.

* `decision_mix` — the barrier-quota sweep was identical at every quota. The reason is not
  that the quota does not matter: the measured arm never places a barrier at all.
* `board_reach` — the grid-size sweep was flat because the Thief never reaches the outer
  ranks within the horizon, so a larger board is unused space.
* `decision_cost` — the per-turn budget against the negotiated timeout (`M6-13`).
* `scent_decay` — the Fixed scent model, reported to explain it rather than retune it.
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from experiment_arena import ARMS, CONFIG, SEEDS, Trace, config_with  # noqa: E402

from p2p_cop_agent.analysis import summarise  # noqa: E402
from p2p_cop_agent.domain.board import Coordinate  # noqa: E402
from p2p_cop_agent.orchestration.harness import run_sub_game  # noqa: E402
from p2p_cop_agent.strategy.scent import CENTER_INTENSITY, DECAY_RATE, decay  # noqa: E402


def decision_cost(samples: int = 400) -> dict:
    """`M6-13`: the per-turn decision cost, against the negotiated response timeout."""
    from p2p_cop_agent.orchestration.state import CopState  # noqa: PLC0415 - benchmark-local

    trace = Trace(CONFIG, random.Random(7))
    policy = ARMS["belief"](trace, random.Random(7))
    cop = CopState.opening(CONFIG)
    last = trace.board.max_index
    trace.thief = Coordinate(last, last)
    trace.field.advance(trace.thief)
    timings = []
    for _ in range(samples):
        start = time.perf_counter()
        policy(cop)
        timings.append((time.perf_counter() - start) * 1000.0)
    summary = summarise(timings)
    timeout_ms = CONFIG["network_and_league"]["response_timeout_sec"] * 1000
    return {"unit": "milliseconds", "samples": samples, **summary.as_dict(),
            "p95": round(sorted(timings)[int(samples * 0.95)], 4),
            "response_timeout_ms": timeout_ms,
            "worst_case_share_of_timeout": round(summary.maximum / timeout_ms, 6)}


def decision_mix() -> dict:
    """What the measured arm actually *does* — added after two sweeps came back flat.

    The barrier-quota sweep was identical to four decimal places at every quota, which
    reads as "the quota does not matter". It is not: the belief arm never places a barrier
    at all, so the sweep was measuring an unused parameter. Counting the decision types
    turns a misleading flat line into the real finding, which is that this arm is
    pursuit-only while `strategy/barrier_policy.py` and `strategy/squeeze.py` exist and are
    tested but are not wired into it.
    """
    kinds: dict[str, int] = {}
    for seed in SEEDS:
        trace = Trace(CONFIG, random.Random(seed))
        inner = ARMS["belief"](trace, random.Random(seed))

        def counting(cop, _inner=inner):
            decision = _inner(cop)
            kinds[type(decision).__name__] = kinds.get(type(decision).__name__, 0) + 1
            return decision

        run_sub_game(CONFIG, counting, trace.thief_policy)
    total = sum(kinds.values())
    return {"matches": len(SEEDS), "decisions": total, "by_type": kinds,
            "barrier_intents": kinds.get("BarrierIntent", 0),
            "barrier_share": round(kinds.get("BarrierIntent", 0) / total, 4) if total else 0.0}


def board_reach() -> dict:
    """Why the grid-size sweep is flat: how much of the board is ever used."""
    out = []
    for size in (7, 9, 12):
        config = config_with("board_and_agents", "grid_size", size)
        reached = set()
        for seed in SEEDS:
            trace = Trace(config, random.Random(seed))
            run_sub_game(config, ARMS["belief"](trace, random.Random(seed)),
                         trace.thief_policy)
            if trace.thief is not None:
                reached.add((trace.thief.row, trace.thief.col))
        out.append({"grid_size": size, "distinct_final_cells": len(reached),
                    "max_index_reached": max(max(cell) for cell in reached),
                    "max_index_available": size - 1})
    return {"runs_per_size": len(SEEDS), "thief_start": CONFIG["board_and_agents"]["thief_start"],
            "horizon": CONFIG["movement_and_barriers"]["survival_threshold"], "sizes": out}


def scent_decay(turns: int = 20) -> dict:
    """`M9-06b`: the Fixed scent model, reported to explain it — not to retune it."""
    intensity, series = CENTER_INTENSITY, [CENTER_INTENSITY]
    for _ in range(turns - 1):
        intensity = decay(intensity)
        series.append(round(intensity, 6))
    return {"source_intensity": CENTER_INTENSITY, "decay_rate": DECAY_RATE,
            "appendix_f_status": "Fixed", "note": "single deposit at turn 0, then decay",
            "turns": list(range(turns)), "intensity": series}
