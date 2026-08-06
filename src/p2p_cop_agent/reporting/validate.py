"""Nothing leaves this process without passing its own schema (`M7-14`).

`M7-14`'s condition is "an artifact that fails its own schema is **never sent**", and the
placement is the whole requirement. A validator that lives only in the test suite proves
the artifacts were valid *on the developer's machine*; it says nothing about the file a
tired operator emails at midnight after a hand-edit. So `validated_write` sits between
building and writing, and `write_artifact` is what the emit path calls underneath it.

**Why the stakes are asymmetric here.** Rule 34 (Prohibited): a report that is not JSON
"will be rejected and result in a zero score". Rule 35 (Mandatory): a conflicting report
"causes disqualification of the game and a score of 0 for **both** teams". A malformed
artifact is not a nuisance to be fixed on resend — sending it is worse than sending
nothing, because `:2584` only costs *us* credit for not reporting, while a bad report can
cost the opponent too.

`M7-14e` is the cross-artifact check, and it is the one no single schema can make:
every file in a set must carry the same `game_uid`. `MatchIdentity` already makes
disagreement hard to *produce*, but a set assembled from two different runs — a re-run
config beside yesterday's log — is exactly what an auditor notices and we would not.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from functools import cache
from pathlib import Path

from jsonschema.validators import validator_for

from p2p_cop_agent.reporting.emit import write_artifact

BUNDLE_SCHEMAS = Path(__file__).resolve().parents[3] / "shared_contract" / "schemas"
# `_schema` is stamped by each builder; this maps it to the controlled schema file. An
# artifact whose `_schema` is unknown is refused rather than waved through, because an
# unrecognised kind is precisely the one nobody has checked.
SCHEMA_FILES: dict[str, str] = {
    "per-subgame-config": "per-subgame-config.schema.json",
}


class ArtifactInvalidError(ValueError):
    """Raised when an artifact would be written or sent while failing its own schema."""


@cache
def _validator(filename: str):
    schema = json.loads((BUNDLE_SCHEMAS / filename).read_text("utf-8"))
    return validator_for(schema)(schema)


def validate_artifact(artifact: Mapping[str, object]) -> None:
    """Refuse an artifact that fails the controlled schema for its own `_schema` kind.

    Artifacts whose kind has no schema in the bundle yet are **not** silently accepted as
    valid; they are reported as unchecked, so "validated" never quietly means "unknown".
    """
    kind = artifact.get("_schema")
    if not isinstance(kind, str) or not kind:
        raise ArtifactInvalidError("artifact carries no `_schema`, so nothing can validate it")
    filename = SCHEMA_FILES.get(kind)
    if filename is None:
        raise ArtifactInvalidError(
            f"no controlled schema for `_schema` {kind!r}; refusing to call it validated"
        )
    errors = sorted(_validator(filename).iter_errors(dict(artifact)), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        where = "/".join(str(part) for part in first.path) or "(root)"
        raise ArtifactInvalidError(f"{kind} fails its schema at {where}: {first.message}")


def validated_write(directory: Path, filename: str, artifact: Mapping[str, object]) -> Path:
    """Validate, then write. The order is the requirement, not an implementation detail."""
    validate_artifact(artifact)
    return write_artifact(directory, filename, artifact)


def check_one_identity(artifacts: Sequence[Mapping[str, object]]) -> None:
    """Refuse a set whose files do not all describe the same game (`M7-14e`).

    No per-file schema can catch this: each artifact is individually valid and they simply
    belong to different matches. It is caught by comparing them to each other or not at
    all.
    """
    if not artifacts:
        raise ArtifactInvalidError("an empty artifact set proves nothing about a game")
    uids = {artifact.get("game_uid") for artifact in artifacts}
    if len(uids) != 1 or None in uids:
        raise ArtifactInvalidError(f"artifact set spans {len(uids)} game_uid value(s): {sorted(map(str, uids))}")
    ids = {artifact.get("game_id") for artifact in artifacts}
    if len(ids) != 1:
        raise ArtifactInvalidError(f"artifact set spans {len(ids)} game_id value(s): {sorted(map(str, ids))}")
