"""Write the played match's game log from its own audit (M5-18a).

The first two-process rehearsal exposed the gap: `play_match` writes the declaration
and the per-sub-game config when given a directory, but the served path passed no
directory and produced **no artifacts at all** — a counted game would have ended with
the graded evidence existing only on the opponent's side. This module closes the log
half: the sub-game's audit payload already carries every sealed payload, nonce, and
commit, which is exactly what `build_log` + `reveal_log` need, and the reveal is
legitimate here because the game has ended (rule 18's boundary).

The summary names the *real* opponent and the *real* config lock from the negotiated
agreement — an artifact naming a placeholder opponent is a false record wearing a
valid schema, and the audit exists to catch false records, including ours.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

from p2p_cop_agent.reporting import MatchIdentity, write_artifact
from p2p_cop_agent.reporting.log_artifact import build_log, reveal_log
from p2p_cop_agent.reporting.log_audit import verify_own_commitments
from p2p_cop_agent.reporting.naming import log_filename
from p2p_cop_agent.reporting.opponent_spec import opponent_commit

# Outcome name -> the role the scoring table pays for it; a technical loss pays no one.
WINNER_BY_OUTCOME = {"CAPTURE": "police", "SURVIVAL": "thief"}


class MatchArtifactError(RuntimeError):
    """Raised when a finished match cannot produce an auditable artifact.

    Distinct from `LogArtifactError`, which polices the *shape* of a log that has records.
    This one reports that there was nothing to write and says why the match ended, so the
    cause survives into the driver's output instead of being replaced by a traceback.
    """


def persist_match(
    directory: Path,
    *,
    game_id: str,
    sub_game: int,
    identity: Mapping[str, object],
    opponent: Mapping[str, object],
    config_sha256: str,
    outcome: object,
    steps: int,
    started_at: str,
    audit: Mapping[str, object],
    reason: str,
    opponent_audits: Sequence[dict],
) -> None:
    """Write everything one finished sub-game leaves behind (`C-051`).

    Extracted from `serve.py` at a real seam: playing a match and recording what it
    produced are different jobs, and the recording half grew a second artifact when the
    opponent's verified audit stopped being thrown away. Keeping both writes together
    also makes the pairing obvious — our sealed log, and the evidence they staked their
    commitments on — which is the pairing a dispute is settled from.
    """
    from p2p_cop_agent.adapters.opponent_audit import write_opponent_audit  # noqa: PLC0415

    write_match_log(
        directory, game_id=game_id, game_uid=config_sha256[:32], sub_game=sub_game,
        group_id=str(identity.get("group_id", "unknown")),
        opponent_group_id=str(opponent.get("group_id", "unknown")),
        config_sha256=config_sha256, outcome=outcome, steps=steps,
        started_at=started_at, audit=audit,
        # Rule 53 per game, per team (inst/:1295): ours from the running tree, theirs
        # from the negotiation identity -- or, failing that, from the Step-0 attestation
        # inside the audit they disclosed to us. Theirs read `"unknown"` in every report we
        # ever sent while the value sat in the first record of every audit they revealed.
        # Preferring the attestation over anything typed by hand is the point: their emailed
        # commit was already stale by the time run 8 played, and so was our own sheet.
        github_commit={
            str(identity.get("group_id", "unknown")):
                str(identity.get("git_commit_hash", "unknown")),
            str(opponent.get("group_id", "unknown")):
                str(opponent.get("git_commit_hash", "")
                    or opponent_commit(opponent_audits) or "unknown"),
        },
        reason=reason,
    )
    written = write_opponent_audit(
        directory, game_id=game_id, sub_game=sub_game, audits=opponent_audits,
        opponent_group_id=str(opponent.get("group_id", "")),
    )
    if written is not None:
        print(f"opponent audit retained: {written.name}")


def write_match_log(
    directory: Path,
    *,
    game_id: str,
    game_uid: str,
    sub_game: int,
    group_id: str,
    opponent_group_id: str,
    config_sha256: str,
    outcome: object,
    steps: int,
    started_at: str,
    audit: Mapping[str, object],
    github_commit: Mapping[str, str] | None = None,
    reason: str = "",
) -> Path:
    """Assemble in-play records from the audit, reveal them, and write the log.

    ``reason`` is ``SubGameOutcome.reason`` -- the text of whatever ended the sub-game
    (`C-050`). It was computed all along and thrown away here, so a log said
    ``technical_loss`` and never why. Two sub-games against `yanell11` on 2026-08-15
    ended that way, and diagnosing them cost a whole series and produced a wrong
    attribution: our wire recorder logs inbound only, so "their turn arrived, then
    silence" was read as *them* stopping when it was equally consistent with *us*
    stopping -- which is what had happened. The opponent's server log settled it, and
    ours could not. A recorded outcome without its cause is an outcome nobody can act on.
    """
    identity = MatchIdentity(game_id, game_uid)
    # Turn records only: the step-0 attestation seals in the same ledger but is its
    # own artifact, not a move. Older payloads carry no `step` member (the ledger
    # numbered them externally), so the commit order numbers them here.
    sealed = [
        record for record in (audit.get("records") or [])
        if isinstance(record.get("payload"), Mapping) and "move" in record["payload"]
    ]
    in_play = [
        {
            "step": record["payload"].get("step", number), "sender": "police",
            "commit": record["commit"], "move": record["payload"]["move"],
            "hint": record["payload"]["hint"], "intent": record["payload"]["intent"],
        }
        for number, record in enumerate(sealed, start=1)
    ]
    name = getattr(outcome, "name", str(outcome))
    summary = {
        "sub_game_number": sub_game, "group_id": group_id, "role": "police",
        "opponent_group_id": opponent_group_id, "result": name.lower(),
        "winner_role": WINNER_BY_OUTCOME.get(name, "none"), "steps": steps,
        "timezone": "UTC", "started_at": started_at,
        "ended_at": datetime.now(UTC).isoformat(),
        "duration_seconds": 0, "tokens_total": 0,
        # Rule 53's per-game commit hash, per team, recorded at write time so the
        # series report can carry it without reconstruction (C-043).
        "github_commit": dict(github_commit or {}),
        # EARNED, not asserted. `sub_game_row` used to emit
        # `{"log_verified": True, "tampered": False}` as hardcoded literals, so every
        # report claimed a verification that had never run -- a false statement in a signed
        # artifact, which is the one category that ends a game outright rather than
        # costing points. What we can honestly check is our OWN log: each sealed record
        # carries its commit beside the payload and nonce that produced it, so recomputing
        # `move_commit` over every step either reproduces the commitment or does not.
        #
        # This is deliberately narrower than it sounds, and the narrowness is the point:
        # it verifies that our reveal matches our own commitments, NOT that the opponent's
        # log is sound. Cross-peer reconciliation is a separate act (rule 36) and fills
        # nothing here.
        "audit": verify_own_commitments(sealed),
        # `C-050`: why the sub-game ended. Always present so its ABSENCE never has to be
        # interpreted; empty on a clean capture or survival, where the result is the
        # whole story, and populated on anything else.
        "result_reason": reason,
    }
    # A match that negotiated but never took a turn seals a step-0 attestation and no
    # moves, so `sealed` is empty and `build_log` rightly refuses -- a log with no records
    # cannot be audited. Raising ITS generic message here loses the one thing worth having:
    # `reason`, the whole point of `C-050`. This module's own docstring says an outcome
    # without its cause is an outcome nobody can act on, and on 2026-08-16 that is exactly
    # what happened -- run 6 sub-game 1 died after 157s and the traceback overwrote the
    # explanation in the driver's tail, leaving the opponent's logs as the only witness
    # for the second time.
    if not in_play:
        raise MatchArtifactError(
            f"sub-game {sub_game} ended {name.lower()} with NO turn records: the peers "
            f"negotiated (the step-0 attestation sealed) but no move was ever exchanged. "
            f"reason={reason!r}. Nothing is written, because a log with no records cannot "
            f"be audited [AE-18] -- but the reason above is the cause worth chasing."
        )
    log = build_log(identity=identity, sub_game=sub_game, records=in_play, summary=summary)
    revealed = reveal_log(
        log,
        [{"step": record["payload"].get("step", number), "payload": record["payload"],
          "nonce": record["nonce"]} for number, record in enumerate(sealed, start=1)],
        mutual_agreement={"opponent_group_id": opponent_group_id,
                          "sha256": config_sha256, "confirmed": True},
    )
    return write_artifact(directory, log_filename(identity, sub_game), revealed)
