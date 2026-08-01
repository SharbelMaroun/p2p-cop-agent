"""M5-15: prove a hostile or broken opponent cannot hang or corrupt this peer.

Each individual guard is unit-tested where it lives -- the phase machine in
`test_phases`, replay and conflict in `test_turn_inbox`, tamper in
`test_audit_reveal`, and silence in `test_turn_loop_faults` and `test_sub_game`.
This is the milestone-level proof, and it asserts the two properties those
piecemeal tests do not:

* **cannot corrupt** -- a rejected adversarial message leaves the peer's prior,
  audit-bearing state exactly as it was, and the next honest turn still admits. A
  guard that rejects but half-applies would hand the end-game audit a record the
  opponent never sent, which is an automatic zero for both sides.
* **cannot hang** -- sustained silence, where no phase transition feeds the
  heartbeat, trips the watchdog into a terminal controlled shutdown, composing the
  bounded waiting of M5-05 with the liveness watchdog of M5-06.

Reusing the real `InboundPeer` fixtures from `test_peer_inbound` keeps this a proof
of the shipped entry point, not of a stand-in.
"""

import pytest

from p2p_cop_agent.orchestration.phases import Phase, PhaseMachine
from p2p_cop_agent.orchestration.shutdown import (
    controlled_shutdown,
    heartbeat_on_transition,
)
from p2p_cop_agent.protocol import ProtocolError
from p2p_cop_agent.services.watchdog import Watchdog
from tests.unit.test_peer_inbound import peer, turn_msg

# --- cannot corrupt: a rejected message must not disturb accepted state ---------


def test_a_conflicting_turn_leaves_the_accepted_commit_on_record() -> None:
    """M5-15c: same step, a different commit is refused -- and the first commit is
    still the one the audit will have to reproduce, proved by re-accepting it
    idempotently (a corrupted record would raise a conflict instead)."""
    p = peer()
    assert p.receive_turn(turn_msg(step=2, digest="a" * 64)) == {"ok": True}
    with pytest.raises(ProtocolError):
        p.receive_turn(turn_msg(step=2, digest="b" * 64))
    assert p.receive_turn(turn_msg(step=2, digest="a" * 64)) == {"ok": True}  # idempotent
    assert p.receive_turn(turn_msg(step=3)) == {"ok": True}  # still advances


def test_a_replayed_turn_is_rejected_yet_the_next_real_step_admits() -> None:
    """M5-15c: an out-of-order step that does not advance is refused without
    rewinding the sender's progress, so honest play continues past it."""
    p = peer()
    p.receive_turn(turn_msg(step=2))
    with pytest.raises(ProtocolError):
        p.receive_turn(turn_msg(step=1))  # does not advance past step 2
    assert p.receive_turn(turn_msg(step=3)) == {"ok": True}


def test_a_malformed_turn_changes_no_state_before_it_is_refused() -> None:
    """M5-15d: schema validation runs before any domain state changes, so a
    malformed message leaves the step it pretended to be still open."""
    p = peer()
    with pytest.raises(ProtocolError):
        p.receive_turn({"step": 1, "sender": "thief"})  # missing required fields
    assert p.receive_turn(turn_msg(step=1)) == {"ok": True}


def test_an_unknown_tool_is_refused_without_side_effects() -> None:
    """M5-15d: a call for a tool outside the Option-B profile is rejected at
    dispatch and cannot reach or disturb any handler."""
    p = peer()
    with pytest.raises(ProtocolError, match="unknown tool"):
        p.dispatch("receive_move", {})
    assert p.receive_turn(turn_msg(step=1)) == {"ok": True}


# --- cannot hang: silence must decide, not wait ---------------------------------


def test_sustained_silence_trips_the_watchdog_into_a_terminal_shutdown() -> None:
    """M5-15a: with no transition to feed the heartbeat, the watchdog trips at the
    agreed timeout and the controlled shutdown routes the machine to its one
    terminal state -- the deadline-plus-watchdog outcome the milestone requires."""
    machine = PhaseMachine()  # owed the opponent's turn, making no progress
    watchdog = Watchdog.started_at(now=0.0, timeout_sec=60.0)
    assert watchdog.check(60.0) is True  # a full timeout of silence
    persisted: list[str] = []
    report = controlled_shutdown(
        machine, persist_state=lambda: persisted.append("state"), reason="watchdog silence"
    )
    assert persisted == ["state"]
    assert machine.current is Phase.TECHNICAL_LOSS
    assert report.phase is Phase.TECHNICAL_LOSS


def test_a_peer_that_keeps_moving_never_trips_the_watchdog() -> None:
    """The contrast that makes the trip meaningful: transitions arriving inside the
    timeout keep feeding the heartbeat, so a healthy match never trips."""
    ticks = iter([10.0, 20.0, 30.0, 40.0, 50.0])
    watchdog = Watchdog.started_at(now=0.0, timeout_sec=60.0)
    beat = heartbeat_on_transition(watchdog, clock=lambda: next(ticks))
    for _ in range(5):
        beat(Phase.COMPUTING_MOVE)
    assert watchdog.tripped is False
    assert watchdog.expired(90.0) is False  # last beat 50.0, only 40s of silence
