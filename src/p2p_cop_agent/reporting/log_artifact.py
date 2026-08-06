"""The game log: the artifact a stranger actually re-verifies (`M7-24`).

`M7-24`'s condition is "a third party can re-verify **without our code**", and `:1690`
says exactly what that third party does: the replay viewer "takes the Nonce and the move
appearing in the log, re-encodes them, and compares the result to the original Commitment
value using the SHA-256 algorithm". Green `Verified OK`, or a red `TAMPERED` banner that
"immediately invalidates" the replay.

So the log must carry, for every step, enough to recompute a digest from scratch — and
nothing that would let someone recompute it *too early*.

**The two phases, and why they are separate types here (`M7-24b`).** Rule 18 is Mandatory:
"Keep the Nonce secret until the end of the game. Sanction: **Disqualification due to
risk of dictionary attack**." A log written step-by-step with its nonces inline would
violate that the moment the file is shared or committed mid-game — and it would look
perfectly correct, because the finished file is identical either way. The rule is about
*when* a byte exists, which no inspection of the final artifact can detect.

`build_log` therefore refuses a step that carries a nonce at all, and `reveal_log` is the
only way to add them. The constraint becomes unrepresentable rather than merely observed:
you cannot write the forbidden intermediate state with this module, whatever you intend.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from p2p_cop_agent.reporting.naming import MatchIdentity, config_filename, log_filename
from p2p_cop_agent.shared.config import JsonObject

SCHEMA_VERSION = "1.2"
# What a step records while the game is running. `intent` is the bluff flag: `M7-24c`
# wants the verbal layer auditable too, and a hint without its intent cannot be judged.
STEP_FIELDS = ("step", "sender", "commit", "move", "hint", "intent")
FORBIDDEN_IN_PLAY = ("nonce", "payload")


class LogArtifactError(ValueError):
    """Raised when a log would be unverifiable, or would reveal a nonce too early."""


def build_log(
    *,
    identity: MatchIdentity,
    sub_game: int,
    steps: Sequence[Mapping[str, object]],
    summary: Mapping[str, object],
) -> JsonObject:
    """Assemble the in-play log: commitments and public moves, **no nonces**.

    Refuses a step carrying `nonce` or `payload`. Both are the reveal, and a reveal in
    the running log is rule 18's sanction waiting for someone to share the file.
    """
    if not steps:
        raise LogArtifactError("a log with no steps cannot be audited")
    recorded = []
    for index, step in enumerate(steps):
        leaked = [name for name in FORBIDDEN_IN_PLAY if name in step]
        if leaked:
            raise LogArtifactError(
                f"step {index} carries {', '.join(leaked)}; the nonce stays secret until the "
                "end of the game [AE-18], so reveals belong in the audit section"
            )
        missing = [name for name in STEP_FIELDS if name not in step]
        if missing:
            raise LogArtifactError(f"step {index} is missing {', '.join(missing)}")
        recorded.append({name: step[name] for name in STEP_FIELDS})
    return {
        "_schema": "game-log",
        "schema_version": SCHEMA_VERSION,
        "game_id": identity.game_id,
        "game_uid": identity.game_uid,
        "sub_game": sub_game,
        "links": {
            "config": config_filename(identity, sub_game),
            "log": log_filename(identity, sub_game),
        },
        "summary": dict(summary),
        "steps": recorded,
        "audit": None,  # explicit: the reveal has not happened yet, rather than absent
    }


def reveal_log(
    log: Mapping[str, object],
    reveals: Sequence[Mapping[str, object]],
    mutual_agreement: Mapping[str, object] | None = None,
) -> JsonObject:
    """Return the log with its final audit section: the nonces and payloads, at the end.

    ``mutual_agreement`` takes `orchestration.settlement.settlement_record`. Added
    2026-08-06 after asking the reference-code notebook what its log actually carries:
    `mutual_agreement` is a **top-level key** there, and `settlement_record`'s own
    docstring had claimed to produce "the `mutual_agreement` block for the log artifact"
    while nothing consumed it. The producer existed and the consumer did not.

    Every reveal must line up with a recorded step, because a reveal for a step that was
    never played — or a step left unrevealed — is exactly what an auditor is looking for.
    """
    steps = log.get("steps")
    if not isinstance(steps, Sequence) or not steps:
        raise LogArtifactError("cannot reveal a log that has no steps")
    if len(reveals) != len(steps):
        raise LogArtifactError(
            f"{len(reveals)} reveals for {len(steps)} steps; every step is revealed exactly once"
        )
    records = []
    for index, (step, reveal) in enumerate(zip(steps, reveals, strict=True)):
        missing = [name for name in ("nonce", "payload") if name not in reveal]
        if missing:
            raise LogArtifactError(f"reveal {index} is missing {', '.join(missing)}")
        if reveal.get("step") != step.get("step"):
            raise LogArtifactError(
                f"reveal {index} is for step {reveal.get('step')!r}, log has {step.get('step')!r}"
            )
        records.append({
            "step": step["step"],
            "commit": step["commit"],
            "nonce": reveal["nonce"],
            "payload": reveal["payload"],
        })
    revealed: JsonObject = {**dict(log), "audit": {"records": records}}
    if mutual_agreement is not None:
        revealed["mutual_agreement"] = dict(mutual_agreement)
    return revealed


def is_revealed(log: Mapping[str, object]) -> bool:
    """Whether the reveal has happened — the one check a caller needs before sharing."""
    return isinstance(log.get("audit"), Mapping)
