"""Write an artifact to disk so a crash cannot leave a half-written one (`M7-25`).

Two obligations meet here.

**`M7-25`: emission must not depend on transport health.** "A disconnected game still
produces its artifact set." So writing takes an already-built object and a directory —
it holds no socket, no client, and no peer state. A game that ends because the opponent
vanished still emits everything it knows, which is the only way the four artifacts can be
evidence of a game that went wrong.

**Atomicity.** An artifact is read back by an auditor and by rule 19's audit phase, whose
sanction is "score of 0 for the falsifying group". A half-written file is
indistinguishable from a tampered one at that point, and the failure mode is silent: the
process crashes, the file looks present, and the problem surfaces days later during
grading. Writing to a temporary file in the same directory and then `os.replace` makes
the visible file either the old one or the complete new one, never a prefix.

The same-directory detail matters: `os.replace` is only atomic within a filesystem, so a
temp file under the system temp directory would silently degrade to a copy.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path


class EmitError(OSError):
    """Raised when an artifact cannot be written where it was asked to go."""


def artifact_bytes(artifact: Mapping[str, object]) -> bytes:
    """Serialize an artifact exactly as it will sit on disk.

    Sorted keys and `ensure_ascii=False`, matching the canonicalization the hashes use,
    so a reader who re-serializes gets the same bytes. A trailing newline because these
    are committed to a repository and a file without one is a diff nuisance forever.
    """
    text = json.dumps(dict(artifact), sort_keys=True, ensure_ascii=False, indent=2)
    return (text + "\n").encode("utf-8")


def write_artifact(directory: Path, filename: str, artifact: Mapping[str, object]) -> Path:
    """Write one artifact atomically and return the path it now occupies.

    Refuses a filename carrying a directory component: every caller derives its name from
    `reporting.naming`, and a name that could climb out of the artifact directory would
    mean an opponent-supplied `game_id` had reached the filesystem unchecked.
    """
    if "/" in filename or "\\" in filename or filename in {"", ".", ".."}:
        raise EmitError(f"artifact filename {filename!r} must be a bare name")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    payload = artifact_bytes(artifact)
    handle, temporary = tempfile.mkstemp(dir=str(directory), prefix=f".{filename}.", suffix=".tmp")
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())  # the bytes, not just the buffer, before the swap
        destination = directory / filename
        os.replace(temporary, destination)
    except OSError:
        Path(temporary).unlink(missing_ok=True)
        raise
    return destination


def write_all(directory: Path, artifacts: Mapping[str, Mapping[str, object]]) -> dict[str, Path]:
    """Write a whole set, keyed by filename. Order is irrelevant; each write is atomic."""
    return {name: write_artifact(directory, name, body) for name, body in artifacts.items()}
