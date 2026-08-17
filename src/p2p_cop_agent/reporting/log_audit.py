"""Verifying our own log, so the report's `audit` block is earned rather than asserted.

`sub_game_row` emitted `{"log_verified": True, "tampered": False}` as hardcoded literals
until 2026-08-17, so every result report claimed a verification that had never run. That is
a false statement inside a signed artifact -- the category that ends a game outright rather
than costing points -- and it was directly contradicted by the log artifact beside it, which
writes `"audit": {}` with the comment that an empty object is honest before the check runs.
One file was scrupulous and the next overwrote it with an assertion.

**What can honestly be checked here.** Each sealed record carries the commitment alongside
the payload and nonce that produced it, so recomputing `move_commit(payload, nonce)` over
every step either reproduces the recorded commit or does not. That is a real check with a
real failure mode: a payload edited after the fact cannot reproduce its own commitment.

**What cannot, and is deliberately not claimed.** This says nothing about the opponent's
log. Cross-peer reconciliation is a separate obligation (rule 36) performed against their
disclosure, and conflating the two would be the same overclaim in a new place. The keys
stay `log_verified`/`tampered` because the template requires them; their meaning is "our
own reveal reproduces our own commitments".
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from p2p_cop_agent.protocol.commit import move_commit


def verify_own_commitments(sealed: Sequence[Mapping[str, object]]) -> dict:
    """Recompute every commitment from its reveal; report what was actually found.

    An empty record set returns `log_verified: False` rather than a vacuous True: a log
    with nothing in it has not been verified, it has merely not been contradicted, and the
    honest answer to "did the audit pass" is no.
    """
    if not sealed:
        return {"log_verified": False, "tampered": False, "steps_checked": 0}

    mismatched = 0
    for record in sealed:
        payload, nonce = record.get("payload"), record.get("nonce")
        recorded = record.get("commit")
        if not isinstance(nonce, str) or not isinstance(recorded, str):
            mismatched += 1
            continue
        try:
            if move_commit(payload, nonce) != recorded:
                mismatched += 1
        except Exception:  # noqa: BLE001 - an uncomputable commit is a failed check
            mismatched += 1

    return {
        "log_verified": mismatched == 0,
        "tampered": mismatched > 0,
        "steps_checked": len(sealed),
    }
