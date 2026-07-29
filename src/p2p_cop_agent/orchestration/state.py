"""Immutable Cop-local state: only what this peer may legitimately know.

The type deliberately has **no field able to hold the opponent's position**.
Starting cells are mutually agreed and public, but the Thief's position from the
first move onward is private truth the Cop must never represent. Presuming a
Thief cell is a caller's argument to a policy, never stored state.

Every transition returns a new instance. Transitions are primitives, not a turn:
they do not increment the turn, order events, or enforce
barrier-versus-movement exclusivity, because live-turn semantics remain
provisional. Composing them into a turn belongs to the rules harness.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board, validate_start_coordinates
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move, legal_moves

DEFAULT_BARRIER_QUOTA_KEY = "max_barriers"


class StateError(ValueError):
    """Raised when Cop-local state is malformed or a transition is illegal."""


@dataclass(frozen=True, slots=True)
class CopState:
    """What the Cop knows locally: its own cell, disclosed barriers, and turn."""

    board: Board
    position: Coordinate
    barriers: BarrierField
    turn: int = 0

    def __post_init__(self) -> None:
        if isinstance(self.turn, bool) or not isinstance(self.turn, int):
            raise StateError(f"turn must be an integer, got {self.turn!r}")
        if self.turn < 0:
            raise StateError(f"turn must not be negative, got {self.turn}")
        self.board.require_on_board(self.position)

    @classmethod
    def opening(cls, game_config: Mapping[str, object]) -> CopState:
        """Build the opening state from a validated match configuration.

        The configured Thief start is validated and then discarded: it is not
        retained anywhere in Cop-local state.
        """
        cop_start, _thief_start = validate_start_coordinates(game_config)
        section = game_config.get("movement_and_barriers")
        if not isinstance(section, Mapping):
            raise StateError("game config is missing a movement_and_barriers object")
        quota = section.get(DEFAULT_BARRIER_QUOTA_KEY)
        if isinstance(quota, bool) or not isinstance(quota, int):
            raise StateError(f"{DEFAULT_BARRIER_QUOTA_KEY} must be an integer, got {quota!r}")
        return cls(
            board=Board.from_config(game_config),
            position=cop_start,
            barriers=BarrierField(max_barriers=quota),
            turn=0,
        )

    @property
    def blocked(self) -> frozenset[Coordinate]:
        """Return the disclosed barrier cells for movement checks."""
        return self.barriers.cells

    def legal_actions(self) -> tuple[Action, ...]:
        """Return every action legal from the current cell and barrier set."""
        return legal_moves(self.board, self.position, self.blocked)

    def moved(self, action: Action) -> CopState:
        """Return the state reached by one legal action; illegal moves reject."""
        return replace(self, position=apply_move(self.board, self.position, action, self.blocked))

    def with_barrier_at(self, cell: Coordinate) -> CopState:
        """Return the state with one disclosed barrier placed on the Cop's turn."""
        return replace(self, barriers=self.barriers.place_adjacent(self.board, self.position, cell))

    def next_turn(self) -> CopState:
        """Return the state with the turn counter advanced by one."""
        return replace(self, turn=self.turn + 1)
