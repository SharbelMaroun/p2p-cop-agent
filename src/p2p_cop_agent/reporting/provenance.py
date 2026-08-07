"""Which code played this game, and whether the hash is the whole truth (`X-07`, `M9-09b`).

`protocol/attestation.running_git_commit()` already resolves the commit for the Step-0 seal.
This adds the half that seal does not need and an audit does: **whether the working tree was
clean when it ran**.

`git rev-parse HEAD` answers happily with uncommitted changes on disk. The hash is then a
truthful answer to the wrong question — the code that played is not the code at that commit,
and nothing in the artifact says so. Rule 53 wants the commit of the code that ran; a hash
pointing at a tree that differs from what ran identifies the wrong thing while looking
correct, which is worse than an obvious gap.

The reference implementation does not even reach this problem: `_subgame_entry` hard-codes
`github_commit` to the string `"unknown"` for both sides, so the field is emitted, is present
in every artifact, and identifies nothing at all.

Both external calls are injected, matching how `deadlines` and `watchdog` take time here, so
a dirty tree is testable without arranging one.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable

from p2p_cop_agent.protocol.attestation import running_git_commit


class ProvenanceError(RuntimeError):
    """Raised when the code that played a game cannot be identified."""


def _porcelain_status() -> str:
    completed = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                               text=True, check=True)
    return completed.stdout


def tree_is_clean(runner: Callable[[], str] = _porcelain_status) -> bool:
    """Whether the working tree matches HEAD. Empty porcelain output means clean."""
    try:
        return not runner().strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProvenanceError(f"could not read the working tree state: {exc}") from exc


def describe(*, commit: str | None = None,
             status_runner: Callable[[], str] | None = None) -> dict[str, object]:
    """The provenance block: the commit, and whether it accounts for what ran."""
    resolved = commit if commit is not None else running_git_commit()
    clean = tree_is_clean(status_runner) if status_runner else tree_is_clean()
    return {"github_commit": resolved, "working_tree_clean": clean}


def require_reproducible(provenance: dict[str, object]) -> None:
    """Refuse provenance that cannot identify what ran.

    Applied before a **counted** game, not a rehearsal. Playing from a dirty tree while
    practising is fine; doing it once the game counts leaves an audit trail pointing at code
    that never ran.
    """
    commit = provenance.get("github_commit")
    if not isinstance(commit, str) or len(commit) != 40:
        raise ProvenanceError(
            f"provenance carries no resolved commit ({commit!r}); rule 53 requires the "
            "commit hash of the code that played, and 'unknown' names nothing [AE-53]")
    if provenance.get("working_tree_clean") is not True:
        raise ProvenanceError(
            f"the working tree has uncommitted changes, so commit {commit[:12]} does not "
            "contain the code about to play; commit or stash first [AE-53]")
