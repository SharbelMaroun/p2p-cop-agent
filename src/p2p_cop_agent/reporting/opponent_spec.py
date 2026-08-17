"""Reading the opponent's Step-0 attestation out of the audit they disclosed to us.

Rule 53 wants a commit hash per game, per team. Ours comes from the running tree; theirs was
filed as ``"unknown"`` in every report we have ever sent, because nothing looked for it --
while it sat in the first record of every audit they revealed.

**Why read it rather than ask.** `yanell11` gave us their commit by email as
``27060c13…``; by the time run 8 played, their tree was ``33119340…`` and our own interop
sheet had likewise gone stale within the hour (it quoted ``9c3f0df0``/``a0fa9bfb`` for a
match played on ``7d13ab17``/``a74e1a23``). A number a human pasted into a message describes
the moment it was written; the Step-0 record describes the code that actually played, and it
is sealed under the same commitment as every move.

**Scope.** This reads only what the opponent published to us and asserts nothing about it.
If they never disclosed a Step-0 record we return ``None`` and the caller keeps
``"unknown"`` -- which is honest, and better than a value we inferred.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

STEP_ZERO_TYPE = "system_spec"


def opponent_step_zero(audits: Sequence[Mapping[str, object]]) -> dict:
    """Return the opponent's Step-0 attestation payload, or an empty mapping."""
    for envelope in audits or ():
        for record in (envelope.get("records") or ()):
            payload = record.get("payload") if isinstance(record, Mapping) else None
            if not isinstance(payload, Mapping):
                continue
            if payload.get("type") == STEP_ZERO_TYPE or payload.get("step") == 0:
                return dict(payload)
    return {}


def opponent_commit(audits: Sequence[Mapping[str, object]]) -> str | None:
    """Return the commit the opponent attested to at Step 0, or None if they sent none.

    Returns None rather than a placeholder so the caller decides what an absent
    attestation is called; inventing ``"unknown"`` here would hide the difference between
    "they did not disclose it" and "we did not look".
    """
    commit = opponent_step_zero(audits).get("github_commit")
    if isinstance(commit, str) and commit.strip():
        return commit.strip()
    return None
