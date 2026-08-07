"""Containment: in a locked orbit, wall the cell just vacated and ratchet the ring (M6-23).

The opponent grid found the boundary of the shipped stack: trap-and-squeeze converts a
pure distance-maximiser 40/40 and a distance-plus-mobility archetype 0/40 — and so does
every barrier-free arm, the **oracle included**, at 0/40. The probe shows the terminal
shape in one line per game: the chase herds the Thief's sooner-reached territory from
36 cells to a 9-cell corner pocket, and there the game locks — distance 3 every turn,
the Thief orbiting the pocket's cycle, zero barriers placed, to the horizon.

Two facts make that lock unbreakable by pricing walls statically, both measured before
this design was reached (both prior versions of this module fired zero times):

- **No placeable wall is ever inside the pocket.** Placement reaches one step from the
  Cop, and one step from the Cop the Cop is nearer by definition — so cop-adjacent
  cells are never in the Thief's sooner-reached region, and pricing candidates by
  pocket area or pocket cycles finds every candidate outside the pocket, cutting
  nothing, every turn.
- **An equal-speed pursuer never closes on a cycle.** The orbit preserves phase
  forever; capture needs the pocket to be a *tree*, whose branches the chase pushes
  the Thief down into a leaf, where the trap rule ends it.

What does change the pocket is time: as both sides orbit, the Cop **occupies cells the
Thief's orbit needs a lap later**. So the endgame rule is a ratchet, not a price list —
once the position reads as a lock (pocket at or under ``REGION_TRIGGER`` cells and
still carrying a cycle), wall the cell just vacated. The wall lands on the orbit ring
behind us, the chase continues unobstructed in front of us, and each lap the ring
loses a cell until the cycle is cut. The quota spends only in the endgame, one cell
per lap segment, far under fourteen.

The one refusal kept is the sealing one: a wall that would leave the believed cell
unreachable to us hands the Thief a fortress and the horizon. The obstruction refusal
that governs the squeeze is deliberately *not* applied — the vacated cell is behind
the chase by construction, and the wall that eventually blocks the ring is the point,
not a side effect.

The companion repository measured territory from the Thief side and refused it —
owning board is not surviving. Read from this side the same asymmetry is the win: the
Thief needs a cycle to survive, so the quota buys tree-ness.
"""

from __future__ import annotations

from p2p_cop_agent.domain.barriers import BarrierError, BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.pursuit import step_distances

# The ratchet arms once the chase has herded the Thief's sooner-reached region to this
# many cells or fewer — half the negotiated-minimum board. The first cut tried 15 and
# measured its own failure: two walls pushed the Thief to a *different* corner whose
# pocket re-locked at 16 cells, one over the trigger, and the rule disarmed for the
# rest of the game. The lock is a property of the orbit, not of any one corner, so the
# trigger must cover every pocket the board can re-lock into.
REGION_TRIGGER = 25


def pocket(
    board: Board,
    believed: Coordinate,
    cop: Coordinate,
    blocked: frozenset[Coordinate],
) -> tuple[int, int]:
    """Return (area, independent cycles) of the region the Thief reaches first.

    Ties go to the Cop — arriving together is a capture, not an escape — and cells we
    cannot reach at all count as the Thief's, which is exactly the sealed pocket the
    placement filter refuses to create. Cycles are ``edges − vertices + components``
    of the induced orthogonal-adjacency subgraph: zero means a forest, and a forest
    is a chase the Thief loses.
    """
    far = board.grid_size * board.grid_size + 1
    ours = step_distances(board, cop, blocked)
    theirs = step_distances(board, believed, blocked)
    cells = {cell for cell, distance in theirs.items() if distance < ours.get(cell, far)}
    edges = sum(
        1 for cell in cells
        for neighbour in (Coordinate(cell.row + 1, cell.col), Coordinate(cell.row, cell.col + 1))
        if neighbour in cells
    )
    seen: set[Coordinate] = set()
    components = 0
    for cell in cells:
        if cell in seen:
            continue
        components += 1
        frontier = [cell]
        seen.add(cell)
        while frontier:
            here = frontier.pop()
            for step_row, step_col in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                neighbour = Coordinate(here.row + step_row, here.col + step_col)
                if neighbour in cells and neighbour not in seen:
                    seen.add(neighbour)
                    frontier.append(neighbour)
    return len(cells), edges - len(cells) + components


def choose_containment(
    board: Board,
    cop: Coordinate,
    believed: Coordinate,
    barriers: BarrierField,
    previous: Coordinate | None = None,
    *,
    region_trigger: int = REGION_TRIGGER,
) -> Coordinate | None:
    """Return the vacated-cell wall when the position is a locked orbit, else None.

    Fires only when every part of the lock reads true: quota remains, a previous cell
    is known and differs from where we stand, the pocket is endgame-small yet still
    carries a cycle, the placement is legal, and walling it leaves the believed cell
    reachable to us. Deterministic — the candidate is *the* vacated cell, so identical
    histories place identical walls (M6-03d).
    """
    board.require_on_board(cop)
    board.require_on_board(believed)
    if barriers.remaining <= 0 or previous is None or previous in (cop, believed):
        return None
    area, cycles = pocket(board, believed, cop, barriers.cells)
    if area == 0 or area > region_trigger or cycles == 0:
        return None  # nothing to cut, or a forest already — the chase wins those
    # The wall must touch the pocket to change it: a wall dropped on the wider chase
    # orbit spends quota without moving a single pocket edge — measured at trigger 25,
    # where fourteen trail walls left the terminal 9-cell orbit intact and cost a
    # capture against the random walk by stalling every other turn.
    far = board.grid_size * board.grid_size + 1
    ours = step_distances(board, cop, barriers.cells)
    cells = {
        cell for cell, d in step_distances(board, believed, barriers.cells).items()
        if d < ours.get(cell, far)
    }
    if not any(
        Coordinate(previous.row + dr, previous.col + dc) in cells
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
    ):
        return None
    try:
        barriers.place_adjacent(board, cop, previous)
    except BarrierError:
        return None
    after = frozenset(barriers.cells | {previous})
    if believed not in step_distances(board, cop, after):
        return None  # never seal the Thief somewhere we cannot follow
    return previous
