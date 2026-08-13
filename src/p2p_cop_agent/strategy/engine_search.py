"""The alpha-beta itself: node types, action generation, and the root (M11-02).

Split from `engine.py` at the file-length cap, and the seam is a real one -- this module
knows only bit indices and masks, while `engine.py` owns the translation to and from
`Coordinate` and `TurnIntent`. Nothing here touches a domain object, which is what keeps
the inner loop cheap enough to be worth searching with.

The move order follows the local referee (`orchestration/harness.py`): the Thief acts,
capture is checked, the Cop acts, capture is checked. So the Cop always chooses knowing
where the Thief just went, and the search is entered at a Cop node for that reason.

**Determinism is a rule here, not a preference** (M6-03d, and rule 53's audit): actions
are generated in a fixed order and ties break on that order, never on a dictionary's
iteration or a clock. The budget is a node count rather than a wall-clock deadline for
the same reason -- two runs of one match must produce the same game, and a timer makes
the search depend on what else the machine happened to be doing.
"""

from __future__ import annotations

from p2p_cop_agent.strategy.bitboard import bit, cell_of, neighbours
from p2p_cop_agent.strategy.engine_eval import CAPTURE, Weights, evaluate

MAX_DEPTH = 8


class Budget:
    """A node allowance shared across one decision's iterative deepening."""

    __slots__ = ("left",)

    def __init__(self, nodes: int) -> None:
        self.left = nodes

    def spend(self) -> bool:
        self.left -= 1
        return self.left > 0


def cop_actions(
    cop: int, free: int, size: int, barriers_left: int, thief: int | None = None
) -> list[tuple[str, int]]:
    """Return every legal Cop action as ``(kind, target)``, best-looking first.

    Moves come before barrier placements so that a move which captures is found before a
    barrier that merely threatens one: it ends the sub-game a turn sooner, and the search
    prefers the shallower win.

    Within the moves the order is by Manhattan distance to the Thief, closing first. That
    is worth doing twice over. It prunes -- alpha-beta is only as good as its first
    guess -- and it fixes ties, which is not cosmetic: **`STAY` is a legal Cop move, and
    a search too shallow to separate its options keeps whichever it generated first.**
    Generate `STAY` first and a blind Cop stands on its opening square for the whole
    sub-game, which is exactly the failure `patrol` was written to undo. Closing moves
    first means the fallback under uncertainty is pursuit.
    """
    origin = cell_of(cop, size)
    step = neighbours(origin, size)
    moves = [("move", index) for index in _indices(step & free)]
    if thief is not None:
        target = cell_of(thief, size)
        moves.sort(key=lambda action: (_manhattan(cell_of(action[1], size), target),
                                       action[1]))
    actions: list[tuple[str, int]] = [*moves, ("move", cop)]
    if barriers_left > 0:
        placeable = (step | bit(origin, size)) & free
        actions.extend(("barrier", index) for index in _indices(placeable))
    return actions


def _manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def thief_actions(thief: int, free: int, size: int, cop: int | None = None) -> list[int]:
    """Return the cells the Thief may occupy next, best-looking first.

    `STAY` is always among them, and it goes last for the same reason it does for the
    Cop: a fleeing evader that cannot tell its options apart should run, not freeze.
    """
    cells = _indices(neighbours(cell_of(thief, size), size) & free)
    if cop is not None:
        away = cell_of(cop, size)
        cells.sort(key=lambda index: (-_manhattan(cell_of(index, size), away), index))
    return [*cells, thief]


def _indices(mask: int) -> list[int]:
    """Return the set bit indices of ``mask``, lowest first."""
    found = []
    while mask:
        low = mask & -mask
        found.append(low.bit_length() - 1)
        mask ^= low
    return found


def trapped(thief: int, free: int, size: int) -> bool:
    """Return whether every cardinal neighbour of the Thief is off-board or barriered."""
    return (neighbours(cell_of(thief, size), size) & free) == 0


def cop_node(cop, thief, free, left, size, depth, alpha, beta, weights, budget, horizon):
    """Return the value of a position in which the Cop is to act (it maximises)."""
    if depth <= 0 or horizon <= 0 or not budget.spend():
        return evaluate(cop, thief, free, left, size, weights)
    best = -CAPTURE * 2
    for kind, target in cop_actions(cop, free, size, left, thief):
        won, value = _cop_reply(kind, target, cop, thief, free, left, size, depth,
                                max(alpha, best), beta, weights, budget, horizon)
        if won:
            return value
        best = max(best, value)
        if best >= beta:
            break
    return best


def _cop_reply(kind, target, cop, thief, free, left, size, depth, alpha, beta,
               weights, budget, horizon):
    """Return ``(is_capture, value)`` for one Cop action."""
    if target == thief:
        return True, CAPTURE - (MAX_DEPTH - depth)
    if kind == "move":
        return False, thief_node(target, thief, free, left, size, depth - 1,
                                 alpha, beta, weights, budget, horizon - 1)
    after = free & ~(1 << target)
    if trapped(thief, after, size):
        return True, CAPTURE - (MAX_DEPTH - depth)
    # Placing forfeits this turn's move (book 3.4), and `barrier_tempo` is what that
    # costs. Without it the search walls patiently against evaders it could simply catch.
    return False, weights.barrier_tempo + thief_node(
        cop, thief, after, left - 1, size, depth - 1,
        alpha, beta, weights, budget, horizon - 1)


def thief_node(cop, thief, free, left, size, depth, alpha, beta, weights, budget, horizon):
    """Return the value of a position in which the Thief is to act (it minimises)."""
    if trapped(thief, free, size):
        return CAPTURE - (MAX_DEPTH - depth)
    if depth <= 0 or horizon <= 0 or not budget.spend():
        return evaluate(cop, thief, free, left, size, weights)
    worst = CAPTURE * 2
    for target in thief_actions(thief, free, size, cop):
        if target == cop:
            continue  # stepping onto the Cop is capture; no evader chooses it
        value = cop_node(cop, target, free, left, size, depth - 1,
                         alpha, min(beta, worst), weights, budget, horizon)
        worst = min(worst, value)
        if worst <= alpha:
            break
    return worst


def search_root(cop, thief, free, left, size, depth, weights: Weights, budget, horizon):
    """Return the best ``(action, value)`` at the root, ordered deterministically."""
    best: tuple[str, int] = ("move", cop)
    best_value = -CAPTURE * 3
    for kind, target in cop_actions(cop, free, size, left, thief):
        won, value = _cop_reply(kind, target, cop, thief, free, left, size, depth,
                                best_value, CAPTURE * 2, weights, budget, horizon)
        if won:
            return (kind, target), value
        if value > best_value:
            best, best_value = (kind, target), value
    return best, best_value
