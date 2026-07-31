"""M5-11: the turn loop's failure paths, which are the point of the phase machine.

A loop that only works when everything works is not a loop you can hand a
classmate's agent. Each test here breaks one thing and asserts the peer reaches a
*declared* terminal state instead of hanging or improvising.

The happy path lives in `test_turn_loop.py`.
"""

import pytest

from p2p_cop_agent.adapters.fastmcp_client import PeerRejectionError, TransportError
from p2p_cop_agent.orchestration.phases import Phase, PhaseMachine
from p2p_cop_agent.orchestration.turn_loop import TurnLoopError, is_sealed_once, run_turn
from tests.unit.test_turn_loop import OPPONENT_TURN, Sink, decide, ledger


def test_a_silent_opponent_reaches_the_terminal_state_rather_than_hanging() -> None:
    """`[AE-7]`: silence is not patience. It must decide, not wait forever.

    The exit passes through `COMPUTING_MOVE` because the declared table has no
    `WAITING_FOR_OPPONENT -> TECHNICAL_LOSS` edge. That is followed as written
    rather than patched; see `turn_loop._await_opponent`.
    """
    machine = PhaseMachine()
    with pytest.raises(TurnLoopError, match="did not send a turn"):
        run_turn(1, machine=machine, ledger=ledger(), transport=Sink(),
                 receive=lambda: None, decide=decide)
    assert machine.current is Phase.TECHNICAL_LOSS
    assert machine.history[-2:] == (Phase.COMPUTING_MOVE, Phase.TECHNICAL_LOSS)


@pytest.mark.parametrize("failure", [TransportError("unreachable"), PeerRejectionError("no")])
def test_a_turn_sealed_but_undelivered_is_never_resealed(failure: Exception) -> None:
    """M5-11b: re-sealing would give one step two hashes and fail the audit.

    A commitment is a promise. If delivery fails the peer keeps the promise it
    made and takes the terminal exit; it does not quietly make a different one.
    """
    machine, book = PhaseMachine(), ledger()
    with pytest.raises(TurnLoopError, match="sealed but not delivered"):
        run_turn(1, machine=machine, ledger=book, transport=Sink(error=failure),
                 receive=lambda: OPPONENT_TURN, decide=decide)

    assert is_sealed_once(book, 1)
    assert machine.current is Phase.TECHNICAL_LOSS


def test_a_refusing_acknowledgement_ends_the_turn() -> None:
    machine = PhaseMachine()
    with pytest.raises(TurnLoopError, match="sealed but not delivered"):
        run_turn(1, machine=machine, ledger=ledger(), transport=Sink(reply={"ok": False}),
                 receive=lambda: OPPONENT_TURN, decide=decide)
    assert machine.current is Phase.TECHNICAL_LOSS


@pytest.mark.parametrize("ack", [{"status": "ok"}, {"status": "delivered"}, {}])
def test_a_foreign_acknowledgement_shape_still_completes_the_turn(ack: dict) -> None:
    """A classmate's peer need not answer in our dialect for the turn to stand."""
    machine = PhaseMachine()
    run_turn(1, machine=machine, ledger=ledger(), transport=Sink(reply=ack),
             receive=lambda: OPPONENT_TURN, decide=decide)
    assert machine.current is Phase.WAITING_FOR_OPPONENT


def test_a_transport_without_the_tool_is_refused_before_sealing_matters() -> None:
    with pytest.raises(TurnLoopError, match="does not expose receive_turn"):
        run_turn(1, machine=PhaseMachine(), ledger=ledger(), transport=object(),
                 receive=lambda: OPPONENT_TURN, decide=decide)


def test_a_step_that_does_not_advance_is_refused_by_the_ledger() -> None:
    machine, book, sink = PhaseMachine(), ledger(), Sink()
    run_turn(2, machine=machine, ledger=book, transport=sink,
             receive=lambda: OPPONENT_TURN, decide=decide)
    with pytest.raises(TurnLoopError, match="could not be sealed"):
        run_turn(2, machine=machine, ledger=book, transport=sink,
                 receive=lambda: OPPONENT_TURN, decide=decide)
