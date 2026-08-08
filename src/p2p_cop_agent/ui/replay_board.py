"""The replay board widget — drawing only, every value from `BoardFrame` (`M8-15`).

Split from `replay_app.py` for the same reason the view model is split from the cursor:
the app assembles, this file draws, and neither touches domain or protocol code. The
replay board is the one canvas with no reference-matched ramp to preserve, so it wears
the full dark theme: near-black felt, faint grid, neon trails whose "glow" is faked by
concentric shapes pre-blended toward the background (`ui/style.py`), rounded barrier
tiles, and a hot ring on the capture cell. Excluded from coverage per `M8-06c`; what is
assertable lives in `replay/board.py` and its tests.
"""

from __future__ import annotations

import tkinter as tk

from p2p_cop_agent.replay.board import CAPTURE_COLOUR, BoardFrame, Trail
from p2p_cop_agent.ui.style import blend, rounded_rect

CELL = 46
FELT = "#0e1626"
GRID_LINE = "#1d2a45"
TILE = "#334155"


def paint_board(canvas: tk.Canvas, frame: BoardFrame) -> None:
    """Repaint the whole reconstruction: grid, both trails, barriers, capture ring."""
    size = frame.grid_size * CELL
    canvas.configure(width=size, height=size, bg=FELT, highlightthickness=0)
    canvas.delete("all")
    for line in range(frame.grid_size + 1):
        canvas.create_line(0, line * CELL, size, line * CELL, fill=GRID_LINE)
        canvas.create_line(line * CELL, 0, line * CELL, size, fill=GRID_LINE)
    for cell in frame.barriers:
        row, column = cell
        rounded_rect(canvas, column * CELL + 3, row * CELL + 3,
                     (column + 1) * CELL - 3, (row + 1) * CELL - 3, 10,
                     fill=TILE, outline=blend(TILE, "#ffffff", 0.15))
        _text(canvas, cell, "#", "#cbd5e1")
    _trail(canvas, frame.theirs)
    _trail(canvas, frame.ours)
    if frame.capture_cell is not None:
        row, column = frame.capture_cell
        for reach, share in ((6, 0.35), (2, 1.0)):
            canvas.create_oval(column * CELL + 5 - reach, row * CELL + 5 - reach,
                               (column + 1) * CELL - 5 + reach,
                               (row + 1) * CELL - 5 + reach,
                               outline=blend(FELT, CAPTURE_COLOUR, share), width=3)


def _trail(canvas: tk.Canvas, trail: Trail) -> None:
    """Oldest steps smallest and dimmest; the current cell a glowing labelled disc."""
    count = len(trail.cells)
    for age, cell in enumerate(trail.cells[:-1]):
        share = (age + 1) / count
        radius = 4 + round(4 * share)
        row, column = cell
        x, y = column * CELL + CELL / 2, row * CELL + CELL / 2
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                           fill=blend(FELT, trail.colour, 0.2 + 0.65 * share), outline="")
    current = trail.current
    if current is not None:
        row, column = current
        canvas.create_oval(column * CELL + 2, row * CELL + 2,
                           (column + 1) * CELL - 2, (row + 1) * CELL - 2,
                           fill=blend(FELT, trail.colour, 0.25), outline="")
        canvas.create_oval(column * CELL + 7, row * CELL + 7,
                           (column + 1) * CELL - 7, (row + 1) * CELL - 7,
                           fill=trail.colour, outline="#ffffff", width=2)
        _text(canvas, current, trail.label[:1].upper(), "#0b1220")


def _text(canvas: tk.Canvas, cell: tuple[int, int], value: str, colour: str) -> None:
    row, column = cell
    canvas.create_text(column * CELL + CELL / 2, row * CELL + CELL / 2, text=value,
                       font=("Segoe UI", 11, "bold"), fill=colour)
