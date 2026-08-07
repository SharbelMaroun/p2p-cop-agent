"""`X-07` / `M9-09b`: the commit hash identifies the code that actually played.

`running_git_commit()` already existed for the Step-0 seal. What was missing is the half an
audit needs and a seal does not: **whether the tree was clean**. `git rev-parse HEAD` answers
happily with uncommitted changes on disk, so a resolved hash can be a truthful answer to the
wrong question — and nothing in the artifact would say so.

The reference does not reach this problem: it hard-codes `github_commit` to `"unknown"`.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.reporting.provenance import (
    ProvenanceError,
    describe,
    require_reproducible,
    tree_is_clean,
)

SHA = "0123456789abcdef0123456789abcdef01234567"


def test_a_clean_tree_is_reported_as_clean() -> None:
    assert describe(commit=SHA, status_runner=lambda: "")["working_tree_clean"] is True


def test_a_dirty_tree_is_reported_rather_than_hidden() -> None:
    assert describe(commit=SHA, status_runner=lambda: " M x.py\n")["working_tree_clean"] is False


def test_a_git_failure_surfaces_as_a_provenance_error() -> None:
    def broken() -> str:
        raise OSError("git missing")

    with pytest.raises(ProvenanceError, match="working tree state"):
        tree_is_clean(runner=broken)


def test_a_clean_resolved_provenance_is_accepted() -> None:
    require_reproducible(describe(commit=SHA, status_runner=lambda: ""))


def test_a_dirty_tree_is_refused_before_a_counted_game() -> None:
    """Fine while rehearsing; once the game counts the recorded commit points at code that
    never ran."""
    with pytest.raises(ProvenanceError, match="uncommitted changes"):
        require_reproducible(describe(commit=SHA, status_runner=lambda: "?? new.py\n"))


@pytest.mark.parametrize("bad", ["unknown", "", SHA[:12], None, 42])
def test_anything_short_of_a_full_sha_is_refused(bad) -> None:
    """`"unknown"` is the exact placeholder the reference ships."""
    with pytest.raises(ProvenanceError, match="AE-53"):
        require_reproducible({"github_commit": bad, "working_tree_clean": True})


def test_a_missing_cleanliness_flag_is_not_read_as_clean() -> None:
    """An absent flag means nobody checked, which is not the same claim as a clean tree."""
    with pytest.raises(ProvenanceError, match="uncommitted changes"):
        require_reproducible({"github_commit": SHA})


def test_the_real_repository_resolves_its_own_commit() -> None:
    """One test against real Git, so the injected-runner tests cannot all pass while the
    actual command is wrong."""
    resolved = describe()
    assert len(resolved["github_commit"]) == 40
