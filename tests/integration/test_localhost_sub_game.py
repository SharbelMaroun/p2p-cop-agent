"""M5-10d/M5-10e: a whole sub-game and its audit, across a real socket.

The unit tests drive the sub-game against a fake transport, which proves the
decision logic. This proves the same run survives an actual carrier: every turn and
the final audit are sent over HTTP into a **separate operating-system process**,
which validates each one and writes down what it saw.

The opponent's replies still come from a local script — a second peer that plays
back is `M7` work — so what is demonstrated here is this peer completing a bounded
sub-game and delivering a reproducible audit to a real remote, not two agents
playing each other.
"""

from __future__ import annotations

from p2p_cop_agent.domain.scoring import Outcome
from p2p_cop_agent.orchestration.phases import PhaseMachine
from p2p_cop_agent.orchestration.sub_game import run_sub_game_over_wire
from p2p_cop_agent.protocol.commit_reveal import TurnLedger, verify_audit
from tests.integration.conftest import transcript_entries

CHALLENGE = "0123456789abcdef0123456789abcdef"


def decide(_incoming: dict | None) -> tuple[dict, dict]:
    return (
        {"move": "MOVE:N", "intent": "truth"},
        {"hint": "circling the block", "smell_grid": {"0,0": 0.9}, "timestamp": "t"},
    )


def opponent_turn(step: int, **extra: object) -> dict:
    return {"step": step, "sender": "thief", "hint": "still running",
            "smell_grid": {"3,3": 0.9}, "commit": "b" * 64,
            "timestamp": f"t{step}", **extra}


def scripted(*messages: dict):
    queue = list(messages)
    return lambda: queue.pop(0) if queue else None


def play(client, receive, threshold: int):
    return run_sub_game_over_wire(
        machine=PhaseMachine(),
        ledger=TurnLedger("police", public_challenge=CHALLENGE),
        transport=client,
        receive=receive,
        decide=decide,
        survival_threshold=threshold,
    )


def test_a_full_sub_game_and_its_audit_cross_a_real_socket(remote_peer) -> None:
    """Every turn and the audit are validated by an interpreter that is not this one."""
    client, transcript, _ = remote_peer

    result = play(client, scripted(*(opponent_turn(s) for s in range(1, 4))), 3)

    assert result.outcome is Outcome.SURVIVAL
    assert result.steps == 3

    entries = transcript_entries(transcript)
    turns = [e for e in entries if e["tool"] == "receive_turn"]
    audits = [e for e in entries if e["tool"] == "submit_audit"]

    assert len(turns) == 3 and all(e["accepted"] for e in turns)
    assert len(audits) == 1 and audits[0]["accepted"] is True


def test_the_delivered_audit_reproduces_every_commitment(remote_peer) -> None:
    """`[AE-19]`: the remote peer accepted it, and it recomputes here too."""
    client, transcript, _ = remote_peer

    result = play(client, scripted(*(opponent_turn(s) for s in range(1, 3))), 2)

    assert verify_audit(result.audit) is True
    assert len(result.audit["records"]) == 2
    assert [e["accepted"] for e in transcript_entries(transcript)
            if e["tool"] == "submit_audit"] == [True]


def test_a_confirmed_capture_ends_the_run_early_over_the_wire(remote_peer) -> None:
    client, transcript, _ = remote_peer

    result = play(client, scripted(
        opponent_turn(1),
        opponent_turn(2, claim_response={"claim": [3, 3], "caught": True}),
        opponent_turn(3),
    ), 10)

    assert result.outcome is Outcome.CAPTURE
    assert result.steps == 2
    assert result.audit["result_claim"] == "capture"

    turns = [e for e in transcript_entries(transcript) if e["tool"] == "receive_turn"]
    assert len(turns) == 2, "the run must stop sending once the game is decided"


def test_a_tampered_audit_is_rejected_by_the_remote_peer(remote_peer) -> None:
    """If this were accepted, the audit would be proving nothing at all."""
    client, transcript, _ = remote_peer

    result = play(client, scripted(opponent_turn(1)), 1)
    forged = {**result.audit}
    forged["records"] = [{**r, "payload": {**r["payload"], "move": "MOVE:S"}}
                         for r in result.audit["records"]]
    client.submit_audit(forged)

    audits = [e for e in transcript_entries(transcript) if e["tool"] == "submit_audit"]
    assert [e["accepted"] for e in audits] == [True, False]
    assert audits[1]["reason"]
