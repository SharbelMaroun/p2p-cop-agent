"""Validate every Option-B protocol fixture against its schema."""

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
        assert schema["x-contract-version"] == "0.2.1-proposed"
        assert schema["x-role-neutral"] is True


def test_turn_message_forbids_clear_position_and_nonce() -> None:
    """The negative TurnMessage fixture carries clear position/nonce and must fail."""
    schema = _schema("turn-message")
    leaky = load_json_object(FIXTURES / "turn_message.invalid.json")
    assert "position" in leaky and "nonce" in leaky
    with pytest.raises(ContractValidationError):
        validate_instance(leaky, schema, "turn-message")
