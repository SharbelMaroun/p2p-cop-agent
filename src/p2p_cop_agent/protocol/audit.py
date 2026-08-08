"""Post-game audit verification and tamper detection (M4-05).

At the end-game reveal each peer submits an ``AuditPayload`` disclosing, for every
sealed turn, the hidden payload and its per-turn commitment nonce. ``audit_reveal``
recomputes every commitment and, when the live commits are supplied, cross-checks
the reveal against what was actually received during play. Any byte, field, or
commitment-nonce mutation breaks the hash and yields a ``TAMPERED`` verdict; a
reveal that silently swaps a whole record is caught by the live cross-check. A
tampered verdict identifies the falsifying peer, whose sub-game score is the
zero-point technical loss (Appendix E rules 19/48); the counterpart award stays
unresolved under ``U-026`` and is never invented here.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from p2p_cop_agent.protocol.commit import verify_commit
from p2p_cop_agent.protocol.messages import ProtocolError, validate_message
from p2p_cop_agent.shared.config import JsonObject


class AuditVerdict(StrEnum):
    """The outcome of verifying one peer's end-game reveal."""

    VERIFIED = "verified"
    TAMPERED = "tampered"


@dataclass(frozen=True, slots=True)
class AuditReport:
    """A decided audit outcome.

    ``sender`` is the wire role of the audited peer (``None`` only when the payload
    was too malformed to read one). On a tampered verdict ``tampered_index`` is the
    first offending record when a single record can be blamed.
    """

    verdict: AuditVerdict
    sender: str | None
    reason: str | None = None
    tampered_index: int | None = None

    @property
    def verified(self) -> bool:
        """Return whether the reveal reproduced every commitment."""
        return self.verdict is AuditVerdict.VERIFIED


def _tampered(sender: str | None, reason: str, index: int | None = None) -> AuditReport:
    return AuditReport(AuditVerdict.TAMPERED, sender, reason, index)


def _first_divergence(live: Sequence[str], revealed: Sequence[str]) -> int | None:
    """Return the first index at which two commit sequences differ, if aligned."""
    for index, (expected, actual) in enumerate(zip(live, revealed, strict=False)):
        if expected != actual:
            return index
    return None


def audit_reveal(payload: object, received_commits: Sequence[str] | None = None) -> AuditReport:
    """Verify an end-game reveal, detecting any tamper against its own commitments.

    ``received_commits`` is the ordered sequence of commits the verifier accepted
    live for this peer (e.g. from a :class:`TurnInbox`). When supplied, the reveal
    must present exactly those commits in order, so a peer cannot substitute a
    fabricated record after the fact.
    """
    try:
        validate_message("audit", payload)
    except ProtocolError as exc:
        return _tampered(None, f"malformed audit payload: {exc}")
    body: JsonObject = payload  # type: ignore[assignment]
    sender = body["sender"]
    records = body["records"]
    for index, record in enumerate(records):
        if not verify_commit(record["payload"], record["nonce"], record["commit"]):
            return _tampered(sender, "revealed record does not reproduce its commitment", index)
    if received_commits is not None:
        live = tuple(received_commits)
        revealed = tuple(record["commit"] for record in records)
        if live != revealed:
            index = _first_divergence(live, revealed)
            return _tampered(sender, "reveal does not match the commits received live", index)
    return AuditReport(AuditVerdict.VERIFIED, sender)
