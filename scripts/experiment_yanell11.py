"""Can our Cop catch yanell11's improved Thief? (2026-08-16)

Run 5 sub-game 1 was a survival with **perfect information**: the belief named their exact
cell on 34/34 turns, and we still finished 35 steps without a capture. So this is not a
perception experiment -- it measures *pursuit*. Two failures were visible in that log and
both are modelled here:

* a **stern chase** -- from step 29 we moved into the cell they had just vacated, six
  turns running, which a same-speed evader escapes forever;
* **barriers spent in the wrong region** -- 8 of 14 formed a ring around the centre
  `[3,3]` while the Thief ran the perimeter, and the remaining 6 were never played.

Arms are the live decision path (`live_decide`), not a shortcut: an earlier arena fed a
different grid shape than the wire does and produced a conclusion that was simply wrong.
Here the Thief emits through `ScentField` and publishes `encode_scent(trail.snapshot())`,
which is exactly what crosses the wire.

Two opponents:

* ``replay``  -- their recorded run-5 g01 trajectory, move for move. It does not react, so
  it answers one narrow question honestly: can a better Cop intercept a *known* path?
* ``evader``  -- greedy max-distance with a corner-avoiding tie-break, reacting to where
  the Cop actually is. Strictly harder than ``replay`` and closer to what we will face.

Usage:  uv run python scripts/experiment_yanell11.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from p2p_cop_agent.domain.actions import Action  # noqa: E402
from p2p_cop_agent.domain.board import Board  # noqa: E402
from p2p_cop_agent.domain.coordinates import Coordinate  # noqa: E402
from p2p_cop_agent.domain.movement import apply_move, legal_moves  # noqa: E402
from p2p_cop_agent.orchestration.live_policy import live_decide  # noqa: E402
from p2p_cop_agent.protocol.scent_wire import encode_scent  # noqa: E402
from p2p_cop_agent.strategy.scent_field import ScentField  # noqa: E402

GRID = 7
HORIZON = 35
THIEF_START = Coordinate(3, 3)
COP_START = Coordinate(0, 0)

GAME = {
    "board_and_agents": {"grid_size": GRID, "thief_start": [3, 3], "cop_start": [0, 0],
                         "axis_origin_corner": "top-left", "axis_start_index": 0},
    "movement_and_barriers": {"move_set": ["N", "S", "E", "W", "STAY"],
                              "max_barriers": 14, "max_moves": HORIZON,
                              "survival_threshold": HORIZON},
    "world": {"map_area": "Haifa", "hint_max_words": 15},
}

REPO = Path(__file__).resolve().parents[1]
# Every trajectory of theirs we hold. run4's three are the near-stationary Thief we beat;
# run5 g01 is the improved one that survived. A default must not be chosen on the newest
# sample alone -- an arm that wins the rematch but loses the games we already won is not
# an improvement.
REPLAYS = {
    "run4-g01": "games/friendly-yanell11-run4/opponent_audit_sharNamr-vs-yanell11_g01.json",
    "run4-g03": "games/friendly-yanell11-run4/opponent_audit_sharNamr-vs-yanell11_g03.json",
    "run4-g05": "games/friendly-yanell11-run4/opponent_audit_sharNamr-vs-yanell11_g05.json",
    "run5-g01": "games/friendly-yanell11-run5/opponent_audit_sharNamr-vs-yanell11_g01.json",
}


def recorded_path(which: str = "run5-g01") -> list[Coordinate]:
    """One of their recorded trajectories, in step order."""
    data = json.loads((REPO / REPLAYS[which]).read_text(encoding="utf-8"))
    rows = [r["payload"] for a in data["audits"] for r in a.get("records", [])]
    cells = []
    for row in sorted(rows, key=lambda r: r.get("step") or 0):
        pos = row.get("position")
        if isinstance(pos, list) and len(pos) == 2:
            cells.append(Coordinate(pos[0], pos[1]))
    return cells


def greedy_evader(board: Board, thief: Coordinate, cop: Coordinate,
                  blocked: frozenset) -> Coordinate:
    """Maximise Manhattan distance from the Cop; break ties away from the nearest corner.

    The corner term matters: a pure max-distance evader walks into a corner and is trapped
    there, which is the mistake our own Thief makes. Theirs does not, so modelling it
    without the tie-break would make this benchmark easier than the real opponent.
    """
    best, best_key = thief, None
    for action in legal_moves(board, thief, blocked):
        nxt = apply_move(board, thief, action, blocked)
        far = abs(nxt.row - cop.row) + abs(nxt.col - cop.col)
        edge = min(nxt.row, GRID - 1 - nxt.row) + min(nxt.col, GRID - 1 - nxt.col)
        key = (far, edge)          # distance first, then room to manoeuvre
        if best_key is None or key > best_key:
            best, best_key = nxt, key
    return best


def play(strategy: str, opponent: str) -> tuple[bool, int, int]:
    """Return (captured, steps, barriers_used) for one sub-game."""
    board = Board(grid_size=GRID, axis_start_index=0, axis_origin_corner="top-left")
    decide = live_decide(board, COP_START, GAME, strategy=strategy)
    trail = ScentField(board=board)
    path = recorded_path(opponent) if opponent in REPLAYS else []

    thief = THIEF_START
    trail.advance(thief)
    incoming = {"hint": "", "smell_grid": encode_scent(trail.snapshot())}
    cop, barriers = COP_START, 0

    for step in range(1, HORIZON + 1):
        payload, _public = decide(incoming)
        cop = Coordinate(*payload["position"])
        barriers = len(payload.get("barriers") or [])
        if cop == thief:                      # the Cop moved onto the Thief
            return True, step, barriers
        claim = payload.get("move", "")
        if claim.startswith("BARRIER:") and str([thief.row, thief.col]) in claim:
            return True, step, barriers       # a barrier on the Thief's cell captures

        blocked = frozenset(Coordinate(r, c) for r, c in (payload.get("barriers") or []))
        if path:
            thief = path[step] if step < len(path) else thief
        else:
            thief = greedy_evader(board, thief, cop, blocked)
        if cop == thief:                      # the Thief stepped onto the Cop
            return True, step, barriers
        trail.advance(thief)
        incoming = {"hint": "", "smell_grid": encode_scent(trail.snapshot())}
    return False, HORIZON, barriers


ARMS = ["shrink-stack", "engine", "robust_worst", "robust_expected", "robust_lcb"]
OPPONENTS = [*REPLAYS, "evader"]

header = "".join(f"{name:>12}" for name in OPPONENTS)
print(f"{'strategy':<18}{header}")
print("-" * (18 + 12 * len(OPPONENTS)))
scoreboard: dict[str, int] = {}
for arm in ARMS:
    cells, wins = [], 0
    for opponent in OPPONENTS:
        try:
            got, steps, _walls = play(arm, opponent)
            wins += got
            cells.append(f"{('CAP@' + str(steps)) if got else 'survive':>12}")
        except Exception as exc:  # noqa: BLE001 - report, do not abort the sweep
            cells.append(f"{type(exc).__name__[:11]:>12}")
    scoreboard[arm] = wins
    print(f"{arm:<18}{''.join(cells)}   captures {wins}/{len(OPPONENTS)}")

print()
best = max(scoreboard, key=lambda a: (scoreboard[a], a == "shrink-stack"))
print(f"best arm: {best} with {scoreboard[best]}/{len(OPPONENTS)} captures "
      f"(incumbent shrink-stack: {scoreboard['shrink-stack']})")
