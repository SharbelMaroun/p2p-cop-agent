"""Protocol-session helpers mixed into the SDK boundary.

These methods let an adapter run one sub-game's commit-reveal exchange and the
Step-0 attestation without re-implementing protocol policy. They live here so the
core :class:`~p2p_cop_agent.sdk.api.CopSDK` configuration surface stays small; the
mixin only reads the two configuration fields it annotates below.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from p2p_cop_agent.domain.scoring import ScoringTable
from p2p_cop_agent.protocol import (
    AuditReport,
    HostSpec,
    SealedAttestation,
    TurnInbox,
    TurnLedger,
    audit_reveal,
    build_step_zero,
    running_git_commit,
    seal_step_zero,
)


class ProtocolSessionMixin:
    """Commit-reveal and Step-0 helpers for a configured SDK instance."""

    __slots__ = ()

    # Provided by the concrete SDK dataclass.
    game_config: Mapping[str, object]
    config_sha256: str

    def new_turn_ledger(self, sender: str, public_challenge: str | None = None) -> TurnLedger:
        """Return a fresh transport-neutral commit-reveal ledger for one sub-game.

        ``sender`` is the peer's wire role for this sub-game (``police``/``thief``),
        not the fixed package role, because roles alternate. ``public_challenge`` is
        the peer's own ``negotiate.nonce`` when known, recorded only to prove that a
        secret commitment nonce never equals it.
        """
        return TurnLedger(sender=sender, public_challenge=public_challenge)

    def new_turn_inbox(self) -> TurnInbox:
        """Return a fresh receive-side turn intake for one sub-game.

        The inbox deduplicates redelivered turns, rejects a re-sent step whose
        commit differs, and rejects any step that fails to strictly advance its
        sender, so an adapter never applies a turn twice or accepts a replay.
        """
        return TurnInbox()

    def verify_opponent_audit(
        self,
        payload: object,
        received_commits: Sequence[str] | None = None,
    ) -> AuditReport:
        """Verify an opponent's end-game reveal, detecting any commitment tamper.

        Pass ``received_commits`` (e.g. ``TurnInbox.commits_for(sender)``) to also
        prove the reveal matches what was accepted live, catching a post-hoc swap.
        """
        return audit_reveal(payload, received_commits)

    def score_after_audit(self, report: AuditReport) -> int | None:
        """Return the falsifying peer's zero-point sanction, or ``None`` if verified.

        A tampered reveal is a technical loss: the falsifying peer scores the
        configured ``technical_loss`` value (Appendix E rules 19/48). The
        non-falsifying counterpart award stays unresolved under ``U-026`` and is
        deliberately not returned here.
        """
        if report.verified:
            return None
        return ScoringTable.from_config(self.game_config).technical_loss_award()

    def seal_step_zero_attestation(
        self,
        *,
        host: HostSpec,
        model: str,
        group_id: str,
        game_id: str,
        git_commit: str | None = None,
        nonce: str | None = None,
    ) -> SealedAttestation:
        """Seal this peer's Step-0 declaration before any move is made.

        The declaration binds the hardware, LLM model, group and game identity, the
        negotiated ``config_sha256``, and the exact running Git commit (read from
        ``git rev-parse HEAD`` unless supplied). The seal is reproducible from the
        revealed ``(payload, nonce)`` by any conforming peer.
        """
        commit = git_commit if git_commit is not None else running_git_commit()
        payload = build_step_zero(
            host=host,
            model=model,
            group_id=group_id,
            game_id=game_id,
            git_commit=commit,
            config_sha256=self.config_sha256,
        )
        return seal_step_zero(payload, nonce=nonce)
