"""Interception chase: close on the flight set with its spread priced in (M6-25).

Tracing the truth-fed incumbent against the mobility-aware archetypes showed the 0/40
was never about walls: **the chase itself never crossed the board.** The Thief bobs
between two rows on the far edge; row-matching and column-closing moves tie exactly
under Manhattan distance *and* under the flight-centroid lead (`|dest − centroid|`
collapses the set to its mean and cannot see the spread), so the fixed N-before-E
tie-break made the Cop mirror the bob on its own edge to the horizon — pocket 23–26
cells, zero walls, all thirty-five turns, on every seed. An oscillation is a mirror
that centroid pursuit polishes.

The replacement scores a move by the **sum of barrier-aware step distances to every
cell the believed Thief can legally hold next turn**, then the worst single one, then
the fixed order. The sum prices the spread: closing the pinned axis strictly beats
mirroring the bobbed one, so the dance breaks and the chase crosses the board. On an
open interior it degrades to flight-set pursuit; at walls and corners it converges
with the flight-centroid herding the arena measured. One ply of the real alternation,
wholly integer, deterministic (M6-03d) — the look-ahead form DEV-SPEC §7 sanctions.

A wall variant was built first and measured off: pricing candidate walls by the same
one-ply worst case both drained the quota mid-game (a wall that shaves one cell is a
losing trade fourteen times over) and stayed blind to the only wall worth buying —
the containment ratchet's lap-later cut, whose value appears one orbit after the
spend. So the wall layers stay exactly the shipped trio (finishing trap, squeeze,
containment ratchet), and this module changes nothing but the move underneath them:
a turn the trap, squeeze, and ratchet all decline is played as interception instead
of centroid chase. Every layer above is measured; the composition can add captures
but never surrender one.
"""

from __future__ import annotations

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move, legal_moves
from p2p_cop_agent.strategy.barrier_policy import (
    BarrierIntent,
    MoveIntent,
    TurnIntent,
    choose_turn_intent,
)
from p2p_cop_agent.strategy.containment import choose_containment
from p2p_cop_agent.strategy.pursuit import step_distances
from p2p_cop_agent.strategy.squeeze import choose_squeeze

_ACTIONS = list(Action)


def thief_replies(
    board: Board, believed: Coordinate, blocked: frozenset[Coordinate]
) -> tuple[Coordinate, ...]:
    """Return every cell the believed Thief can legally hold after one step.

    ``STAY`` is the believed cell itself; a destination behind a barrier is not a
    reply. Order is the fixed action order, so every ranking downstream is stable.
    """
    return (believed, *(apply_move(board, believed, action, blocked)
                        for action in legal_moves(board, believed, blocked)
                        if action is not Action.STAY))


def interception_move(
    board: Board,
    cop: Coordinate,
    believed: Coordinate,
    blocked: frozenset[Coordinate],
) -> Action:
    """Return the legal move that closes on the whole flight set, spread included.

    Ascending rank: summed barrier-aware step distance to every reply, then the
    worst single reply, then the fixed action order. A reply sealed off from some
    destination prices as one full board — unreachable ground is conceded ground.
    ``STAY`` competes on equal terms, so a sealed-off Cop still returns a legal
    action rather than wandering.
    """
    board.require_on_board(cop)
    board.require_on_board(believed)
    replies = thief_replies(board, believed, blocked)
    fields = [step_distances(board, reply, blocked) for reply in replies]
    far = board.grid_size * board.grid_size + 1

    def rank(action: Action) -> tuple[int, int, int]:
        destination = apply_move(board, cop, action, blocked)
        steps = [field.get(destination, far) for field in fields]
        return (sum(steps), max(steps), _ACTIONS.index(action))

    return min(legal_moves(board, cop, blocked), key=rank)


def shrinking_turn_intent(
    board: Board,
    cop: Coordinate,
    believed: Coordinate,
    barriers: BarrierField,
    previous: Coordinate | None = None,
) -> TurnIntent:
    """Return the tournament intent: the shipped wall stack over the interception chase.

    Layer order is the incumbent's — free capture move or finishing trap, else the
    squeeze, else the containment ratchet — and only the final fallback differs:
    a turn every wall layer declines is played as interception instead of the
    flight-centroid chase, because that chase is the measured hole the mobility-aware
    archetypes walk through.
    """
    chosen = choose_turn_intent(board, cop, believed, barriers)
    if isinstance(chosen, BarrierIntent):
        return chosen
    blocked = barriers.cells
    if apply_move(board, cop, chosen.action, blocked) == believed:
        return chosen  # the free capture move outranks everything
    distance = step_distances(board, believed, blocked).get(cop)
    if distance is not None and distance > 1:
        squeeze = choose_squeeze(board, cop, believed, barriers)
        if squeeze is not None:
            return BarrierIntent(squeeze)
        containment = choose_containment(board, cop, believed, barriers, previous)
        if containment is not None:
            return BarrierIntent(containment)
    return MoveIntent(interception_move(board, cop, believed, blocked))
