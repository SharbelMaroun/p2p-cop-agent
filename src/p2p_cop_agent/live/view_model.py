"""The live screen as data (`M8-01a`, `M8-01b`, `M8-06b`, `M8-07`).

Same split as the replay viewer: this turns a `LocalTruth` snapshot into display-ready
values, and `ui/live_app.py` reads nothing else. A Tk window cannot be asserted about in
CI, so everything the belief-map screenshot claims is decided here instead.

**The heat ramp is relative to the peak, not absolute (`M8-01a`).** The reference scales by
"the peak value on the board at that moment": white `(255, 255, 255)` at zero, deep red
`(255, 51, 51)` at the peak, with green and blue falling together in between. Relative
scaling is the right choice and worth stating why — a belief spread over 64 cells has a
maximum near `0.016`, so an absolute ramp would render every honest board uniformly white
and the screenshot would show a heat map that never heats. `:1660` asks for "cells with
high probability" to stand out, which is a statement about contrast, not about absolute
values.

**Colour is not the only signal (`M8-11b`).** Each cell also carries a percentage and the
most-likely cell is marked `T?`, matching Figure 9's own labelling. A grader reading a
greyscale print, or anyone with a red-green deficiency, still gets the same information —
and the accessibility row asks exactly that.
"""

from __future__ import annotations

from dataclasses import dataclass

from p2p_cop_agent.live.local_truth import Cell, LocalTruth, TurnState

BANNER_COLOURS = {
    TurnState.YOUR_TURN: "#2ecc71",
    TurnState.LOCKED: "#95a5a6",
    TurnState.WAITING: "#95a5a6",
    TurnState.GAME_OVER: "#546e7a",
}
OWN_MARK = "C"
LIKELY_MARK = "T?"
BARRIER_MARK = "#"
GRID_LINE = "#cccccc"
OWN_COLOUR = "#2980b9"
BARRIER_COLOUR = "#263238"
VISITED_COLOUR = "#b0bec5"


@dataclass(frozen=True)
class CellView:
    """One board square, ready to draw. Carries no opponent truth — only our belief."""

    cell: Cell
    colour: str
    mark: str
    probability: float
    is_own: bool
    is_barrier: bool
    is_visited: bool

    @property
    def percentage(self) -> str:
        """The second signal, so colour is not the only one (`M8-11b`).

        A belief spread over 64 cells sits well below 1% almost everywhere, and rounding
        those to `0%` prints a board that claims the opponent is nowhere — the opposite of
        what the number is there to say. Below one percent the label degrades to `<1%`,
        which is honest about the magnitude without pretending to precision.
        """
        if self.probability <= 0:
            return ""
        if self.probability < 0.01:
            return "<1%"
        return f"{self.probability * 100:.0f}%"


@dataclass(frozen=True)
class LiveFrame:
    """The whole live screen for one moment."""

    grid_size: int
    banner_label: str
    banner_detail: str
    banner_colour: str
    accepts_input: bool
    step: int
    score: int
    hints: tuple[str, ...]
    cells: tuple[CellView, ...]

    @property
    def status_line(self) -> str:
        return f"step {self.step}   ·   score {self.score}"

    def at(self, cell: Cell) -> CellView:
        return next(view for view in self.cells if view.cell == cell)


def heat_colour(probability: float, peak: float) -> str:
    """White at zero, deep red at the peak — the reference's ramp.

    `peak` is the highest belief currently on the board, so contrast is preserved however
    diffuse the distribution is. A zero peak (nothing believed yet) leaves the board white
    rather than dividing by zero.
    """
    if peak <= 0 or probability <= 0:
        return "#ffffff"
    share = min(probability / peak, 1.0)
    channel = round(255 - (255 - 51) * share)
    return f"#ff{channel:02x}{channel:02x}"


def _cell_view(cell: Cell, truth: LocalTruth, peak: float, likely: Cell | None) -> CellView:
    probability = truth.belief.get(cell, 0.0)
    is_own = cell == truth.own_position
    is_barrier = cell in truth.disclosed_barriers
    if is_barrier:
        colour, mark = BARRIER_COLOUR, BARRIER_MARK
    elif is_own:
        colour, mark = OWN_COLOUR, OWN_MARK
    else:
        colour = heat_colour(probability, peak)
        mark = LIKELY_MARK if cell == likely and probability > 0 else ""
    return CellView(
        cell=cell,
        colour=colour,
        mark=mark,
        probability=probability,
        is_own=is_own,
        is_barrier=is_barrier,
        is_visited=cell in truth.visited,
    )


def frame_of(truth: LocalTruth) -> LiveFrame:
    """Project a snapshot onto the screen. Reads only what `LocalTruth` permits."""
    peak = truth.peak
    likely = truth.most_likely
    cells = tuple(
        _cell_view((row, column), truth, peak, likely)
        for row in range(truth.grid_size)
        for column in range(truth.grid_size)
    )
    return LiveFrame(
        grid_size=truth.grid_size,
        banner_label=truth.turn_state.label,
        banner_detail=truth.turn_state.detail,
        banner_colour=BANNER_COLOURS[truth.turn_state],
        accepts_input=truth.turn_state.accepts_input,
        step=truth.step,
        score=truth.score,
        hints=tuple(truth.hints),
        cells=cells,
    )
