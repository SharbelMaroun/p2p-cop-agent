"""The replay board as data: the whole chase at a glance (`M8-15`).

The book's replay axis exists to answer "what really happened?" (p.54/135), and rule 9's
objective-board ban binds the **live** interface only — the replay runs in the audit
phase, after the nonces are revealed, as a "Retrospective Witness". The reference draws
exactly this: it loads the opponent's log beside our own when one is available and paints
both true positions on one board, falling back to a single trail when it is not. This
module is that reconstruction as display-ready data; the widget layer reads nothing else.

Everything here is tolerant by construction, because a replay that crashes on a strange
log is a viewer that fails during the demo it exists for: a record without a position is
skipped, barriers are read from the cop-shaped `payload.barriers` list or parsed out of
the thief-shaped `state` string, the grid size comes from the state string with the
board's own coordinates as the fallback, and an opponent log that does not align by step
still renders whatever does. Verification stays the cursor's job — this file never touches
a hash.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from p2p_cop_agent.replay.load import ReplayLog

Cell = tuple[int, int]

OUR_COLOUR = "#1565c0"
THEIR_COLOUR = "#ef6c00"
BARRIER_COLOUR = "#263238"
CAPTURE_COLOUR = "#c62828"


@dataclass(frozen=True)
class Trail:
    """One side's revealed path up to the cursor: oldest first, current cell last."""

    label: str
    colour: str
    cells: tuple[Cell, ...]

    @property
    def current(self) -> Cell | None:
        return self.cells[-1] if self.cells else None


@dataclass(frozen=True)
class BoardFrame:
    """The reconstructed board for one cursor position. Display values only."""

    grid_size: int
    ours: Trail
    theirs: Trail
    barriers: frozenset[Cell]
    capture_cell: Cell | None

    @property
    def caption(self) -> str:
        sides = [f"{self.ours.label} trail {len(self.ours.cells)} step(s)"]
        if self.theirs.cells:
            sides.append(f"{self.theirs.label} trail {len(self.theirs.cells)} step(s)")
        else:
            sides.append("opponent log not loaded")
        return "   ·   ".join(sides)


def _payload(record: object) -> Mapping[str, object]:
    payload = record.get("payload") if isinstance(record, Mapping) else None
    return payload if isinstance(payload, Mapping) else {}


def _position(record: object) -> Cell | None:
    value = _payload(record).get("position")
    if isinstance(value, Sequence) and len(value) == 2:
        try:
            return int(value[0]), int(value[1])
        except (TypeError, ValueError):
            return None
    return None


def _step(record: object, default: int) -> int:
    value = _payload(record).get("step")
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def _barriers(record: object) -> frozenset[Cell]:
    """The cumulative disclosed set: the cop-shaped list, else the thief-shaped state."""
    payload = _payload(record)
    value = payload.get("barriers")
    if not isinstance(value, Sequence) or isinstance(value, str):
        match = re.search(r"barriers=(\[.*?\])(?:;|$)", str(payload.get("state", "")))
        if match is None:
            return frozenset()
        try:
            value = ast.literal_eval(match.group(1))
        except (ValueError, SyntaxError):
            return frozenset()
    cells = []
    for item in value:
        if isinstance(item, Sequence) and not isinstance(item, str) and len(item) == 2:
            try:
                cells.append((int(item[0]), int(item[1])))
            except (TypeError, ValueError):
                continue
    return frozenset(cells)


def _grid_size(records: Sequence[object], positions: Sequence[Cell]) -> int:
    for record in records:
        match = re.search(r"grid=(\d+)x", str(_payload(record).get("state", "")))
        if match is not None:
            return int(match.group(1))
    reach = max((max(cell) for cell in positions), default=6)
    return max(reach + 1, 7)


def board_frame(
    log: ReplayLog,
    position: int,
    *,
    opponent: ReplayLog | None = None,
    our_label: str = "police",
    their_label: str = "thief",
    captured: bool = False,
) -> BoardFrame:
    """Reconstruct the board at cursor ``position`` (zero-based, clamped).

    Our trail is every revealed position up to the cursor. The opponent's trail, when
    that log is present, is every record whose step is at or before the step under the
    cursor — the alignment the turn cycle defines, with the misaligned remainder simply
    not drawn. ``captured`` rings the final cell so the capture reads at a glance.
    """
    records = log.records
    index = max(0, min(position, len(records) - 1)) if records else 0
    shown = records[: index + 1]
    ours = tuple(cell for cell in (_position(r) for r in shown) if cell is not None)
    step_now = _step(records[index], index + 1) if records else 0
    theirs: tuple[Cell, ...] = ()
    barriers = _barriers(records[index]) if records else frozenset()
    if opponent is not None:
        aligned = [r for r in opponent.records if _step(r, 10**9) <= step_now]
        theirs = tuple(cell for cell in (_position(r) for r in aligned) if cell is not None)
        if aligned:
            barriers = barriers | _barriers(aligned[-1])
    capture_cell = ours[-1] if captured and index == len(records) - 1 and ours else None
    every = [*ours, *theirs]
    return BoardFrame(
        grid_size=_grid_size([*shown, *(opponent.records if opponent else ())], every),
        ours=Trail(our_label, OUR_COLOUR, ours),
        theirs=Trail(their_label, THEIR_COLOUR, theirs),
        barriers=barriers,
        capture_cell=capture_cell,
    )
