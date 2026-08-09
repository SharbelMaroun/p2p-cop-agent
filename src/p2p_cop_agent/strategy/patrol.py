"""Where to go when the opponent has told us nothing at all (M6-27).

A Cop that has never decoded an observation holds the uniform prior, and
:meth:`Belief.most_likely` breaks that tie row-major -- returning the board's first
cell, ``(0, 0)``, which is exactly the Cop's own opening square. Aiming the pursuit
there produced "I am already on my target", so the served policy answered ``STAY`` and
kept answering it: in the `amireman` friendly the Cop stood on its start cell for 26
consecutive turns, spent no barrier, and lost on the horizon.

Standing still is *strictly dominated* here, and the reason is worth stating because it
is not the obvious one. The Cop's evidence is the window the **opponent** transmits, so
walking around does not improve what it can see -- there is no "searching for a better
vantage point" in this game. What moving does improve is the chance of **landing on**
the Thief, since occupying its cell is itself the capture condition. A stationary Cop
has exactly zero of those chances; a sweeping one has one per turn.

So the blind policy is a deterministic tour of waypoints spread across the board, held
long enough to actually be reached rather than re-aimed every turn (which would leave
the Cop oscillating between two of them). It is only a fallback: one decoded
observation and the belief pursuit takes over again.
"""

from __future__ import annotations

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.belief import Belief

# Turns spent aiming at one waypoint. A crossing of the 7×7 floor costs six steps, so a
# shorter hold would re-aim before arriving and the Cop would never cover ground.
WAYPOINT_HOLD_TURNS = 7

# How many turns a decoded observation still counts as localisation. Beyond this the
# trail we are aiming at is old enough that the Thief could be anywhere within reach,
# and sitting on the last known cell is the standing-still failure by another route.
STALE_AFTER_TURNS = 3

# Fraction above the flat share that counts as a real peak. A belief whose argmax is
# barely above uniform localises nothing, and its row-major tie-break is the corner.
PEAK_MARGIN = 1.5


def is_localised(belief: Belief) -> bool:
    """Return whether ``belief`` actually points somewhere.

    Three separate paths produced a flat distribution in play, and each one aimed the
    pursuit at ``(0, 0)``: never having observed, an observation whose likelihood
    carried no evidence (``Belief.updated`` returns the prior, and the prior here is
    rebuilt uniform every turn), and a decode that yielded no cells. Testing the
    distribution catches all three at once, rather than each mechanism separately.
    """
    values = list(belief.probabilities.values())
    if not values:
        return False
    return max(values) > PEAK_MARGIN / len(values)


def needs_sweep(belief: Belief, seen_turn: int | None, turn: int) -> bool:
    """Return whether the Cop should sweep rather than pursue its belief."""
    if seen_turn is None or turn - seen_turn > STALE_AFTER_TURNS:
        return True
    return not is_localised(belief)


def sweep_waypoints(board: Board) -> tuple[Coordinate, ...]:
    """Return the tour: the centre, then the four quadrant centres.

    Scaled from the board rather than hard-coded, so a negotiated 9×9 or 11×11 sweeps
    the same shape. Duplicates are collapsed for a board too small to distinguish them.
    """
    low = board.min_index
    high = board.max_index
    mid = (low + high) // 2
    near = (low + mid) // 2
    far = (mid + high + 1) // 2
    ordered = (
        (mid, mid), (near, near), (near, far), (far, far), (far, near),
    )
    seen: list[Coordinate] = []
    for row, col in ordered:
        cell = Coordinate(row, col)
        if cell not in seen:
            seen.append(cell)
    return tuple(seen)


def aim(
    board: Board, belief: Belief, seen_turn: int | None, turn: int, cop: Coordinate
) -> Coordinate:
    """Return where the Cop should aim: its belief's peak, or the sweep when blind.

    The whole "do we actually know anything?" decision lives here rather than in the
    turn loop, so the wire layer asks one question and cannot reintroduce the corner
    freeze by forgetting a case.
    """
    if needs_sweep(belief, seen_turn, turn):
        return sweep_target(board, turn, cop)
    return Coordinate.from_pair(belief.most_likely())


def sweep_target(board: Board, turn: int, cop: Coordinate | None = None) -> Coordinate:
    """Return the waypoint a blind Cop should aim at on ``turn`` (1-based).

    Deterministic in the turn number and position, so two runs of the same match produce
    the same sweep and the policy stays reproducible (M6-03d).

    A waypoint the Cop already occupies is skipped to the next one. Without that the
    sweep re-lands on the standing-still bug it exists to fix: "go where you already
    are" is `STAY`, and the hold would keep answering it for a whole waypoint's worth
    of turns.
    """
    tour = sweep_waypoints(board)
    index = max(0, turn - 1) // WAYPOINT_HOLD_TURNS % len(tour)
    if cop is not None and tour[index] == cop:
        index = (index + 1) % len(tour)
    return tour[index]
