"""The single-gateway coordinator (M5-08).

Appendix E rule 3: one coordinator initialises MCP, activates the decision module,
and owns the log manager, deadline tracker, and watchdog -- and no subsystem
references another directly. This class is that coordinator. Every subsystem is
injected as a *port* (see ``ports.py``), so the gateway is the only place the five
are wired together, and each depends on an interface rather than a sibling.

The gateway **coordinates a turn; it never decides one** (book §9). It hands the
opponent's message to the decision module and publishes what comes back, but it
never inspects a move, computes a position, or reads the board. Deciding lives in the
decision module, and moving it here would collapse the very separation rule 3 exists
to keep. What the gateway *does* own is the wiring the subsystems cannot do for
themselves: every phase transition feeds the watchdog a heartbeat and the log manager
an event, and a trip drives the controlled shutdown, persisting through the log
manager -- the seam M5-06 left injected, now wired to a real subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass

from p2p_cop_agent.orchestration.phases import Phase, PhaseMachine
from p2p_cop_agent.orchestration.ports import (
    DeadlineTracker,
    DecisionModule,
    LivenessWatchdog,
    LogManager,
    MCPConnector,
)
from p2p_cop_agent.orchestration.shutdown import ShutdownReport, controlled_shutdown
from p2p_cop_agent.orchestration.turn_loop import Receive, TurnRecord, run_turn
from p2p_cop_agent.protocol.commit_reveal import TurnLedger


@dataclass(frozen=True, slots=True)
class Orchestrator:
    """The one coordinator that owns the five subsystems and wires them together."""

    connector: MCPConnector
    decision: DecisionModule
    log: LogManager
    deadlines: DeadlineTracker
    watchdog: LivenessWatchdog
    clock: object  # Callable[[], float]; kept structural so no clock impl is imported

    def run_turn(
        self,
        step: int,
        *,
        machine: PhaseMachine,
        ledger: TurnLedger,
        receive: Receive,
        opens: bool = False,
    ) -> TurnRecord:
        """Coordinate one turn: delegate the decision, feed the watchdog and log."""
        return run_turn(
            step,
            machine=machine,
            ledger=ledger,
            transport=self.connector,
            receive=receive,
            decide=self.decision.decide,
            opens=opens,
            on_transition=self._on_transition(step),
        )

    def shut_down(self, machine: PhaseMachine, *, reason: str) -> ShutdownReport:
        """Persist through the log manager, then route to the terminal state (M5-06)."""
        return controlled_shutdown(machine, persist_state=self._persist(reason), reason=reason)

    def _on_transition(self, step: int):
        """Return the per-phase hook that beats the watchdog and logs the transition."""

        def hook(phase: Phase) -> None:
            self.watchdog.heartbeat(self._now())
            self.log.record("phase", {"step": step, "phase": phase.value})

        return hook

    def _persist(self, reason: str):
        """Return the ``persist_state`` the shutdown calls, wired to the log manager."""

        def persist() -> None:
            self.log.record("persist_state", {"reason": reason})

        return persist

    def _now(self) -> float:
        """Read the injected clock without importing a clock implementation."""
        return self.clock()  # type: ignore[operator]
