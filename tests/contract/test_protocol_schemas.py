"""Validate simulator-v3.0.0 compatibility fixtures against their schemas."""

from pathlib import Path

import pytest

from p2p_cop_agent.shared.config import load_json_object
from p2p_cop_agent.shared.contracts import ContractValidationError, validate_instance

BUNDLE = Path(__file__).resolve().parents[2] / "shared_contract"
SCHEMAS = BUNDLE / "schemas"
FIXTURES = BUNDLE / "fixtures"

# (schema file stem, fixture file stem)
CASES = [
    ("negotiate", "negotiate"),
    ("turn-message", "turn_message"),
    ("audit-record", "audit_record"),
    ("audit-payload", "audit_payload"),
    ("control-message", "control_message"),
    ("tool-response", "tool_response"),
    ("per-subgame-config", "per_subgame_config"),
]


def _schema(name: str) -> dict:
    return load_json_object(SCHEMAS / f"{name}.schema.json")


@pytest.mark.parametrize(("schema_name", "fixture_name"), CASES)
def test_valid_fixture_passes_schema(schema_name: str, fixture_name: str) -> None:
    schema = _schema(schema_name)
    instance = load_json_object(FIXTURES / f"{fixture_name}.valid.json")
    validate_instance(instance, schema, schema_name)


@pytest.mark.parametrize(("schema_name", "fixture_name"), CASES)
def test_invalid_fixture_fails_schema(schema_name: str, fixture_name: str) -> None:
    schema = _schema(schema_name)
    instance = load_json_object(FIXTURES / f"{fixture_name}.invalid.json")
    with pytest.raises(ContractValidationError):
        validate_instance(instance, schema, schema_name)


def test_every_message_schema_is_role_neutral_and_versioned() -> None:
    for schema_name, _ in CASES:
        schema = _schema(schema_name)
        assert schema["x-contract-version"] == "0.2.8-proposed"
        assert schema["x-role-neutral"] is True


def test_corrected_wire_schemas_identify_the_compatibility_profile() -> None:
    for schema_name in ("negotiate", "turn-message", "audit-payload"):
        assert _schema(schema_name)["x-compatibility-profile"] == "simulator-v3.0.0"


@pytest.mark.parametrize(
    ("forbidden_field", "value"),
    [
        ("position", [1, 1]),
        ("move", "N"),
        ("nonce", "0" * 32),
        ("intent", "pursue"),
        ("verdict", "truth"),
    ],
)
def test_turn_message_forbids_each_private_commitment_field(
    forbidden_field: str,
    value: object,
) -> None:
    schema = _schema("turn-message")
    leaky = load_json_object(FIXTURES / "turn_message.valid.json")
    leaky[forbidden_field] = value
    with pytest.raises(ContractValidationError):
        validate_instance(leaky, schema, "turn-message")


def test_nonce_schemas_distinguish_public_challenge_from_commitment_nonce() -> None:
    challenge = _schema("negotiate")["properties"]["nonce"]
    audit_record = _schema("audit-record")["properties"]["nonce"]
    audit_payload = _schema("audit-payload")["properties"]["records"]["items"]
    embedded_audit_nonce = audit_payload["properties"]["nonce"]

    assert challenge["x-purpose"] == "negotiation-challenge"
    assert challenge["x-visibility"] == "public"
    for nonce_schema in (audit_record, embedded_audit_nonce):
        assert nonce_schema["x-purpose"] == "per-turn-commitment-nonce"
        assert nonce_schema["x-visibility"] == "audit-only"
