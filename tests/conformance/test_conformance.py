"""Unknown-opponent conformance against the neutral stub."""

import json
from pathlib import Path

import pytest

from tests.conformance.neutral_stub import TOOLS, ConformanceError, NeutralPeer, commit

BUNDLE = Path(__file__).resolve().parents[2] / "shared_contract"
VECTORS = BUNDLE / "vectors" / "move-commit.vectors.json"
PUBLIC_NEGOTIATION_CHALLENGE = "0123456789abcdef0123456789abcdef"
COMMITMENT_NONCE = "abcdefabcdefabcdefabcdefabcdefab"


def police() -> NeutralPeer:
    return NeutralPeer("police", "group-alpha")


def offer(group_id: str, role: str = "police") -> dict:
    return {
        "terms": {"grid_size": 7},
        "nonce": PUBLIC_NEGOTIATION_CHALLENGE,
        "signature": "sig",
        "identity": {"role": role, "group_id": group_id},
    }


def test_exact_tool_names_and_argument_names() -> None:
    assert TOOLS == {
        "negotiate": "message",
        "receive_turn": "message",
        "submit_audit": "payload",
        "receive_control": "message",
    }


def test_police_can_offer_and_accept_negotiation() -> None:
    peer = police()
    assert peer.negotiate(offer("group-beta", "thief")) == {"ok": True}
    assert peer.opponent_group == "group-beta"


def test_two_participant_pairs_do_not_change_controlled_bytes() -> None:
    before = (BUNDLE / "PARITY_MANIFEST.json").read_bytes()
    assert NeutralPeer("police", "team-a").negotiate(offer("team-b", "thief")) == {"ok": True}
    assert NeutralPeer("thief", "team-c").negotiate(offer("team-d", "police")) == {"ok": True}
    assert (BUNDLE / "PARITY_MANIFEST.json").read_bytes() == before


def test_neutral_stub_reproduces_move_commit_vectors() -> None:
    vectors = json.loads(VECTORS.read_text(encoding="utf-8"))["vectors"]
    for vector in vectors:
        assert commit(vector["payload"], vector["nonce"]) == vector["commit"]


@pytest.mark.parametrize(
    ("forbidden_field", "value"),
    [("position", [1, 1]), ("nonce", COMMITMENT_NONCE)],
)
def test_turn_message_rejects_each_private_commitment_field(
    forbidden_field: str,
    value: object,
) -> None:
    leaky = {
        "step": 1,
        "sender": "police",
        "hint": "x",
        "smell_grid": [[0.0]],
        "commit": "a" * 64,
        "timestamp": "t",
        forbidden_field: value,
    }
    with pytest.raises(ConformanceError):
        police().receive_turn(leaky)


def good_turn(step: int = 1, sender: str = "police", digest: str = "a" * 64) -> dict:
    return {
        "step": step,
        "sender": sender,
        "hint": "x",
        "smell_grid": [[0.0]],
        "commit": digest,
        "timestamp": "t",
    }


def test_duplicate_same_commit_is_acknowledged_once() -> None:
    peer = police()
    assert peer.receive_turn(good_turn(step=1)) == {"ok": True}
    assert peer.receive_turn(good_turn(step=1)) == {"ok": True}


def test_same_step_different_commit_is_a_conflict() -> None:
    peer = police()
    peer.receive_turn(good_turn(step=1, digest="a" * 64))
    with pytest.raises(ConformanceError, match="conflict"):
        peer.receive_turn(good_turn(step=1, digest="b" * 64))


def test_non_advancing_step_is_an_illegal_transition() -> None:
    peer = police()
    peer.receive_turn(good_turn(step=2))
    with pytest.raises(ConformanceError, match="illegal transition"):
        peer.receive_turn(good_turn(step=1))


@pytest.mark.parametrize(
    "message",
    [
        {**good_turn(), "sender": "cop"},
        {**good_turn(), "step": -1},
        {**good_turn(), "commit": "not-hex"},
    ],
)
def test_invalid_turn_fields_are_rejected(message: dict) -> None:
    with pytest.raises(ConformanceError):
        police().receive_turn(message)


def test_invalid_public_negotiation_challenge_is_rejected() -> None:
    bad = offer("group-beta", "thief")
    bad["nonce"] = "too-short"
    with pytest.raises(ConformanceError):
        police().negotiate(bad)


def test_audit_reproduction_is_checked() -> None:
    peer = police()
    payload = {"step": 1, "move": "N"}
    valid = {
        "sender": "police",
        "records": [
            {
                "payload": payload,
                "nonce": COMMITMENT_NONCE,
                "commit": commit(payload, COMMITMENT_NONCE),
            }
        ],
        "result_claim": {"outcome": "capture"},
    }
    assert peer.submit_audit(valid) == {"ok": True}
    valid["records"][0]["commit"] = "f" * 64
    with pytest.raises(ConformanceError, match="does not reproduce"):
        peer.submit_audit(valid)
