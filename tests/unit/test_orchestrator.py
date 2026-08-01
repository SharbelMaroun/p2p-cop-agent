"""M5-08: the single-gateway coordinator wires the subsystems and never decides.

The gateway is driven with fake subsystem ports so its coordination is observable:
it must delegate the decision, beat the watchdog and log on every transition, and
persist through the log manager on shutdown -- all without ever computing a move
itself. The import-side of rule 3 (no subsystem imports a sibling) is proven in
`test_gateway_boundary`.
"""

from p2p_cop_agent.orchestration.orchestrator import Orchestrator
from p2p_cop_agent.orchestration.phases import Phase, PhaseMachine
from p2p_cop_agent.protocol.commit_reveal import TurnLedger
from p2p_cop_agent.services.watchdog import Watchdog
from tests.unit.test_turn_loop import CHALLENGE, OPPONENT_TURN, Sink


class Decider:
    """A stand-in decision module that records what it was asked and answers fixed."""

    def __init__(self) -> None:
        self.calls: list[dict | None] = []

    def decide(self, incoming: dict | None) -> tuple[dict, dict]:
        self.calls.append(incoming)
        return (
            {"move": "MOVE:N", "intent": "truth"},
            {"hint": "park", "smell_grid": {"0,0": 0.9}, "timestamp": "t"},
        )


class Log:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict | None]] = []

    def record(self, event: str, detail: dict | None = None) -> None:
        self.events.append((event, detail))


class Deadlines:
    def deadline(self, now: float) -> float:
        return now  # unused on the run_turn path; present to satisfy the port


def _ledger() -> TurnLedger:
    return TurnLedger("police", public_challenge=CHALLENGE)


def _gateway(**overrides: object) -> Orchestrator:
    defaults: dict = {
        "connector": Sink(),
        "decision": Decider(),
        "log": Log(),
        "deadlines": Deadlines(),
        "watchdog": Watchdog.started_at(now=0.0, timeout_sec=60.0),
        "clock": lambda: 5.0,
    }
    defaults.update(overrides)
    return Orchestrator(**defaults)  # type: ignore[arg-type]


def test_the_gateway_delegates_the_decision_and_publishes_what_it_returns() -> None:
    decider = Decider()
    record = _gateway(decision=decider).run_turn(
        1, machine=PhaseMachine(), ledger=_ledger(), receive=lambda: OPPONENT_TURN
    )
    assert decider.calls == [OPPONENT_TURN]  # it asked the decision module
    assert record.sent["hint"] == "park"  # and published exactly its answer
    assert "move" not in record.sent  # the move stays sealed; the gateway added nothing


def test_every_transition_feeds_the_watchdog_and_the_log() -> None:
    watchdog = Watchdog.started_at(now=0.0, timeout_sec=60.0)
    log = Log()
    ticks = iter([10.0, 20.0, 30.0, 40.0, 50.0])
    _gateway(watchdog=watchdog, log=log, clock=lambda: next(ticks)).run_turn(
        1, machine=PhaseMachine(), ledger=_ledger(), receive=lambda: OPPONENT_TURN
    )
    assert [event for event, _ in log.events] == ["phase"] * 5
    assert watchdog.silent_for(55.0) == 5.0  # last heartbeat was the 50.0 transition


def test_shut_down_persists_through_the_log_then_reaches_the_terminal_state() -> None:
    log = Log()
    machine = PhaseMachine()  # owed the opponent's turn
    report = _gateway(log=log).shut_down(machine, reason="watchdog silence")
    assert ("persist_state", {"reason": "watchdog silence"}) in log.events
    assert machine.current is Phase.TECHNICAL_LOSS
    assert report.persisted is True
