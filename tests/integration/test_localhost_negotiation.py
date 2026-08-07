"""M5-10b: one negotiate round trip between two real OS processes.

The contract tests prove the negotiation *logic*; the neutral-stub tests prove
the *call shapes*. Neither shows two independent interpreters actually agreeing
to play, which is what Appendix E rule 11 is about: an offer signed in this
process, carried over HTTP, and judged by a peer that loaded the match object
from disk on its own.

The harness -- spawning and reaping the peer -- lives in `conftest.py`.
"""

from __future__ import annotations

from p2p_cop_agent.protocol import build_offer
from tests.integration.conftest import match_object, transcript_entries

# Complete per the book-mandated pre-game content `build_offer` now enforces on our
# side (M5-04h); neutral test values, not the real team's.
IDENTITY = {
    "group_id": "neutral-group-alpha", "group_name": "Alpha", "members": ["a", "b"],
    "repos": {"cop": "https://example.test/cop", "thief": "https://example.test/thief"},
    "mcp_servers": {"cop": "https://cop.example.test/mcp"}, "llm_model": "cli-default",
    "spec": {"os": "Example OS", "cpu_type": "Example CPU", "cpu_freq_mhz": 3600, "cpu_cores": 8, "ram_gb": 32, "gpu_model": "none", "vram_gb": 0},
}


def negotiations(transcript) -> list[dict]:
    return [e for e in transcript_entries(transcript) if e["tool"] == "negotiate"]


def test_a_matching_offer_is_agreed_across_the_socket(remote_peer) -> None:
    """A separate process reads our terms and decides it will play."""
    client, transcript, _ = remote_peer

    assert client.negotiate(build_offer(match_object(), IDENTITY)) == {"ok": True}

    agreed = negotiations(transcript)
    assert agreed and agreed[0]["accepted"] is True


def test_a_mismatched_offer_is_refused_across_the_socket_and_names_the_term(
    remote_peer,
) -> None:
    """Rule 11 over a real carrier: refuse to play, and say what disagreed.

    The offer is internally consistent -- correctly signed and Appendix-F legal --
    so only a peer that compares the terms against its **own** config catches it.
    A bare refusal would leave the opponent nothing to fix.
    """
    client, transcript, _ = remote_peer
    offer = build_offer(match_object(world={"hint_max_words": 20}), IDENTITY)

    assert client.negotiate(offer) == {"ok": True}

    refused = negotiations(transcript)
    assert refused and refused[0]["accepted"] is False
    assert "hint_max_words" in refused[0]["reason"]


def test_a_forged_signature_is_refused_across_the_socket(remote_peer) -> None:
    """Tampering with the terms after signing must not survive the crossing."""
    client, transcript, _ = remote_peer
    offer = build_offer(match_object(), IDENTITY)
    offer["terms"]["board_size"] = 9

    assert client.negotiate(offer) == {"ok": True}

    refused = negotiations(transcript)
    assert refused and refused[0]["accepted"] is False
    assert "signature" in refused[0]["reason"]
