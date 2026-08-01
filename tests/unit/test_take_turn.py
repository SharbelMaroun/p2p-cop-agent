"""M5-17: ``take_turn`` -- the mailbox side of the autonomous play loop.

``drain`` validates everything and returns verdicts; the play loop needs the
opposite shape -- the next *turn message* the peer accepted, so it can be fed to
``run_turn``. The three behaviours pinned here are the ones that would each
silently break an unattended match:

* a rejected turn must be **consumed**, or the poller re-rejects it forever and
  starves the real turn behind it;
* a second queued turn must be **left in place**, or a hostile (or merely eager)
  peer sending two at once costs us the next step;
* the other mailboxes must be drained, or a negotiate/audit/control message
  parked in front of a turn stalls the game.
"""

import json
from pathlib import Path

from p2p_cop_agent import CopSDK
from p2p_cop_agent.adapters import PeerInboxes, take_turn
from p2p_cop_agent.peer import InboundPeer
from p2p_cop_agent.protocol import TurnLedger

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = ROOT / "config" / "rate_limits.json"
CONTROL_VALID = ROOT / "shared_contract" / "fixtures" / "control_message.valid.json"


def _peer() -> InboundPeer:
    return InboundPeer(CopSDK.from_repository(ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS))


def turn_msg(step: int = 1) -> dict:
    return {"step": step, "sender": "thief", "hint": "x", "smell_grid": {"0,0": 0.9},
            "commit": "a" * 64, "timestamp": "t"}


def audit_msg() -> dict:
    ledger = TurnLedger("thief")
    ledger.seal_turn(1, {"step": 1, "move": "N"},
                     {"hint": "x", "smell_grid": {"0,0": 0.1}, "timestamp": "t"})
    return ledger.audit_payload("capture")


def test_an_empty_mailbox_yields_nothing_rather_than_blocking() -> None:
    """The waiting belongs to the poller; this source must always answer at once."""
    assert take_turn(PeerInboxes(), _peer()) is None


def test_a_queued_turn_is_validated_and_returned() -> None:
    inboxes = PeerInboxes()
    inboxes.turns.put(turn_msg(1))
    assert take_turn(inboxes, _peer()) == turn_msg(1)


def test_a_rejected_turn_is_consumed_so_it_cannot_be_re_rejected_forever() -> None:
    """Leaving it queued would starve every real turn behind it."""
    inboxes = PeerInboxes()
    inboxes.turns.put({"step": 1, "sender": "thief"})  # missing mandated members
    assert take_turn(inboxes, _peer()) is None
    assert inboxes.turns.empty()


def test_a_rejected_turn_is_skipped_and_the_next_good_one_is_returned() -> None:
    inboxes = PeerInboxes()
    inboxes.turns.put({"nonsense": True})
    inboxes.turns.put(turn_msg(1))
    assert take_turn(inboxes, _peer()) == turn_msg(1)


def test_a_second_queued_turn_is_left_for_the_next_step() -> None:
    """Draining both would discard the next step instead of playing it."""
    peer = _peer()
    inboxes = PeerInboxes()
    inboxes.turns.put(turn_msg(1))
    inboxes.turns.put(turn_msg(2))
    assert take_turn(inboxes, peer) == turn_msg(1)
    assert inboxes.turns.qsize() == 1
    assert take_turn(inboxes, peer) == turn_msg(2)


def test_the_other_mailboxes_are_drained_so_nothing_parks_in_front_of_a_turn() -> None:
    inboxes = PeerInboxes()
    inboxes.controls.put(json.loads(CONTROL_VALID.read_text(encoding="utf-8")))
    inboxes.audits.put(audit_msg())
    inboxes.turns.put(turn_msg(1))
    assert take_turn(inboxes, _peer()) == turn_msg(1)
    assert inboxes.controls.empty()
    assert inboxes.audits.empty()


def test_only_a_turn_is_returned_even_when_other_mail_is_waiting() -> None:
    """Only a turn advances the loop; the rest are validated and recorded, not played."""
    inboxes = PeerInboxes()
    inboxes.controls.put(json.loads(CONTROL_VALID.read_text(encoding="utf-8")))
    assert take_turn(inboxes, _peer()) is None
