"""M5-11: one turn, driven by the phase machine, over a fake transport.

No socket here on purpose — the loop is transport-neutral, so a turn can be
driven, starved, and broken deterministically. The wire itself is proven in
`tests/integration/`.
"""


from p2p_cop_agent.orchestration.phases import Phase, PhaseMachine
from p2p_cop_agent.orchestration.turn_loop import (
    is_sealed_once,
    run_turn,
    sealed_steps,
)
from p2p_cop_agent.protocol.commit_reveal import TurnLedger

CHALLENGE = "0123456789abcdef0123456789abcdef"
OPPONENT_TURN = {"step": 1, "sender": "thief", "hint": "by the river",
                 "smell_grid": {"3,3": 0.9}, "commit": "a" * 64, "timestamp": "t1"}


class Sink:
    """A transport that records what it was sent and answers however it is told."""

    def __init__(self, reply: object = None, error: Exception | None = None) -> None:
        self.reply = reply if reply is not None else {"ok": True}
        self.error = error
        self.sent: list[dict] = []

    def receive_turn(self, message: dict) -> object:
        self.sent.append(message)
        if self.error is not None:
            raise self.error
        return self.reply


def decide(_incoming: dict | None) -> tuple[dict, dict]:
    return (
        {"move": "MOVE:N", "intent": "truth"},
        {"hint": "near the park", "smell_grid": {"0,0": 0.9}, "timestamp": "t"},
    )


def ledger() -> TurnLedger:
    return TurnLedger("police", public_challenge=CHALLENGE)


def test_one_turn_walks_the_declared_phases_in_order() -> None:
    machine, book = PhaseMachine(), ledger()
    record = run_turn(1, machine=machine, ledger=book, transport=Sink(),
                      receive=lambda: OPPONENT_TURN, decide=decide)

    assert record.phases == (
        Phase.COMPUTING_MOVE, Phase.COMMITTING, Phase.AWAITING_REVEAL,
        Phase.VERIFYING, Phase.WAITING_FOR_OPPONENT,
    )
    assert machine.current is Phase.WAITING_FOR_OPPONENT


def test_the_turn_sent_carries_the_commit_and_never_the_move() -> None:
    """The move stays private until the audit — the wire carries only a hash."""
    sink = Sink()
    run_turn(1, machine=PhaseMachine(), ledger=ledger(), transport=sink,
             receive=lambda: OPPONENT_TURN, decide=decide)

    sent = sink.sent[0]
    assert set(sent) >= {"step", "sender", "hint", "smell_grid", "commit", "timestamp"}
    assert "move" not in sent and "intent" not in sent and "nonce" not in sent
    assert len(sent["commit"]) == 64


def test_the_opening_peer_does_not_wait_for_a_turn_first() -> None:
    """The Thief moves first, so its opening turn has nothing to await."""
    def starve() -> dict | None:
        raise AssertionError("an opening turn must not await the opponent")

    record = run_turn(1, machine=PhaseMachine(), ledger=ledger(), transport=Sink(),
                      receive=starve, decide=decide, opens=True)
    assert record.received is None


def test_a_waiting_peer_receives_before_it_computes() -> None:
    record = run_turn(1, machine=PhaseMachine(), ledger=ledger(), transport=Sink(),
                      receive=lambda: OPPONENT_TURN, decide=decide)
    assert record.received == OPPONENT_TURN


def test_every_transition_is_reported_for_the_log() -> None:
    """M5-11d: the log manager must see each phase, not just the outcome."""
    seen: list[Phase] = []
    run_turn(1, machine=PhaseMachine(), ledger=ledger(), transport=Sink(),
             receive=lambda: OPPONENT_TURN, decide=decide, on_transition=seen.append)
    assert seen == [
        Phase.COMPUTING_MOVE, Phase.COMMITTING, Phase.AWAITING_REVEAL,
        Phase.VERIFYING, Phase.WAITING_FOR_OPPONENT,
    ]


def test_turns_alternate_and_each_step_is_sealed_exactly_once() -> None:
    machine, book, sink = PhaseMachine(), ledger(), Sink()
    for step in (1, 2, 3):
        run_turn(step, machine=machine, ledger=book, transport=sink,
                 receive=lambda: OPPONENT_TURN, decide=decide)

    assert sealed_steps(book) == (1, 2, 3)
    assert all(is_sealed_once(book, step) for step in (1, 2, 3))
