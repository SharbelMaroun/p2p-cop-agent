"""Tests for the transport-neutral Option-B message surface (M4-01)."""

from pathlib import Path

import pytest

from p2p_cop_agent.protocol import (
    MESSAGE_SCHEMAS,
    OK_RESPONSE,
    ProtocolError,
    is_ok_response,
    require_wire_role,
    validate_message,
)
from p2p_cop_agent.shared.config import load_json_object

FIXTURES = Path(__file__).resolve().parents[2] / "shared_contract" / "fixtures"

# Logical message name -> fixture file stem.
CASES = {
    "negotiate": "negotiate",
    "turn": "turn_message",
    "audit": "audit_payload",
    "audit_record": "audit_record",
    "control": "control_message",
    "tool_response": "tool_response",
}


@pytest.mark.parametrize(("name", "stem"), CASES.items())
def test_valid_fixture_passes(name: str, stem: str) -> None:
    validate_message(name, load_json_object(FIXTURES / f"{stem}.valid.json"))


@pytest.mark.parametrize(("name", "stem"), CASES.items())
def test_invalid_fixture_raises_protocol_error(name: str, stem: str) -> None:
    with pytest.raises(ProtocolError):
        validate_message(name, load_json_object(FIXTURES / f"{stem}.invalid.json"))


def test_every_logical_name_maps_to_a_schema() -> None:
    assert set(CASES) <= set(MESSAGE_SCHEMAS)


def test_unknown_message_type_is_rejected() -> None:
    with pytest.raises(ProtocolError, match="unknown message type"):
        validate_message("does-not-exist", {})


def test_turn_message_with_clear_position_is_rejected() -> None:
    leaky = load_json_object(FIXTURES / "turn_message.valid.json")
    leaky["position"] = [4, 4]
    with pytest.raises(ProtocolError):
        validate_message("turn", leaky)


@pytest.mark.parametrize("role", ["police", "thief"])
def test_require_wire_role_accepts_wire_roles(role: str) -> None:
    assert require_wire_role(role) == role


@pytest.mark.parametrize("bad", ["cop", "COP", "", None, "robber"])
def test_require_wire_role_rejects_non_wire_roles(bad: object) -> None:
    with pytest.raises(ProtocolError, match="wire role"):
        require_wire_role(bad)


def test_ok_response_helper() -> None:
    assert is_ok_response(OK_RESPONSE) is True
    assert is_ok_response({"ok": True, "extra": 1}) is True
    assert is_ok_response({"ok": False}) is False
    assert is_ok_response({}) is False
    assert is_ok_response("ok") is False
