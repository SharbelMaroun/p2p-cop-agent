"""Run every gate from a fresh clone, the way the grader will (`M9-12b`).

Every gate passes on this machine. That is a weaker claim than it sounds: a working tree
accumulates things a clone does not have — an editable install, a stale `.venv`, a file
written but never `git add`ed, a cached artifact. **The question that matters is whether the
gates pass on a checkout of what was actually pushed.**

So this clones `HEAD` locally, installs from the lockfile with `uv sync --frozen`, and runs
each gate there. `--frozen` is the point of `G-001`: a resolve that quietly updates a
dependency proves the gates pass against some other version of the project.

**The untracked-file case is what earns its keep.** A gate script that exists only in the
working tree passes here and vanishes in a clone, and the symptom — "no such file" during a
grader's run — arrives at the worst possible moment. `git clone` copies only what is
committed, so the clone answers that by construction. The Thief's copy of this caught two
real failures on its first run.

`M9-12a` (a genuinely different machine) is **not** this, and the difference is recorded
rather than blurred: a local clone shares the OS, the Python build and the uv cache, so it
catches missing files and lockfile drift, never platform-specific breakage.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The gates that can run inside a clone. The prompt log is reviewed rather than executed, and
# CI runs on the push rather than here, so neither appears.
GATES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("lint", ("uv", "run", "ruff", "check", ".")),
    ("tests + branch coverage", ("uv", "run", "python", "-m", "pytest", "-q",
                                 "-p", "no:cacheprovider")),
    ("file lengths", ("uv", "run", "python", "scripts/check_file_lengths.py")),
    ("secret scan", ("uv", "run", "python", "scripts/check_secrets.py")),
    ("submission contents", ("uv", "run", "python", "scripts/check_submission_contents.py")),
    ("patch whitespace", ("git", "diff", "--check")),
)


def run(command: tuple[str, ...], cwd: Path, timeout: int = 900) -> tuple[bool, str]:
    try:
        done = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                              errors="replace", timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    tail = (done.stdout + done.stderr).strip().splitlines()[-3:]
    return done.returncode == 0, "\n      ".join(tail)


def main() -> int:
    """Clone, install frozen, and run every runnable gate inside the clone."""
    workspace = Path(tempfile.mkdtemp(prefix="cop-clean-clone-"))
    clone = workspace / "repo"
    failures: list[str] = []
    try:
        ok, detail = run(("git", "clone", "--local", "--no-hardlinks", str(ROOT), str(clone)),
                         cwd=workspace)
        if not ok:
            print(f"clone FAILED: {detail}")
            return 2
        print(f"Cloned into {clone}")

        ok, detail = run(("uv", "sync", "--frozen"), cwd=clone)
        print(f"frozen install: {'PASS' if ok else 'FAIL'}\n      {detail}")
        if not ok:
            print("\nA frozen install that fails means the lockfile and the manifest "
                  "disagree; every later gate would run against a different project.")
            return 1

        for name, command in GATES:
            ok, detail = run(command, cwd=clone)
            print(f"{name}: {'PASS' if ok else 'FAIL'}\n      {detail}")
            if not ok:
                failures.append(name)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    if failures:
        print(f"\n{len(failures)} gate(s) failed in a clean clone: {', '.join(failures)}")
        print("Re-run each in the working tree. Passing there means something is not "
              "committed; failing there too means the clone simply surfaced it first.")
        return 1
    print(f"\nClean-clone verification OK: {len(GATES) + 1} gates pass on a fresh checkout.")
    print("Note: a LOCAL clone. `M9-12a` (a second machine) is a different claim, still open.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
