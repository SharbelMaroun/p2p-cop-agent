"""M5-17: a whole sub-game played from the mailbox, with nothing fed in by hand.

Every earlier sub-game test hands ``run_sub_game_over_wire`` a scripted
``receive``. That proves the loop, but it quietly assumes the one piece that did
not exist: something to turn the passive mailbox into a turn source. Until this
existed a peer could not play unattended -- which is exactly why `M5-07c` (the
two-machine game) was blocked on code and not only on hardware.

Here the opponent is reachable only through the real parts: the peer sends via
the transport, the opponent's reply lands in this peer's own ``PeerInboxes``, and
the polling receiver has to find it there. Mailbox -> poller -> ``run_turn`` ->
transport -> mailbox, closed.
"""

from pathlib import Path

from p2p_cop_agent import CopSDK
from p2p_cop_agent.adapters import PeerInboxes, take_turn
from p2p_cop_agent.domain.scoring import Outcome
from p2p_cop_agent.orchestration.phases import PhaseMachine
from p2p_cop_agent.orchestration.polling import turn_receiver
from p2p_cop_agent.orchestration.sub_game import run_sub_game_over_wire
from p2p_cop_agent.peer import InboundPeer
from p2p_cop_agent.protocol.commit_reveal import TurnLedger, verify_audit
from tests.unit.test_polling import FakeClock
from tests.unit.test_turn_loop import CHALLENGE, decide

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = ROOT / "config" / "rate_limits.json"


def _peer() -> InboundPeer:
    return InboundPeer(CopSDK.from_repository(ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS))


def reply(step: int, **extra: object) -> dict:
    return {"step": step, "sender": "thief", "hint": "somewhere",
            "smell_grid": {"3,3": 0.9}, "commit": "a" * 64,
            "timestamp": f"t{step}", **extra}


class MailboxOpponent:
    """An opponent that answers into *our* inboxes, the way a real peer would.

    It is a ``PeerTransport``: we call ``receive_turn`` to send, and its answer
    arrives asynchronously in the mailbox rather than as a return value -- which
    is the whole shape of the wire profile, where the tool only acknowledges.

    Its opening turn is seeded into the mailbox before play starts, because the
    book gives the Thief the first move: by the time a Cop looks, the Thief's
    step-1 message is already sitting there.
    """

    def __init__(self, inboxes: PeerInboxes, *replies: dict) -> None:
        self.inboxes = inboxes
        self.replies = list(replies)
        self.sent: list[dict] = []
        self.audits: list[dict] = []
        if self.replies:
            self.inboxes.turns.put(self.replies.pop(0))

    def receive_turn(self, message: dict) -> dict:
        self.sent.append(message)
        if self.replies:
            self.inboxes.turns.put(self.replies.pop(0))
        return {"ok": True}

    def submit_audit(self, payload: dict) -> dict:
        self.audits.append(payload)
        return {"ok": True}


def play(*replies: dict, threshold: int = 5, opens: bool = False, timeout: float = 30.0):
    """Play a sub-game whose only turn source is the mailbox.

    ``opens`` is ``False`` because this is the Cop: the book gives the first move
    of every cycle to the Thief, so a Cop's every turn -- including step 1 --
    begins by waiting. That makes the mailbox load-bearing from the very first
    step rather than from the second.
    """
    inboxes = PeerInboxes()
    peer = _peer()
    opponent = MailboxOpponent(inboxes, *replies)
    clock = FakeClock()
    result = run_sub_game_over_wire(
        machine=PhaseMachine(),
        ledger=TurnLedger("police", public_challenge=CHALLENGE),
        transport=opponent,
        receive=turn_receiver(
            lambda: take_turn(inboxes, peer),
            clock=clock.time,
            sleep=clock.sleep,
            timeout=timeout,
            poll_interval=0.5,
        ),
        decide=decide,
        survival_threshold=threshold,
        opens=opens,
    )
    return result, opponent, clock


def test_a_whole_sub_game_plays_with_no_message_fed_in_by_hand() -> None:
    """The gap `M5-07c` named: a peer that drives itself, not one driven by a test."""
    result, opponent, _ = play(
        reply(1),
        reply(2, claim_response={"claim": [3, 3], "caught": True}),
    )
    assert result.outcome is Outcome.CAPTURE
    assert result.steps == 2
    assert len(opponent.sent) == 2


def test_the_opponent_reply_really_travels_through_the_mailbox() -> None:
    """If the poller were bypassed the peer would stall on step 2, not answer it."""
    result, opponent, _ = play(reply(1), reply(2, win_claim={"type": "survival"}))
    assert result.outcome is Outcome.SURVIVAL
    assert [m["step"] for m in opponent.sent] == [1, 2]


def test_the_audit_still_closes_the_sub_game_and_verifies() -> None:
    result, opponent, _ = play(
        reply(1, claim_response={"claim": [3, 3], "caught": True}),
    )
    assert result.audit is not None
    assert opponent.audits == [result.audit]
    assert verify_audit(result.audit) is True


def test_a_silent_opponent_ends_the_game_instead_of_hanging_the_poller() -> None:
    """Rule 6, end to end: the wait is bounded, so silence decides rather than blocks."""
    result, _, clock = play(threshold=5, timeout=2.0)
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert clock.now >= 2.0  # it really waited its budget before giving up


def test_a_peer_that_stops_answering_midway_takes_the_technical_loss() -> None:
    """One turn is played, then the opponent goes quiet and step 2 never arrives."""
    result, opponent, _ = play(reply(1), threshold=5, timeout=1.0)
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert len(opponent.sent) == 1  # our step 1 went out; nothing came back after it
    assert result.audit is not None  # the audit goes out even when we are losing
