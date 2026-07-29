"""Receive-side turn intake with idempotency and replay guards (M4-04).

``TurnLedger`` (M4-03) is the send side of one sub-game; ``TurnInbox`` is the
receive side. It admits inbound public ``TurnMessage``s from peers, deduplicating
redelivery of the same ``(sender, step, commit)`` so a turn is applied once,
rejecting a re-sent ``(sender, step)`` that carries a different commit as a
conflict, and rejecting any step that fails to strictly advance its sender as a
replay. Every failure is a deterministic ``ProtocolError`` subclass; nothing here
touches the read-only ``shared_contract`` bundle. Tamper detection at reveal time
is M4-05.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from p2p_cop_agent.protocol.messages import ProtocolError, require_wire_role, validate_message
from p2p_cop_agent.shared.config import JsonObject


class ReplayError(ProtocolError):
    """Raised when a turn's step does not strictly advance its sender."""


class ConflictError(ProtocolError):
    """Raised when a ``(sender, step)`` is re-sent with a different commit."""


@dataclass(frozen=True, slots=True)
class Intake:
    """The outcome of admitting one inbound turn.

    ``fresh`` is ``True`` the first time a ``(sender, step, commit)`` is applied
    and ``False`` on an idempotent redelivery, so an adapter can acknowledge a
    duplicate without applying its effect twice.
    """

    step: int
    sender: str
    commit: str
    fresh: bool


@dataclass
class TurnInbox:
    """Track inbound public turns per sender within one sub-game."""

    _commits: dict[tuple[str, int], str] = field(default_factory=dict)
    _last_step: dict[str, int] = field(default_factory=dict)

    def admit(self, message: JsonObject) -> Intake:
        """Admit one inbound public turn, or reject it deterministically.

        A redelivery of an already-seen ``(sender, step)`` with the same commit is
        idempotent (``fresh=False``); the same key with a different commit is a
        :class:`ConflictError`; any not-yet-seen step that does not strictly
        advance its sender is a :class:`ReplayError`.
        """
        validate_message("turn", message)
        sender = require_wire_role(message["sender"])
        step, digest = message["step"], message["commit"]
        key = (sender, step)
        seen = self._commits.get(key)
        if seen is not None:
            if seen == digest:
                return Intake(step, sender, digest, fresh=False)
            raise ConflictError(f"conflicting commit for {sender} step {step}")
        last = self._last_step.get(sender)
        if last is not None and step <= last:
            raise ReplayError(f"step {step} does not advance past {last} for {sender}")
        self._commits[key] = digest
        self._last_step[sender] = step
        return Intake(step, sender, digest, fresh=True)

    def commits_for(self, sender: str) -> tuple[str, ...]:
        """Return the commits accepted live for a sender, in step order.

        This is the sequence an end-game audit must reproduce exactly, so a peer
        cannot substitute a fabricated record after the fact (M4-05).
        """
        require_wire_role(sender)
        ordered = sorted(
            (step, digest) for (who, step), digest in self._commits.items() if who == sender
        )
        return tuple(digest for _, digest in ordered)
