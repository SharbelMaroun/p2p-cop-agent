"""Deterministic Cop pursuit baseline.

Contract-independent: this module reads only the public domain API and its
explicit arguments. It defines no new game rule, performs no I/O, touches no
shared-contract byte, and knows nothing about transport or protocol state.

The presumed Thief cell is supplied by the caller. Deriving it from scent or
belief is deferred M6 work and is deliberately not attempted here.

Distance is a barrier-aware breadth-first step count rather than a plain
row/column difference, so a cell that looks closer is not preferred when
barriers make it longer to reach. Ties are broken by the fixed ``Action``
declaration order (``N``, ``S``, ``E``, ``W``, ``STAY``).

``STAY`` sits last in that order, but on a grid it never merely ties: the cell
graph is bipartite, so an adjacent cell's distance always differs from the
current cell's by exactly one. ``STAY`` therefore wins only when it is strictly
best — the Cop already stands on the target — or when no legal move reaches the
target at all.

The policy chooses movement only. Whether to give up the turn to place a
barrier is a separate decision and is not modelled here, because
barrier-versus-movement turn exclusivity depends on the live-turn state
machine, which remains provisional.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Set as AbstractSet

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move, legal_moves

_NO_BARRIERS: frozenset[Coordinate] = frozenset()


def _neighbours(
    board: Board,
    cell: Coordinate,
    blocked: AbstractSet[Coordinate],
) -> tuple[Coordinate, ...]:
    """Return every cell reached from ``cell`` by one legal directional move.

    ``STAY`` is excluded: it never enters a new cell and would add a self-loop
    that cannot shorten any path.
    """
    return tuple(
        apply_move(board, cell, action, blocked)
        for action in legal_moves(board, cell, blocked)
        if action is not Action.STAY
    )


def step_distances(
    board: Board,
    origin: Coordinate,
    blocked: AbstractSet[Coordinate] = _NO_BARRIERS,
) -> dict[Coordinate, int]:
    """Return barrier-aware step counts from ``origin`` to every reachable cell.

    Cells enclosed by barriers or board edges are absent from the result rather
    than being given a sentinel distance. Movement is symmetric, so the map is
    equally valid read as "steps from ``origin``" or "steps to ``origin``".
    """
    board.require_on_board(origin)
    distances = {origin: 0}
    queue = deque([origin])
    while queue:
        cell = queue.popleft()
        for neighbour in _neighbours(board, cell, blocked):
            if neighbour not in distances:
                distances[neighbour] = distances[cell] + 1
                queue.append(neighbour)
    return distances


def choose_action(
    board: Board,
    cop: Coordinate,
    target: Coordinate,
    blocked: AbstractSet[Coordinate] = _NO_BARRIERS,
) -> Action:
    """Return the deterministic legal action that best closes on ``target``.

    Every candidate is drawn from :func:`legal_moves`, so the result is always
    legal for the given board and barriers. Among candidates the action whose
    destination has the smallest barrier-aware distance to ``target`` wins, and
    equal scores fall back to ``Action`` declaration order.

    When no legal move can reach ``target`` at all — the Cop is sealed off from
    it by barriers or edges — the policy returns ``Action.STAY`` rather than
    wandering. ``STAY`` is legal for any on-board cell, so a legal action is
    always produced. Off-board inputs are rejected by ``require_on_board``.
    """
    board.require_on_board(cop)
    board.require_on_board(target)
    distances = step_distances(board, target, blocked)
    scored = [
        (distances[destination], action)
        for action in legal_moves(board, cop, blocked)
        for destination in (apply_move(board, cop, action, blocked),)
        if destination in distances
    ]
    if not scored:
        return Action.STAY
    return min(scored, key=lambda pair: pair[0])[1]
