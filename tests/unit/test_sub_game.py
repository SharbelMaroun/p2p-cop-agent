"""M5-10d/M5-10e: a whole sub-game decided by claims, then proven by the audit.

Nothing here referees. Each test drives the peer with an opponent script and asserts
it reaches the outcome the *opponent's answers* imply — which is the only thing a
peer that cannot see the board is entitled to conclude.
"""


from p2p_cop_agent.domain.scoring import Outcome
from p2p_cop_agent.orchestration.phases import PhaseMachine
from p2p_cop_agent.orchestration.sub_game import run_sub_game_over_wire
from p2p_cop_agent.protocol.commit_reveal import TurnLedger
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
