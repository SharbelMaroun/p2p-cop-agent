"""M5-10d/M5-10e: a whole sub-game decided by claims, then proven by the audit.

Nothing here referees. Each test drives the peer with an opponent script and asserts
it reaches the outcome the *opponent's answers* imply — which is the only thing a
peer that cannot see the board is entitled to conclude.
"""

import pytest

from p2p_cop_agent.domain.scoring import Outcome
from p2p_cop_agent.orchestration.phases import PhaseMachine
from p2p_cop_agent.orchestration.sub_game import RESULT_CLAIMS, run_sub_game_over_wire
from p2p_cop_agent.orchestration.turn_loop import TurnLoopError
from p2p_cop_agent.protocol.commit_reveal import TurnLedger, verify_audit
from tests.unit.test_turn_loop import CHALLENGE, Sink, decide


def turn(step: int, **extra: object) -> dict:
    return {"step": step, "sender": "thief", "hint": "somewhere",
            "smell_grid": {"3,3": 0.9}, "commit": "a" * 64,
            "timestamp": f"t{step}", **extra}


class Opponent:
    """Replays a scripted sequence of opponent turns, then falls silent."""

    def __init__(self, *messages: dict) -> None:
        self.messages = list(messages)

    def __call__(self) -> dict | None:
        return self.messages.pop(0) if self.messages else None


def play(receive, *, threshold: int = 5, transport=None, **kwargs):
    return run_sub_game_over_wire(
        machine=PhaseMachine(),
        ledger=TurnLedger("police", public_challenge=CHALLENGE),
        transport=transport if transport is not None else Sink(),
        receive=receive,
        decide=decide,
        survival_threshold=threshold,
        **kwargs,
    )


def test_a_confirmed_capture_ends_the_sub_game_immediately() -> None:
    """Only the peer that knows where it stood can end it — so its answer decides."""
    result = play(Opponent(
        turn(1),
        turn(2, claim_response={"claim": [3, 3], "caught": True}),
        turn(3),
    ))
    assert result.outcome is Outcome.CAPTURE
    assert result.steps == 2
    assert "confirmed capture" in result.reason


def test_a_denied_capture_claim_does_not_end_the_sub_game() -> None:
    """A claim asserts nothing; a denial is simply the game continuing."""
    result = play(Opponent(*(turn(s, claim_response={"claim": [1, 1], "caught": False})
                             for s in range(1, 6))))
    assert result.outcome is Outcome.SURVIVAL
    assert result.steps == 5


def test_a_survival_claim_ends_the_sub_game() -> None:
    result = play(Opponent(turn(1), turn(2, win_claim={"type": "survival"})))
    assert result.outcome is Outcome.SURVIVAL
    assert result.reason == "the opponent claimed survival"


def test_reaching_the_threshold_uncaught_is_survival_inclusively() -> None:
    """`U-027`: completing the final step uncaptured is a Thief win, not one short."""
    result = play(Opponent(*(turn(s) for s in range(1, 6))), threshold=5)
    assert result.outcome is Outcome.SURVIVAL
    assert result.steps == 5
    assert len(result.turns) == 5


def test_a_silent_opponent_is_a_technical_loss_not_a_hang() -> None:
    result = play(Opponent(turn(1)), threshold=5)
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert result.steps == 1
    assert "did not send a turn" in result.reason


# --- the audit is the point ----------------------------------------------------


def test_the_audit_reveals_every_sealed_turn_and_recomputes() -> None:
    """`[AE-19]`: what we send must reproduce, or we score zero for both sides."""
    result = play(Opponent(*(turn(s) for s in range(1, 4))), threshold=3)

    assert result.audit is not None
    assert len(result.audit["records"]) == 3
    assert verify_audit(result.audit) is True


def test_the_audit_claim_matches_the_outcome() -> None:
    captured = play(Opponent(turn(1, claim_response={"claim": [3, 3], "caught": True})))
    assert captured.audit["result_claim"] == RESULT_CLAIMS[Outcome.CAPTURE] == "capture"

    survived = play(Opponent(*(turn(s) for s in range(1, 4))), threshold=3)
    assert survived.audit["result_claim"] == "survival"


def test_the_audit_is_delivered_to_the_opponent() -> None:
    class Recorder(Sink):
        def __init__(self) -> None:
            super().__init__()
            self.audits: list[dict] = []

        def submit_audit(self, payload: dict) -> dict:
            self.audits.append(payload)
            return {"ok": True}

    peer = Recorder()
    play(Opponent(turn(1), turn(2)), threshold=2, transport=peer)
    assert len(peer.audits) == 1
    assert verify_audit(peer.audits[0]) is True


def test_a_technical_loss_still_sends_its_audit() -> None:
    """Withholding the reveal would make the loss uncheckable, which helps nobody."""
    result = play(Opponent(), threshold=3)
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert result.audit is not None
    assert result.audit["result_claim"] == "timeout"


def test_an_opponent_that_has_left_does_not_break_the_reveal() -> None:
    class Gone(Sink):
        def submit_audit(self, payload: dict) -> dict:
            raise ConnectionError("peer already exited")

    result = play(Opponent(turn(1), turn(2)), threshold=2, transport=Gone())
    assert result.audit is not None and verify_audit(result.audit) is True


@pytest.mark.parametrize("bad", [0, -1, True, "35", None])
def test_an_invalid_threshold_is_refused(bad: object) -> None:
    with pytest.raises(TurnLoopError, match="survival_threshold"):
        play(Opponent(turn(1)), threshold=bad)
