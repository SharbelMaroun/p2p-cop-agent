"""Immutable, reproducible history of Cop-local state.

A history is an ordered tuple of :class:`CopState` snapshots. It is append-only:
every operation returns a new history and no recorded snapshot is ever mutated
or removed, so a recorded past cannot be rewritten.

Reproducibility follows from the parts: ``CopState`` and everything it holds are
frozen value types, and every transition is deterministic. Replaying the same
opening state and the same action sequence therefore yields an equal history,
which is what makes a later replay or verifier meaningful.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from p2p_cop_agent.domain.actions import Action
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.orchestration.state import CopState, StateError


@dataclass(frozen=True, slots=True)
class CopHistory:
    """An append-only ordered record of Cop-local state snapshots."""

    snapshots: tuple[CopState, ...]

    def __post_init__(self) -> None:
        if not self.snapshots:
            raise StateError("history must contain at least the opening state")
        for snapshot in self.snapshots:
            if not isinstance(snapshot, CopState):
                raise StateError(f"history entry must be a CopState, got {snapshot!r}")

    @classmethod
    def starting(cls, state: CopState) -> CopHistory:
        """Return a history holding only the opening state."""
        return cls((state,))

    @property
    def current(self) -> CopState:
        """Return the most recently recorded state."""
        return self.snapshots[-1]

    @property
    def opening(self) -> CopState:
        """Return the first recorded state."""
        return self.snapshots[0]

    @property
    def positions(self) -> tuple[Coordinate, ...]:
        """Return the Cop cell from every recorded snapshot, in order."""
        return tuple(snapshot.position for snapshot in self.snapshots)

    def __len__(self) -> int:
        """Return the number of recorded snapshots."""
        return len(self.snapshots)

    def __iter__(self) -> Iterator[CopState]:
        """Iterate recorded snapshots oldest first."""
        return iter(self.snapshots)

    def record(self, state: CopState) -> CopHistory:
        """Return a new history with one more snapshot appended."""
        return CopHistory((*self.snapshots, state))

    def apply(self, action: Action) -> CopHistory:
        """Return a new history after moving the current state by one action."""
        return self.record(self.current.moved(action))

    def apply_all(self, actions: Iterable[Action]) -> CopHistory:
        """Return a new history after applying each action in order."""
        history = self
        for action in actions:
            history = history.apply(action)
        return history
