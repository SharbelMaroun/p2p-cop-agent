"""What the live screen is allowed to know (`M8-01`, `M8-01d`, `M8-07a`).

This is the highest-consequence boundary in the project. Appendix E:

* **Rule 8 (Mandatory)** — "Display true local information only in the live user interface.
  Sanction: **Disqualification due to data breach**."
* **Rule 9 (Prohibited)** — "Do not display the full objective board state in the live user
  interface. Sanction: **Project disqualification due to unfair advantage**."

Rule 9's sanction is the whole *project*, not one game. Asked directly, what is forbidden
is precise: "the GUI may never show the actual, objective coordinates of the opponent while
the match is live". And it never becomes allowed — after the reveal the operator moves to
the **replay viewer**, which is where seeing the true history belongs; the live GUI "is not
specified to change its nature after the game".

**Why a type and not a rule of thumb.** Our own process legitimately holds the opponent's
revealed positions during the audit, so a GUI that renders "whatever the runtime has" would
leak them — and the leak would look like ordinary code. `:1647` states the principle:
each interface shows "only the information accessible to it … and never the full objective
board state. There is no 'bird's-eye view'". The reference enforces it the same way: its
`snapshot()` fixes exactly which fields cross to the GUI, so the opponent's true position
"is not part of the View object and the GUI is therefore incapable of drawing it".

So `LocalTruth` has a closed field set and is built from explicit arguments rather than
handed a runtime object to read. Adding a field is a visible edit that fails
`test_local_truth_boundary.py`, which pins the field set exactly. That is the difference
between a boundary and an intention.

**Barriers are the same argument one level down (`M8-07a`).** Rule 15 (Mandatory) —
"Declare openly the placement of all obstacles" — makes a barrier public *once declared*,
so `disclosed` is its own input rather than something read off a board object that knows
about every barrier including the ones not yet announced.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum

Cell = tuple[int, int]

# The two states Figure 9 shows (`:1669`, `:1670`). Locking is mandatory, not cosmetic:
# asked directly, the interface "enforces the lock" after the commit is sent to prevent a
# race where both sides act on the same turn.
class TurnState(Enum):
    """What the banner says, and whether the operator may act."""

    YOUR_TURN = ("YOUR TURN", "turn received (act enabled)", True)
    LOCKED = ("LOCKED", "commit sent (input locked)", False)
    WAITING = ("WAITING", "awaiting the opponent's turn", False)
    GAME_OVER = ("GAME OVER", "the sub-game has ended", False)

    def __init__(self, label: str, detail: str, accepts_input: bool) -> None:
        self.label = label
        self.detail = detail
        self.accepts_input = accepts_input


@dataclass(frozen=True)
class LocalTruth:
    """Everything the live screen may see, and nothing else.

    The field set is closed on purpose. Every name here is something this agent observed
    or was told: where **we** are, which barriers were **declared**, which cells **we**
    visited, what **we** believe, what the opponent **said**. No field can hold the
    opponent's real position, so no widget can render one.
    """

    grid_size: int
    own_position: Cell
    turn_state: TurnState
    step: int
    disclosed_barriers: frozenset[Cell] = frozenset()
    visited: frozenset[Cell] = frozenset()
    belief: Mapping[Cell, float] = field(default_factory=dict)
    hints: Sequence[str] = ()
    score: int = 0

    @property
    def peak(self) -> float:
        """The highest belief on the board — the heat ramp is relative to it."""
        return max(self.belief.values(), default=0.0)

    @property
    def most_likely(self) -> Cell | None:
        """The cell the operator reads as "probably there".

        Still not the opponent's position: it is *our inference*, which is the whole point
        of a belief map. Rules 8 and 9 forbid showing the truth, not showing a guess.
        """
        if not self.belief:
            return None
        return max(self.belief, key=lambda cell: self.belief[cell])


def local_truth(
    *,
    grid_size: int,
    own_position: Cell,
    turn_state: TurnState,
    step: int,
    disclosed_barriers: Iterable[Cell] = (),
    visited: Iterable[Cell] = (),
    belief: Mapping[Cell, float] | None = None,
    hints: Iterable[str] = (),
    score: int = 0,
) -> LocalTruth:
    """Build a snapshot from **explicit values**, never by reading a runtime object.

    Keyword-only and exhaustive: a caller has to name every piece of information it is
    handing the screen. Passing a runtime and letting the view take what it likes is the
    shape of code that eventually takes too much.
    """
    if grid_size <= 0:
        raise ValueError("grid_size must be positive")
    if not _on_board(own_position, grid_size):
        raise ValueError(f"own_position {own_position} is off a {grid_size}x{grid_size} board")
    return LocalTruth(
        grid_size=grid_size,
        own_position=own_position,
        turn_state=turn_state,
        step=step,
        disclosed_barriers=frozenset(disclosed_barriers),
        visited=frozenset(visited),
        belief=dict(belief or {}),
        hints=tuple(hints),
        score=score,
    )


def _on_board(cell: Cell, grid_size: int) -> bool:
    row, column = cell
    return 0 <= row < grid_size and 0 <= column < grid_size
