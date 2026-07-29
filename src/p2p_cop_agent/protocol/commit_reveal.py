"""Transport-neutral commit-reveal ledger (M4-03).

One ``TurnLedger`` tracks one peer's sealed turns within one sub-game. Each turn
seals a private payload (semantic state, move, and intent) under a fresh secret
commitment nonce and emits only the public ``TurnMessage``. Payloads and nonces
stay private until the post-game audit, which reveals every record so the opponent
can reproduce each commit. The simulator-v3.0.0 compatibility profile has no live
reveal tool.

This module covers the happy-path round-trip and the fresh-nonce discipline.
Duplicate/replay/conflict depth is M4-04 and tamper/technical-loss is M4-05.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from p2p_cop_agent.protocol.commit import generate_commitment_nonce, move_commit, verify_commit
from p2p_cop_agent.protocol.messages import (
    ProtocolError,
    is_ok_response,
    require_wire_role,
    validate_message,
)
from p2p_cop_agent.shared.config import JsonObject

# Keys that must never appear in a public turn message.
_SECRET_KEYS = ("payload", "nonce", "position", "move", "intent", "verdict")


class CommitRevealError(ValueError):
    """Raised when the commit-reveal sequence or nonce discipline is violated."""


@dataclass(frozen=True, slots=True)
class SealedTurn:
    """One privately stored turn: the hidden payload, its nonce, and the commit."""

    step: int
    payload: JsonObject
    nonce: str
    commit: str


@dataclass
class TurnLedger:
    """A per-sub-game commit-reveal ledger for one peer.

    ``public_challenge`` is the peer's own ``negotiate.nonce`` when known; it is
    recorded only to prove a commitment nonce never equals or derives from it.
    """

    sender: str
    public_challenge: str | None = None
    _records: list[SealedTurn] = field(default_factory=list)
    _used_nonces: set[str] = field(default_factory=set)
    _last_step: int | None = field(default=None)

    def __post_init__(self) -> None:
        require_wire_role(self.sender)

    @property
    def records(self) -> tuple[SealedTurn, ...]:
        """Return the sealed turns in commit order."""
        return tuple(self._records)

    def seal_turn(
        self,
        step: object,
        payload: JsonObject,
        public: Mapping[str, object],
        *,
        nonce: str | None = None,
    ) -> JsonObject:
        """Seal a turn and return only its public ``TurnMessage``.

        ``payload`` is the private commitment content; ``public`` carries the
        schema-required public fields (``hint``, ``smell_grid``, ``timestamp`` and
        any optional public events). A fresh nonce is generated unless one is
        supplied for a test vector; either way it must be unused and must not equal
        the public challenge.
        """
        if isinstance(step, bool) or not isinstance(step, int) or step < 0:
            raise CommitRevealError(f"step must be a non-negative integer, got {step!r}")
        if self._last_step is not None and step <= self._last_step:
            raise CommitRevealError(f"step must strictly advance past {self._last_step}")
        commitment_nonce = nonce if nonce is not None else generate_commitment_nonce()
        if commitment_nonce in self._used_nonces:
            raise CommitRevealError("commitment nonce reuse is not allowed")
        if self.public_challenge is not None and commitment_nonce == self.public_challenge:
            raise CommitRevealError("commitment nonce must not equal the public challenge")
        digest = move_commit(payload, commitment_nonce)
        leaked = sorted(key for key in _SECRET_KEYS if key in public)
        if leaked:
            raise CommitRevealError(f"public turn fields must not include secrets: {leaked}")
        message: JsonObject = {"step": step, "sender": self.sender, "commit": digest, **public}
        validate_message("turn", message)
        self._records.append(SealedTurn(step, dict(payload), commitment_nonce, digest))
        self._used_nonces.add(commitment_nonce)
        self._last_step = step
        return message

    def acknowledge(self, response: object) -> None:
        """Require the transport acknowledgement ``{"ok": true}`` for a sent turn."""
        if not is_ok_response(response):
            raise CommitRevealError("missing transport acknowledgement")

    def audit_payload(self, result_claim: str) -> JsonObject:
        """Reveal every sealed record as a schema-valid ``AuditPayload``."""
        payload: JsonObject = {
            "sender": self.sender,
            "records": [
                {"payload": record.payload, "nonce": record.nonce, "commit": record.commit}
                for record in self._records
            ],
            "result_claim": result_claim,
        }
        validate_message("audit", payload)
        return payload


def verify_audit(payload: object) -> bool:
    """Return whether a revealed ``AuditPayload`` reproduces every commitment."""
    try:
        validate_message("audit", payload)
    except ProtocolError:
        return False
    records = payload["records"]  # type: ignore[index]
    return all(
        verify_commit(record["payload"], record["nonce"], record["commit"]) for record in records
    )
