"""M5-14: an opponent's content rejection is a scored outcome, not a retry loop.

The two failure kinds were kept disjoint at the connector (M5-03c): `TransportError`
is a carrier fault, `PeerRejectionError` is the peer reaching us and declining. This
is the milestone-level proof that the distinction actually changes behaviour --
retry is for the carrier and never for a decided game outcome (M5-14a) -- and that an
unrecoverable rejection reaches a defined, scorable terminal state (M5-14b). The
mechanisms already exist (the disjoint types, `attempt`'s `retry_on`, and
`turn_loop._deliver`); this pins the behaviour they combine to give.
"""

import pytest

from p2p_cop_agent.adapters.fastmcp_client import PeerRejectionError, TransportError
from p2p_cop_agent.domain.scoring import Outcome
from p2p_cop_agent.orchestration.phases import PhaseMachine
from p2p_cop_agent.orchestration.sub_game import run_sub_game_over_wire
from p2p_cop_agent.protocol.commit_reveal import TurnLedger
from p2p_cop_agent.services.deadlines import RetryPolicy, attempt
from tests.unit.test_turn_loop import CHALLENGE, OPPONENT_TURN, Sink, decide

POLICY = RetryPolicy(max_retries=3, backoff_sec=0, response_timeout_sec=30)


def test_a_transport_fault_is_retried_until_it_succeeds() -> None:
    calls: list[int] = []

    def flaky() -> str:
        calls.append(1)
        if len(calls) < 2:
            raise TransportError("carrier blip")
        return "delivered"

    assert attempt(flaky, POLICY, clock=lambda: 0.0, retry_on=(TransportError,)) == "delivered"
    assert len(calls) == 2  # failed once, retried, then succeeded


def test_a_content_rejection_is_not_retried() -> None:
    """M5-14a: a decided rejection propagates at once, even with attempts to spare."""
    calls: list[int] = []

    def refused() -> str:
        calls.append(1)
        raise PeerRejectionError("your move is illegal")

    with pytest.raises(PeerRejectionError):
        attempt(refused, POLICY, clock=lambda: 0.0, retry_on=(TransportError,))
    assert len(calls) == 1  # tried once and never retried a lost game


def test_a_rejection_in_a_sub_game_is_a_scored_technical_loss() -> None:
    """M5-14b: the match reaches a defined terminal state, and the audit still goes
    out so the outcome can be checked and scored."""
    result = run_sub_game_over_wire(
        machine=PhaseMachine(),
        ledger=TurnLedger("police", public_challenge=CHALLENGE),
        transport=Sink(error=PeerRejectionError("declined")),
        receive=lambda: OPPONENT_TURN,
        decide=decide,
        survival_threshold=5,
    )
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert result.audit is not None
    assert result.audit["result_claim"] == "timeout"


def test_the_two_failure_kinds_stay_disjoint() -> None:
    """The guarantee the retry rule rests on: neither is the other, so a rejection
    can never be caught by `except TransportError` and quietly retried."""
    assert not issubclass(PeerRejectionError, TransportError)
    assert not issubclass(TransportError, PeerRejectionError)
