"""Golden acceptance for the simulator-v3.0.0 compatibility profile.

Rejection cases for wrong wire shapes live in
``test_simulator_v3_rejections.py`` so each file stays within the test
file-length limit.
"""

from pathlib import Path

import pytest

from p2p_cop_agent.protocol import (
    canonical_payload_bytes,
    move_commit,
    validate_message,
    verify_audit,
)
from p2p_cop_agent.shared.config import load_json_object

BUNDLE = Path(__file__).resolve().parents[2] / "shared_contract"
WIRE_FIXTURE = BUNDLE / "fixtures" / "simulator-v3.0.0-wire.golden.json"
COMMIT_VECTORS = BUNDLE / "vectors" / "simulator-v3.0.0-commit.golden.json"


def wire_fixture() -> dict:
    """Load the labelled source-derived wire fixture."""
    return load_json_object(WIRE_FIXTURE)


def messages() -> dict:
    """Return the golden messages by fixture name."""
    return wire_fixture()["messages"]  # type: ignore[return-value]


def commit_vectors() -> dict:
    """Load the labelled source-derived commitment vectors."""
    return load_json_object(COMMIT_VECTORS)


def test_golden_data_is_explicitly_labelled() -> None:
    assert wire_fixture()["profile"] == "simulator-v3.0.0"
    assert commit_vectors()["profile"] == "simulator-v3.0.0"


@pytest.mark.parametrize(
    ("logical_name", "fixture_name"),
    [
        ("negotiate", "negotiation"),
        ("turn", "normal_turn"),
        ("turn", "capture_claim_turn"),
        ("turn", "claim_response_turn"),
        ("turn", "win_claim_turn"),
        ("audit", "audit_payload"),
    ],
)
def test_cop_accepts_source_derived_wire_objects(
    logical_name: str,
    fixture_name: str,
) -> None:
    validate_message(logical_name, messages()[fixture_name])


def test_negotiation_signature_reproduces_exactly_without_identity_role() -> None:
    message = messages()["negotiation"]
    assert "role" not in message["identity"]
    assert move_commit(message["terms"], message["nonce"]) == message["signature"]


def test_normal_turn_serializes_every_absent_optional_as_null() -> None:
    message = messages()["normal_turn"]
    optional = ("barrier_placed", "capture_claim", "claim_response", "win_claim")
    assert all(field in message and message[field] is None for field in optional)


def test_claim_turns_preserve_reference_coordinate_and_object_shapes() -> None:
    capture = messages()["capture_claim_turn"]
    response = messages()["claim_response_turn"]
    win = messages()["win_claim_turn"]
    assert capture["capture_claim"] == [1, 0]
    assert response["claim_response"] == {"claim": [1, 0], "caught": False}
    assert win["win_claim"] == {"type": "survival"}


def test_golden_turns_never_expose_private_commitment_fields() -> None:
    forbidden = {"position", "move", "intent", "verdict", "nonce"}
    for name in (
        "normal_turn",
        "capture_claim_turn",
        "claim_response_turn",
        "win_claim_turn",
    ):
        assert forbidden.isdisjoint(messages()[name])


def test_golden_audit_record_reproduces_and_verifies() -> None:
    payload = messages()["audit_payload"]
    record = payload["records"][0]
    assert move_commit(record["payload"], record["nonce"]) == record["commit"]
    assert verify_audit(payload) is True


def test_cop_reproduces_exact_source_derived_commitment_hashes() -> None:
    for vector in commit_vectors()["vectors"]:
        canonical = canonical_payload_bytes(vector["payload"])
        assert canonical.decode("utf-8") == vector["canonical_json"]
        assert move_commit(vector["payload"], vector["nonce"]) == vector["commit"]


def test_non_ascii_vector_requires_unescaped_utf8() -> None:
    vector = next(
        item
        for item in commit_vectors()["vectors"]
        if item.get("proves_ensure_ascii_false") is True
    )
    canonical = canonical_payload_bytes(vector["payload"])
    assert "שלום".encode() in canonical
    assert b"\\u05e9" not in canonical
    assert canonical.decode("utf-8") == vector["canonical_json"]
