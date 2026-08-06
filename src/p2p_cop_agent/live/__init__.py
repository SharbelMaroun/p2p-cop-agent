"""The live GUI's data layer: local truth, and the screen derived from it.

Two rules govern everything here. Rule 8 (Mandatory): "Display true local information only
in the live user interface. Sanction: Disqualification due to data breach." Rule 9
(Prohibited): "Do not display the full objective board state in the live user interface.
Sanction: **Project disqualification** due to unfair advantage."

* `local_truth` — the closed set of things the screen may know. Built from explicit
  arguments, never by reading a runtime, so the opponent's real position has nowhere to sit.
* `view_model` — that snapshot projected onto cells, colours, marks and a banner.

The widgets live in `ui/live_app.py` and read `LiveFrame` only, which is what keeps the
boundary testable: a Tk window cannot be asserted about in CI, but a frame can.
"""

from p2p_cop_agent.live.local_truth import Cell, LocalTruth, TurnState, local_truth
from p2p_cop_agent.live.view_model import CellView, LiveFrame, frame_of, heat_colour

__all__ = [
    "Cell",
    "CellView",
    "LiveFrame",
    "LocalTruth",
    "TurnState",
    "frame_of",
    "heat_colour",
    "local_truth",
]
