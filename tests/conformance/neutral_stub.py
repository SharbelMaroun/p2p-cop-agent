"""A neutral reference peer for simulator-v3.0.0 compatibility testing.

This stub deliberately imports no Cop runtime code (`p2p_cop_agent`). It relies
only on the standard library and jsonschema, and it re-implements the
canonicalization and commit rules independently so it can prove cross-
implementation reproducibility of the shared vectors. It exposes exactly the
simulator-v3.0.0 compatibility tools with their exact argument names.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema.validators import validator_for

BUNDLE = Path(__file__).resolve().parents[2] / "shared_contract"
SCHEMAS = BUNDLE / "schemas"

# Exact exposed tool name -> exact single argument name.
TOOLS = {
    "negotiate": "message",
    "receive_turn": "message",
    "submit_audit": "payload",
    "receive_control": "message",
}
OK = {"ok": True}


class ConformanceError(ValueError):
    """Raised when an inbound message violates the compatibility profile."""


def canonical(payload: object) -> bytes:
    """Independent canonicalization matching the shared profile."""
    text = json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    )
    return text.encode("utf-8")


def commit(payload: object, commitment_nonce: str) -> str:
    """Return an independent per-turn commitment hash."""
    suffix = b"|" + commitment_nonce.encode("ascii")
    return hashlib.sha256(canonical(payload) + suffix).hexdigest()


class NeutralPeer:
    """A minimal role-neutral peer that validates and applies inbound messages."""

    def __init__(self, role: str, group_id: str) -> None:
        self.role = role
        self.group_id = group_id
        self._schemas = {p.name.removesuffix(".schema.json"): _load(p) for p in SCHEMAS.glob("*.schema.json")}
        self._turns: dict[tuple[str, int], str] = {}
        self._last_step: dict[str, int] = {}
        self.opponent_group: str | None = None

    def _validate(self, instance: object, schema_name: str) -> None:
        schema = self._schemas[schema_name]
        validator = validator_for(schema)(schema)
        errors = sorted(validator.iter_errors(instance), key=lambda item: item.json_path)
        if errors:
            raise ConformanceError(f"{schema_name}: {errors[0].message}")

    def negotiate(self, message: dict) -> dict:
        """Accept or reject a per-match negotiation offer."""
        self._validate(message, "negotiate")
        self.opponent_group = message["identity"]["group_id"]
        return dict(OK)

    def receive_turn(self, message: dict) -> dict:
        """Accept a public turn, deduplicating and rejecting illegal transitions."""
        self._validate(message, "turn-message")
        sender, step, digest = message["sender"], message["step"], message["commit"]
        key = (sender, step)
        if key in self._turns:
            if self._turns[key] == digest:
                return dict(OK)
            raise ConformanceError("protocol conflict: same sender/step, different commit")
        last = self._last_step.get(sender)
        if last is not None and step <= last:
            raise ConformanceError("illegal transition: step did not advance")
        self._turns[key] = digest
        self._last_step[sender] = step
        return dict(OK)

    def submit_audit(self, payload: dict) -> dict:
        """Accept an audit only if every record reproduces its commitment."""
        self._validate(payload, "audit-payload")
        for record in payload["records"]:
            if commit(record["payload"], record["nonce"]) != record["commit"]:
                raise ConformanceError("audit record commit does not reproduce")
        return dict(OK)

    def receive_control(self, message: dict) -> dict:
        """Accept an optional control message."""
        self._validate(message, "control-message")
        return dict(OK)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
