"""M5-09/M5-10: the book's stage-2 milestone, over a real socket.

Book p. 105 asks that a message sent by peer A on localhost be **received
correctly** by peer B. Every other transport test in this repository runs both
halves inside one interpreter, which proves the call shapes but cannot prove
process separation (`AE-1`, `AE-2`) or that anything ever crossed a socket.

This test starts a genuinely separate OS process, sends to it over HTTP, and
reads the transcript that process wrote. The gate was skipped when M4 was built
before M5, and the book warns against exactly that ordering. The negotiate round
trip lives in `test_localhost_negotiation.py`; the harness is in `conftest.py`.
"""

from __future__ import annotations

import os

import pytest

from p2p_cop_agent.adapters import FastMCPClient, TransportError
from tests.integration.conftest import free_port, transcript_entries

TURN = {"step": 1, "sender": "thief", "hint": "near the bridge",
        "smell_grid": {"3,3": 0.9}, "commit": "a" * 64, "timestamp": "t"}


def test_a_turn_crosses_a_real_socket_into_a_separate_process(remote_peer) -> None:
    """The stage-2 milestone: A sends on localhost, B receives it correctly."""
    client, transcript, peer_pid = remote_peer

    assert client.receive_turn(TURN) == {"ok": True}

    accepted = [e for e in transcript_entries(transcript) if e["tool"] == "receive_turn"]
    assert accepted and accepted[0]["accepted"] is True

    # Validated by an interpreter that is not this one -- the point of AE-1/AE-2.
    # The handling PID is not asserted equal to the spawned PID: the HTTP server
    # serves requests from a worker process, so it is a descendant rather than
    # the child we started. "Not us" is the property that matters.
    assert peer_pid != os.getpid()
    assert accepted[0]["pid"] != os.getpid()


def test_the_remote_peer_rejects_a_malformed_turn_without_dropping_the_call(
    remote_peer,
) -> None:
    """Across a socket the ack still separates delivery from content (`ADR-002`)."""
    client, transcript, _ = remote_peer

    assert client.receive_turn({"bad": "turn"}) == {"ok": True}

    rejected = [e for e in transcript_entries(transcript) if e["tool"] == "receive_turn"]
    assert rejected and rejected[0]["accepted"] is False
    assert rejected[0]["reason"]


def test_an_unstarted_port_is_a_transport_error_not_a_hang() -> None:
    """A peer that was never started must fail fast, never wait forever."""
    client = FastMCPClient(f"http://127.0.0.1:{free_port()}/mcp", timeout=10.0)
    with pytest.raises(TransportError):
        client.receive_turn(TURN)
