"""Every artifact of one series must agree on `game_id` and `game_uid`.

friendly-9 shipped three identities for one series and nothing noticed:

    Cop log     41cd0d7dc0f6bbcc0f305f051b9fbbfa       config_sha256[:32] -- not a UUID
    Thief log   9b80122e-75f9-c32d-5bff-abc032ae086b   the UNLABELLED derivation
    result      248354ae-94b5-0617-238d-cebcf015d984   the agreed value

The result was right because the report layer recomputes it, so every check that read the
summary passed. An identity correct in the aggregate and wrong in the evidence beneath it
survives exactly the inspections we were doing. `yanell11` verified their own side after we
reported ours, found it clean, and made it a law in their suite; this is ours.

Two rules, both learned from that failure:

1. **agreement** -- within one results directory, every `game_id` and every `game_uid` must
   be a single value. Not "mostly", not "the result is right".
2. **shape** -- a `game_uid` must be a UUID. `config_sha256[:32]` is 32 hex characters with
   no hyphens; it is a digest only one side can compute, so it names the series something
   no peer and no other artifact can reproduce. Checking the shape catches it even before
   the disagreement does.

Usage:  uv run python scripts/check_artifact_identity.py [results_dir ...]
        (no arguments: every games/* directory in this repository)
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

UUID_SHAPE = re.compile(r"\A[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")
IDENTITY_KEYS = ("game_id", "game_uid")


def artifact_identities(directory: Path) -> dict[str, dict[str, list[str]]]:
    """Map each identity key to the values found, and which files carried them."""
    found: dict[str, dict[str, list[str]]] = {key: defaultdict(list) for key in IDENTITY_KEYS}
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        for key in IDENTITY_KEYS:
            value = data.get(key)
            if isinstance(value, str) and value:
                found[key][value].append(path.name)
    return {key: dict(values) for key, values in found.items()}


def problems(directory: Path) -> list[str]:
    """Return every identity fault in one results directory."""
    faults: list[str] = []
    identities = artifact_identities(directory)
    for key, values in identities.items():
        if len(values) > 1:
            detail = "; ".join(
                f"{value!r} in {', '.join(sorted(files))}" for value, files in sorted(values.items()))
            faults.append(f"{directory.name}: {len(values)} different {key} values -- {detail}")
    for value, files in identities.get("game_uid", {}).items():
        if not UUID_SHAPE.fullmatch(value):
            faults.append(
                f"{directory.name}: game_uid {value!r} is not a UUID (in {', '.join(sorted(files))})"
                " -- a 32-hex digest here is config_sha256[:32], which only one peer can compute")
    return faults


def main(argv: list[str]) -> int:
    roots = [Path(a) for a in argv[1:]] or sorted(
        d for d in (Path(__file__).resolve().parents[1] / "games").iterdir() if d.is_dir())
    faults: list[str] = []
    checked = 0
    for directory in roots:
        if not directory.is_dir():
            continue
        if not any(directory.glob("*.json")):
            continue
        checked += 1
        faults.extend(problems(directory))
    if faults:
        print("Artifact identity violations:")
        for fault in faults:
            print(f"  {fault}")
        return 1
    print(f"Artifact identity OK: {checked} results directories agree on game_id and game_uid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
