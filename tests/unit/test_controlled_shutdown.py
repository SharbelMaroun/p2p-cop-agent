"""M5-06c/M5-06d: persist then shut down cleanly when the watchdog trips.

The contract here is ordering and fail-closed behaviour, not a storage format: on a
trip the runtime persists its state **first**, then routes the declared phase
machine to its one terminal state (`TECHNICAL_LOSS`). Persisting must never be able
to block the terminal transition -- a shutdown that hangs is the exact failure the
watchdog exists to prevent -- so a failing ``persist_state`` still ends the game.
"""

import pytest

from p2p_cop_agent.orchestration.phases import Phase, PhaseMachine
from p2p_cop_agent.orchestration.shutdown import (
    ShutdownError,
    controlled_shutdown,
    heartbeat_on_transition,
)
from p2p_cop_agent.services.watchdog import Watchdog


def _machine_at(phase: Phase) -> PhaseMachine:
    """Drive a fresh machine to ``phase`` using only declared transitions."""
    machine = PhaseMachine()
    path = {
        Phase.WAITING_FOR_OPPONENT: (),
        Phase.COMPUTING_MOVE: (Phase.COMPUTING_MOVE,),
        Phase.COMMITTING: (Phase.COMPUTING_MOVE, Phase.COMMITTING),
        Phase.AWAITING_REVEAL: (
            Phase.COMPUTING_MOVE, Phase.COMMITTING, Phase.AWAITING_REVEAL,
        ),
    }[phase]
    for step in path:
        machine.to(step)
    return machine


def test_persist_runs_before_the_terminal_transition() -> None:
    machine = _machine_at(Phase.AWAITING_REVEAL)
    log: list[str] = []
    report = controlled_shutdown(
        machine, persist_state=lambda: log.append("persisted"), reason="watchdog"
    )
    assert log == ["persisted"]
    assert machine.current is Phase.TECHNICAL_LOSS
    assert report.persisted is True
    assert report.phase is Phase.TECHNICAL_LOSS
    assert report.reason == "watchdog"


def test_a_waiting_peer_reaches_the_loss_through_the_declared_bridge() -> None:
    """WAITING_FOR_OPPONENT has no direct loss edge, so it steps through
    COMPUTING_MOVE -- the same documented path the turn loop uses, not a new edge."""
    machine = _machine_at(Phase.WAITING_FOR_OPPONENT)
    controlled_shutdown(machine, persist_state=lambda: None, reason="watchdog")
    assert machine.current is Phase.TECHNICAL_LOSS
    assert Phase.COMPUTING_MOVE in machine.history


def test_a_failing_persist_still_reaches_the_terminal_state() -> None:
    def boom() -> None:
        raise OSError("disk full")

    machine = _machine_at(Phase.AWAITING_REVEAL)
    report = controlled_shutdown(machine, persist_state=boom, reason="watchdog")
    assert report.persisted is False
    assert machine.current is Phase.TECHNICAL_LOSS


def test_a_synchronous_phase_has_no_defined_terminal_exit() -> None:
    """A trip mid-commit is undefined: bridging it would fake a reveal, so refuse."""
    machine = _machine_at(Phase.COMMITTING)
    with pytest.raises(ShutdownError):
        controlled_shutdown(machine, persist_state=lambda: None, reason="watchdog")
    assert machine.current is Phase.COMMITTING


def test_shutting_down_an_already_terminal_machine_is_idempotent() -> None:
    machine = _machine_at(Phase.AWAITING_REVEAL)
    controlled_shutdown(machine, persist_state=lambda: None, reason="first")
    report = controlled_shutdown(machine, persist_state=lambda: None, reason="again")
    assert report.phase is Phase.TECHNICAL_LOSS


def test_transitions_feed_the_watchdog_as_heartbeats() -> None:
    """M5-06a: the main loop already emits a transition per phase (M5-11d); the
    watchdog subscribes to that stream instead of the loop growing new plumbing."""
    clock = iter([10.0, 20.0, 30.0])
    wd = Watchdog.started_at(now=0.0, timeout_sec=60.0)
    beat = heartbeat_on_transition(wd, clock=lambda: next(clock))
    beat(Phase.COMPUTING_MOVE)
    beat(Phase.COMMITTING)
    assert wd.silent_for(25.0) == 5.0  # last beat was at 20.0


def test_a_tripped_watchdog_stops_feeding_itself() -> None:
    wd = Watchdog.started_at(now=0.0, timeout_sec=60.0)
    wd.check(60.0)
    beat = heartbeat_on_transition(wd, clock=lambda: 61.0)
    with pytest.raises(Exception):  # noqa: B017,PT011 - WatchdogError surfaces
        beat(Phase.COMPUTING_MOVE)
