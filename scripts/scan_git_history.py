"""Scan every blob in Git history for secrets, not only the working tree (`M9-04b`).

`check_secrets.py` answers "is there a secret in the files that exist now". That is the
wrong question at submission time. Rule 39 forbids secrets being *in the repository*, and a
credential deleted three commits ago is still in the repository: every clone carries the
blob and `git log -p` prints it. A working-tree scan reports clean on a repository that
leaks.

**The cost of a finding grows with every commit.** Removing a blob means rewriting history,
which invalidates every clone and changes every commit hash after the bad one — including
any hash already recorded in an emitted artifact under rule 53. So this runs early, not
once at the end.

Two things are checked, because a file can be a credential without containing anything that
matches a pattern:

* **blob contents**, through `check_secrets.line_findings` — the same function the
  working-tree gate uses, so the two can never disagree about what counts as a secret;
* **paths**, against the names `.gitignore` exists to exclude. A committed `token.json` is a
  finding regardless of what is inside it.

A finding is not fixed by deleting the file. **Rotate the credential first**: a key that
reached a pushed commit is compromised from that moment, and rewriting history is damage
control rather than a remedy.

Written for this repository against its own scanner's API (`M1-015`: the design travels,
the bytes do not). The Thief solved the same problem the same day; neither file was copied.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.check_secrets import TEXT_SUFFIXES, line_findings  # noqa: E402

# Names that must never appear in history at all, whatever they contain. These mirror the
# `.gitignore` entries rules 39 and 40 require; the name is evidence on its own.
FORBIDDEN_NAMES = frozenset({"credentials.json", "token.json"})
FORBIDDEN_SUFFIXES = (".key", ".pem", ".p12")
LARGEST_PLAUSIBLE_SECRET = 2_000_000  # beyond this a blob is not hand-written configuration
MAX_REPORTED = 200

# Findings in history that were read, judged, and are not secrets.
#
# **This is not an allowlist, and the difference is the whole point.** A pattern allowlist
# suppresses a rule everywhere and forever, including on a real credential added tomorrow —
# which is why nothing in this project has one. A key here is a **blob SHA**, and a blob SHA
# is the hash of exact bytes that a human read. Different content is a different SHA and
# fires again; a secret cannot hide behind an entry here, because it would have to produce a
# hash collision to do it.
#
# Entries are only ever for **immutable history**. A finding in the working tree is fixed at
# the source; a finding in a blob that already exists in every clone cannot be, and
# rewriting history over a false positive would invalidate every clone and change every
# commit hash after it — including hashes already recorded in emitted artifacts under rule
# 53. That cost is only worth paying for a real leak.
REVIEWED_HISTORY: dict[tuple[str, int], str] = {
    ("3a49edc8c380f7d0bd75ca1a5eed304f18f58c33", 546):
        "docs/PROMPT_LOG.md prose describing a dummy test vector built by string "
        "concatenation. Reviewed 2026-08-07 with the value redacted: the captured text is a "
        "three-character prefix, and no credential value is present in the blob. The "
        "working-tree copy was rephrased when the file-level scanner flagged it; this blob "
        "is the pre-fix version and can no longer change.",
}


def _git(*args: str) -> str:
    completed = subprocess.run(["git", *args], capture_output=True, text=True,
                               errors="replace", check=True)
    return completed.stdout


def reachable_blobs() -> list[tuple[str, str]]:
    """Every (sha, path) reachable from any ref, including deleted and rewritten files.

    `--all` rather than `HEAD`: a secret committed on a branch that was merged and deleted
    is unreachable from the current tip and perfectly present in the repository, which is
    precisely where one hides.
    """
    pairs: list[tuple[str, str]] = []
    for entry in _git("rev-list", "--objects", "--all").splitlines():
        sha, _, path = entry.partition(" ")
        if path:
            pairs.append((sha, path))
    return pairs


def is_forbidden(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    if name in FORBIDDEN_NAMES or name.endswith(FORBIDDEN_SUFFIXES):
        return True
    return name.startswith(".env") and not name.endswith(("-example", "example"))


def is_scannable(path: str) -> bool:
    return Path(path.rsplit("/", 1)[-1]).suffix.lower() in TEXT_SUFFIXES


def introducing_commit(path: str) -> str:
    """The earliest commit that added this path, so a rewrite knows where to start."""
    try:
        history = _git("log", "--all", "--reverse", "--format=%H", "--", path)
    except subprocess.CalledProcessError:
        return "unknown"
    return history.split("\n", 1)[0].strip() or "unknown"


def scan_history() -> list[str]:
    """Return every finding across every reachable blob."""
    results: list[str] = []
    reported_paths: set[str] = set()
    for sha, path in reachable_blobs():
        if is_forbidden(path) and path not in reported_paths:
            reported_paths.add(path)
            results.append(
                f"{path}: credential file committed (added in {introducing_commit(path)})")
        if not is_scannable(path):
            continue
        try:
            blob = _git("cat-file", "blob", sha)
        except subprocess.CalledProcessError:
            continue
        if len(blob) > LARGEST_PLAUSIBLE_SECRET:
            continue
        results.extend(
            f"{path}@{sha[:12]}:{number}: {label}"
            for number, line in enumerate(blob.splitlines(), start=1)
            for label in line_findings(line)
            if (sha, number) not in REVIEWED_HISTORY
        )
    return results


def reviewed_still_present() -> list[str]:
    """Reviewed entries whose blob is no longer reachable — i.e. stale pins.

    Reported so the table cannot quietly accumulate entries for objects that history no
    longer contains. A pin that matches nothing is dead weight at best, and at worst it
    suggests a review that no longer applies to anything.
    """
    live = {sha for sha, _ in reachable_blobs()}
    return [f"{sha[:12]}:{line}" for (sha, line) in REVIEWED_HISTORY if sha not in live]


def main() -> int:
    """Scan history and fail when anything that looks like a secret is present."""
    try:
        blobs = reachable_blobs()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"could not read Git history: {exc}")
        return 2
    results = scan_history()
    stale = reviewed_still_present()
    if stale:
        print(f"Stale reviewed-history pins (blob no longer reachable): {', '.join(stale)}")
    if not results:
        print(f"Git history scan OK: {len(blobs)} objects checked; "
              f"{len(REVIEWED_HISTORY)} reviewed historical finding(s) excluded by blob SHA; "
              "0 unreviewed findings.")
        return 0
    print(f"Possible secrets in Git history ({len(results)} finding(s)):")
    print(*results[:MAX_REPORTED], sep="\n")
    if len(results) > MAX_REPORTED:
        print(f"... and {len(results) - MAX_REPORTED} more")
    print("\nRotate the credential FIRST. A key that reached a pushed commit is compromised "
          "from that moment; rewriting history is damage control, not a fix.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
