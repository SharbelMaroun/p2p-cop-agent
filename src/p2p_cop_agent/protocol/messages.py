"""Transport-neutral Option-B message validation.

Runtime counterpart to the test-only neutral stub: it loads the role-neutral
``shared_contract`` schemas and validates the Option-B messages, raising a stable
``ProtocolError`` on failure. It is transport-agnostic — the FastMCP adapters (M5)
call into this, and the commit-reveal state machine (later M4 tasks) builds on it.
Per ADR-002 the wire payload is exactly the schema-defined message: no envelope
member such as ``message_id``, ``sequence``, or ``idempotency_key`` is added.
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import cache
from pathlib import Path

from p2p_cop_agent.shared.config import JsonObject, load_json_object
from p2p_cop_agent.shared.contracts import ContractValidationError, validate_instance

_SCHEMA_DIR = Path(__file__).resolve().parents[3] / "shared_contract" / "schemas"

# Logical message name -> controlled schema filename.
MESSAGE_SCHEMAS = {
    "negotiate": "negotiate.schema.json",
    "turn": "turn-message.schema.json",
    "audit": "audit-payload.schema.json",
    "audit_record": "audit-record.schema.json",
    "control": "control-message.schema.json",
    "tool_response": "tool-response.schema.json",
}

WIRE_ROLES = ("police", "thief")
OK_RESPONSE: JsonObject = {"ok": True}


class ProtocolError(ValueError):
    """Raised when a message violates the Option-B message contract."""


@cache
def _schema(name: str) -> JsonObject:
    """Load and cache one controlled message schema by logical name."""
    try:
        filename = MESSAGE_SCHEMAS[name]
    except KeyError:
        raise ProtocolError(f"unknown message type {name!r}") from None
    return load_json_object(_SCHEMA_DIR / filename)


def validate_message(name: str, message: object) -> None:
    """Validate a message against its schema, raising ProtocolError on failure."""
    try:
        validate_instance(message, _schema(name), name)
    except ContractValidationError as exc:
        raise ProtocolError(str(exc)) from exc


def require_wire_role(value: object) -> str:
    """Return a validated wire role, rejecting the internal ``cop`` label."""
    if value not in WIRE_ROLES:
        raise ProtocolError(f"wire role must be one of {WIRE_ROLES}, got {value!r}")
    return value  # type: ignore[return-value]


def is_ok_response(response: object) -> bool:
    """Return whether a tool response is exactly *this* peer's ``{"ok": true}`` ack.

    Use it to assert what **we** send. For judging what an *opponent* sent back,
    use :func:`is_acknowledgement` -- demanding our own shape from a peer we did
    not write is the bug described there.
    """
    return isinstance(response, Mapping) and response.get("ok") is True


# ``status`` values by which an opponent signals it declined the message.
REFUSAL_WORDS = frozenset({"error", "failed", "failure", "rejected", "refused", "denied"})


def signals_refusal(response: object) -> bool:
    """Return whether a well-formed reply explicitly says the peer refused.

    Silence is not refusal: only an explicit ``ok: false``, a ``status`` naming a
    failure, or a non-empty ``error`` member counts.
    """
    if not isinstance(response, Mapping):
        return False
    if response.get("ok") is False:
        return True
    status = response.get("status")
    if isinstance(status, str) and status.strip().lower() in REFUSAL_WORDS:
        return True
    return response.get("error") not in (None, "")


def is_acknowledgement(response: object) -> bool:
    """Return whether an opponent's reply counts as a delivery acknowledgement.

    Liberal on shape, strict on refusal. This peer sends ``{"ok": true}``, but the
    profile never fixed what an opponent must send back and the reference is
    reported to answer ``{"status": "ok"}`` or ``{"status": "delivered"}``.
    Requiring our own dict would read every successful delivery from a
    simulator-built classmate as a failure and abandon a game that was going fine.

    This lives here, in the transport-neutral layer, so the outbound adapter and
    the commit-reveal ledger cannot drift apart on what counts as delivered --
    they judged it differently until 2026-07-31, and the ledger's stricter reading
    would have aborted every turn against such a peer.
    """
    return isinstance(response, Mapping) and not signals_refusal(response)
