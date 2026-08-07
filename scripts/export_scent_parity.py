"""Export the scent model so an opponent can run identical physics (`M6-15`).

The book's boxed method (`inst/police_thief_p2p_Summary.md:1043-1048`) has three steps: agree
the emission and decay model, **check that both sides interpret it identically using a
concrete numerical example**, and lock the agreement with a SHA-256 hash. Rule 23 then
cancels the game for any deviation from the formula. It also *recommends* — not mandates —
exchanging the scent mechanism's source code.

`scent_lock.py` already does the third step. This does the second, which is the one that
actually catches disagreements, because the hash only tells two peers **that** they differ.

The worked example is not decoration. The reference simulator deposits first and decays the
whole field afterwards, yielding `(tau + delta)(1 - rho)`; the book's formula decays first,
yielding `max(0, (1 - rho)*tau + delta)`. Both are "multiplicative decay with rho = 0.1",
both agree on every Appendix F constant, and they disagree on the very first re-emission —
`0.9` against `0.81` on a cell just stepped on. Constants cannot expose that. A trace can,
in one line, before anyone has played a turn.

The walk **returns to its start**, so a cell is re-emitted onto after decaying. That is where
the two orderings separate, and a trace that never revisits a cell would agree under both.

**What is not in the bundle.** Belief, trust, hint decoding and pursuit — Cop-private by
`M6-18`, and rule 2 forbids sharing agent internals. The scent model is the one part of this
agent that is *supposed* to be public, because both peers must run it identically.

Sending the bundle is a per-opponent act and is not automated here: it is addressed to a
person, and this script has no business deciding who. Write it, read it, then attach it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.strategy import scent
from p2p_cop_agent.strategy.scent_field import ScentField
from p2p_cop_agent.strategy.scent_lock import scent_model_hash, scent_model_record

# Small enough to check by hand, and it revisits (3,3) — see the module docstring.
WALK = ((3, 3), (3, 4), (4, 4), (4, 3), (3, 3))
PLACES = 6
DEFAULT_OUT = Path("artifacts") / "scent-parity.json"


def board(grid_size: int = 7) -> Board:
    """The negotiated board. Axis members are stated because they change what a key means."""
    return Board(grid_size=grid_size, axis_start_index=0, axis_origin_corner="top-left")


def trace(grid_size: int = 7) -> list[dict]:
    """Walk the field and record the whole board after each step.

    The **whole** board, not the 5x5 window: a window hides whether cells outside it decayed,
    and an opponent whose decay ran only inside the window would match every published number
    while running different physics.
    """
    from p2p_cop_agent.domain.coordinates import Coordinate  # noqa: PLC0415

    field = ScentField(board=board(grid_size))
    steps = []
    for index, (row, col) in enumerate(WALK):
        field.advance(Coordinate(row=row, col=col))
        steps.append({
            "step": index,
            "occupied": [row, col],
            "field": {f"{r},{c}": round(tau, PLACES)
                      for (r, c), tau in sorted(field.intensities.items()) if tau > 0.0},
        })
    return steps


def bundle(grid_size: int = 7) -> dict:
    """Everything an opponent needs to reproduce our field, and nothing else."""
    return {
        "_note": "Scent model offered for parity per the book's boxed method and rule 23's "
                 "recommendation. Contains the emission/decay model only: belief, trust and "
                 "pursuit are agent-private [AE-2].",
        "model_record": scent_model_record(),
        "scent_model_hash": scent_model_hash(),
        "source_files": ["src/p2p_cop_agent/strategy/scent.py",
                         "src/p2p_cop_agent/strategy/scent_field.py",
                         "src/p2p_cop_agent/strategy/scent_lock.py"],
        "how_to_check": [
            "Hash your own model record with canonical JSON; it must equal scent_model_hash.",
            "Run the walk in worked_example.walk on an empty field of the stated grid_size, "
            "advancing one cell per step, and compare each step's field to ours.",
            "A mismatch at step 4 with agreement before it means decay ordering: we decay "
            "then add, per the book's formula. Deposit-then-decay attenuates fresh trails.",
        ],
        "worked_example": {
            "grid_size": grid_size,
            "axis_origin_corner": "top-left",
            "axis_start_index": 0,
            "keys": "row,col",
            "decimal_places": PLACES,
            "walk": [list(cell) for cell in WALK],
            "steps": trace(grid_size),
        },
        "negotiable": {
            "outer_ring_delta": scent.DEFAULT_OUTER_RING_DELTA,
            "_note": "The eight cells at squared distance 5 carry no book value [U-030]. "
                     "This is our opening offer, not a book constant; a different agreed "
                     "value changes the hash, which is the point of locking it.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Write the bundle, and print where it went and what to do with it."""
    args = list(sys.argv[1:] if argv is None else argv)
    out = Path(args[0]) if args else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bundle(), indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    print(f"scent_model_hash: {scent_model_hash()}")
    print("Send this file, plus the three source files it names, to the opponent before "
          "negotiation. Then compare their hash with ours: equal means agreed, different "
          "means one of us must change before play [AE-23].")
    return 0


if __name__ == "__main__":
    sys.exit(main())
