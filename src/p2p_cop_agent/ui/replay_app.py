"""The replay window (`M8-02`, `M8-02e`) — widgets only, no logic.

Rule 20 is Mandatory and its sanction is a "threshold condition for confirmation of logs
and submission of the project" (p.129/272). The verifier satisfies the *verification*; this
file satisfies the *app*, and produces the `Verified OK` screenshot `:1769` calls part of
the submission requirements.

**What the screen must show**, asked directly: the `nonce`, `move` and original `commit`
from the log entry (p.56/142); a clear verdict indicator — a green `Verified OK` stamp or a
bright red `TAMPERED` banner (p.56/142, 59/146); and control buttons to move "back and
forth in time" (p.56/141). The board is **not** required — the mandatory screenshot
requirement is about the verdict banner — so this window shows the evidence rather than a
grid, and the belief-map picture stays with the live GUI where the book puts it.

**Every widget reads `ReplayFrame` and nothing else** (`M8-06`: "no widget touches domain
or protocol code directly"). The reference draws the same boundary: its widgets are dumb
components handed ready-made strings, with a controller in between.

Excluded from coverage by `M8-06c` and the guidelines' coverage config: a Tk window cannot
be asserted about in CI. What *can* be asserted lives in `replay/view_model.py`, and
`test_replay_view_model.py` pins the exact banner text and colour for both verdicts — so
the picture in the README is backed by an assertion rather than by someone having looked
at it once.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from p2p_cop_agent.replay.cursor import Replay
from p2p_cop_agent.replay.view_model import (
    COLOUR_NEUTRAL,
    COLOUR_TEXT_ON_STAMP,
    ReplayFrame,
    frame_of,
)

BACKGROUND = "#eceff1"
PANEL = "#ffffff"
INK = "#263238"
MUTED = "#607d8b"
ROW_OK = "#e8f5e9"
ROW_BAD = "#ffebee"


class ReplayWindow:
    """A Tk window over a `Replay`. Holds widgets; derives every string from the frame."""

    def __init__(self, replay: Replay, root: tk.Misc | None = None) -> None:
        self._replay = replay
        self.root = root or tk.Tk()
        self.root.title("Replay Viewer — cryptographic verification")
        self.root.configure(bg=BACKGROUND)
        self._mono = tkfont.Font(family="Consolas", size=9)
        self._build()
        self.refresh()

    # --- widgets ------------------------------------------------------------------------

    def _build(self) -> None:
        self._stamp = tk.Label(self.root, font=("Segoe UI", 22, "bold"),
                               fg=COLOUR_TEXT_ON_STAMP, pady=10)
        self._stamp.pack(fill="x")
        self._banner = tk.Label(self.root, font=("Segoe UI", 10), bg=BACKGROUND, fg=INK)
        self._banner.pack(fill="x", pady=(6, 0))
        self._source = tk.Label(self.root, font=("Segoe UI", 8), bg=BACKGROUND, fg=MUTED)
        self._source.pack(fill="x")
        self._sequence = tk.Label(self.root, font=("Segoe UI", 8), bg=BACKGROUND)
        self._sequence.pack(fill="x", pady=(0, 6))

        body = tk.Frame(self.root, bg=BACKGROUND)
        body.pack(fill="both", expand=True, padx=10)
        self._rows = tk.Frame(body, bg=PANEL, bd=1, relief="solid")
        self._rows.pack(side="left", fill="both", expand=True)
        self._detail = tk.Frame(body, bg=PANEL, bd=1, relief="solid")
        self._detail.pack(side="left", fill="both", padx=(10, 0))
        self._detail_labels = self._build_detail()
        self._build_controls()

    def _build_detail(self) -> dict[str, tk.Label]:
        tk.Label(self._detail, text="STEP UNDER CURSOR", font=("Segoe UI", 8, "bold"),
                 bg=PANEL, fg=MUTED).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=6)
        labels: dict[str, tk.Label] = {}
        for index, name in enumerate(("step", "sender", "move", "commit", "nonce", "verdict"), 1):
            tk.Label(self._detail, text=name, font=("Segoe UI", 8, "bold"), bg=PANEL,
                     fg=MUTED).grid(row=index, column=0, sticky="nw", padx=(8, 6), pady=2)
            value = tk.Label(self._detail, font=self._mono, bg=PANEL, fg=INK,
                             justify="left", wraplength=300)
            value.grid(row=index, column=1, sticky="w", padx=(0, 8), pady=2)
            labels[name] = value
        return labels

    def _build_controls(self) -> None:
        bar = tk.Frame(self.root, bg=BACKGROUND)
        bar.pack(fill="x", padx=10, pady=8)
        for text, command in (
            ("|< Restart", self._replay.restart),
            ("< Back", self._replay.step_back),
            ("Step >", self._replay.step_forward),
            ("Jump to divergence", self._replay.go_to_first_divergence),
        ):
            tk.Button(bar, text=text, font=("Segoe UI", 9), width=17,
                      command=self._act(command)).pack(side="left", padx=3)
        self._position = tk.Label(bar, font=("Segoe UI", 9, "bold"), bg=BACKGROUND, fg=INK)
        self._position.pack(side="right")

    def _act(self, command):
        """Every control does the same two things: move, then re-derive the whole screen.

        Re-deriving rather than patching is what keeps `M8-08a` true at the UI layer — the
        stamp is recomputed on every navigation, so a screenshot is of a live computation.
        """
        def handler() -> None:
            command()
            self.refresh()
        return handler

    # --- rendering ----------------------------------------------------------------------

    def refresh(self) -> None:
        """Repaint from a fresh frame. The only place widget text is ever set."""
        frame = frame_of(self._replay)
        self._stamp.configure(text=f"  {frame.stamp}  ", bg=frame.stamp_colour)
        self._banner.configure(text=frame.banner)
        self._source.configure(text=f"{frame.origin}   ·   game {frame.game_id}"
                                    f"   ·   sub-game {frame.sub_game}")
        self._sequence.configure(text=frame.sequence_summary,
                                 fg=MUTED if frame.sequence_ok else COLOUR_NEUTRAL)
        self._position.configure(text=frame.position_label)
        self._paint_rows(frame)
        self._paint_detail(frame)

    def _paint_rows(self, frame: ReplayFrame) -> None:
        for child in self._rows.winfo_children():
            child.destroy()
        for row in frame.rows:
            text = (f"{'>' if row.is_current else ' '} step {row.step:>3}  {row.sender:<7}"
                    f" {row.move:<4} {row.commit_short:<14} {row.verdict}")
            tk.Label(self._rows, text=text, font=self._mono, anchor="w",
                     bg=ROW_OK if row.ok else ROW_BAD, fg=INK,
                     padx=8, pady=1).pack(fill="x")

    def _paint_detail(self, frame: ReplayFrame) -> None:
        current = frame.current
        for name, value in (("step", current.step), ("sender", current.sender),
                            ("move", current.move), ("commit", current.commit),
                            ("nonce", current.nonce), ("verdict", current.reason)):
            self._detail_labels[name].configure(text=value)


def run(replay: Replay) -> None:  # pragma: no cover - the event loop
    ReplayWindow(replay).root.mainloop()
