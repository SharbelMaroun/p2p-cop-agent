"""Controlled shutdown on a watchdog trip (M5-06c, M5-06d).

When the watchdog trips the book asks for two things in order: ``persist_state()``
then ``controlled_shutdown()``. This module owns that ordering and, above all, its
fail-closed guarantee: persisting must never be able to block the terminal
transition, because a shutdown that hangs is the exact failure the watchdog exists
to catch. So a failing ``persist_state`` is recorded and the game still ends.

The concrete snapshot writer is not decided here -- that is the log manager's job
(M5-12) and the orchestrator's to wire (M5-08). ``persist_state`` is therefore an
injected callable, and this module guarantees only that it runs first and that the
declared phase machine reaches its one terminal state afterwards `[AE-7]`.

Routing to ``TECHNICAL_LOSS`` follows the declared table, never a new edge. A peer
that is merely *waiting* has no direct loss transition, so it steps through
``COMPUTING_MOVE`` -- the same bridge ``turn_loop._await_opponent`` already uses. A
trip in a synchronous phase (``COMMITTING``/``VERIFYING``) has no defined exit, and
bridging one would fake a reveal, so it is refused rather than invented.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from p2p_cop_agent.orchestration.phases import TRANSITIONS, Phase, PhaseMachine
from p2p_cop_agent.services.watchdog import Watchdog

# Persist whatever is needed to reconstruct and audit the match. Wired by M5-08.
PersistState = Callable[[], object]
# The loop already emits one transition per phase (M5-11d); this consumes them.
OnTransition = Callable[[Phase], None]


class ShutdownError(RuntimeError):
    """Raised when a trip lands in a phase with no declared terminal exit."""


@dataclass(frozen=True, slots=True)
class ShutdownReport:
    """What a controlled shutdown did: enough to log why the game ended."""

    reason: str
    persisted: bool
    phase: Phase


def heartbeat_on_transition(watchdog: Watchdog, *, clock: Callable[[], float]) -> OnTransition:
    """Turn the loop's phase transitions into watchdog heartbeats (M5-06a).

    Reuses the existing ``on_transition`` hook rather than threading a watchdog
    through the loop's signature: every phase entered is a sign of life.
    """

    def beat(_phase: Phase) -> None:
        watchdog.heartbeat(clock())

    return beat


def controlled_shutdown(
    machine: PhaseMachine, *, persist_state: PersistState, reason: str
) -> ShutdownReport:
    """Persist, then route the phase machine to its one terminal state."""
    persisted = _persist(persist_state)
    _route_to_terminal(machine)
    return ShutdownReport(reason=reason, persisted=persisted, phase=machine.current)


def _persist(persist_state: PersistState) -> bool:
    """Run the injected writer, but never let it block the shutdown."""
    try:
        persist_state()
    except Exception:  # noqa: BLE001 - a failed snapshot must not stop the loss
        return False
    return True


def _route_to_terminal(machine: PhaseMachine) -> None:
    """Reach ``TECHNICAL_LOSS`` using only declared transitions."""
    if machine.is_terminal:
        return
    if Phase.TECHNICAL_LOSS in TRANSITIONS[machine.current]:
        machine.fail()
        return
    if machine.current is Phase.WAITING_FOR_OPPONENT:
        machine.to(Phase.COMPUTING_MOVE)
        machine.fail()
        return
    raise ShutdownError(
        f"watchdog tripped in {machine.current.value}, which has no declared "
        "terminal exit; bridging it would fabricate a phase"
    )
