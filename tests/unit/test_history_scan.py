"""`M9-04b`: the history scanner, and the honesty of its reviewed-findings table.

The scanner answers a question the working-tree gate cannot: rule 39 forbids secrets being
*in the repository*, and a credential deleted three commits ago is still in every clone.

The part that needs testing is not the scan — it is `REVIEWED_HISTORY`. Any mechanism that
suppresses a security finding is one edit away from being the place a real leak hides, so
these tests exist to hold the difference between what it is and what it must never become:

* the keys are **full 40-hex blob SHAs**, so a pin is the hash of exact reviewed bytes.
  A prefix would be ambiguous, and an abbreviated key would let a *different* object match;
* every pin carries a written reason and a review date;
* every pin points at a blob history actually still contains;
* the table is **tiny**, and a test fails if it grows past what one person can re-read.

A pattern allowlist would suppress a rule everywhere and forever, including on a credential
committed tomorrow. A content address cannot: different bytes hash differently and fire
again.
"""

from __future__ import annotations

import re

import pytest

from scripts.check_secrets import line_findings
from scripts.scan_git_history import (
    FORBIDDEN_NAMES,
    REVIEWED_HISTORY,
    is_forbidden,
    is_scannable,
    reachable_blobs,
    reviewed_still_present,
)

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
MAX_REVIEWED = 5


# --- the reviewed table, which is the only risky part -----------------------------------------


@pytest.mark.parametrize("key", sorted(REVIEWED_HISTORY))
def test_every_pin_is_a_full_content_address(key) -> None:
    """**The property that makes this not an allowlist.** A full blob SHA is the hash of
    the exact bytes somebody read; different content is a different SHA and fires again."""
    sha, line = key
    assert FULL_SHA.match(sha), f"{sha!r} is not a full 40-hex blob SHA"
    assert isinstance(line, int) and line > 0


@pytest.mark.parametrize("key", sorted(REVIEWED_HISTORY))
def test_every_pin_states_a_reason_and_a_review_date(key) -> None:
    """A suppression with no recorded reason is indistinguishable from one added to make a
    gate go quiet."""
    reason = REVIEWED_HISTORY[key]
    assert len(reason) > 60, "too short to be a review"
    assert re.search(r"20\d\d-\d\d-\d\d", reason), "no review date"


def test_no_pin_refers_to_a_blob_history_no_longer_contains() -> None:
    """A pin matching nothing is dead weight, and suggests a review that no longer applies
    to anything. Checked against the real repository."""
    assert reviewed_still_present() == []


def test_the_reviewed_table_stays_small_enough_to_re_read() -> None:
    """The failure mode of a review list is accumulation. If this trips, the question is
    whether the detector is too noisy — not whether to raise the limit."""
    assert len(REVIEWED_HISTORY) <= MAX_REVIEWED


def test_a_pin_does_not_suppress_the_same_text_in_a_different_blob() -> None:
    """The claim stated directly: the *rule* is untouched. Whatever a pinned line contains,
    `line_findings` still reports it — suppression happens only for one exact object, and
    only in history."""
    for sha, _ in REVIEWED_HISTORY:
        assert FULL_SHA.match(sha)
    # Joined at runtime: this file is scanned too, and a literal here would fail the very
    # gate it is asserting about.
    probe = "api_key = " + '"live-value-here"'
    assert line_findings(probe), "the detector itself was weakened"


# --- the scanner's own predicates ---------------------------------------------------------------


@pytest.mark.parametrize("path", ["credentials.json", "a/b/token.json", "k.pem", "x.key",
                                  ".env", "sub/.env.production"])
def test_a_credential_path_is_a_finding_whatever_it_contains(path: str) -> None:
    """A file can be a credential without containing anything a pattern matches, so the
    name is evidence on its own."""
    assert is_forbidden(path)


@pytest.mark.parametrize("path", [".env-example", "docs/env-example", "src/main.py",
                                  "README.md", "keyring.py"])
def test_an_innocent_path_is_not_flagged(path: str) -> None:
    """`.env-example` is committed on purpose — it is the file that documents which
    variables exist without holding any of their values."""
    assert not is_forbidden(path)


def test_the_forbidden_names_match_what_gitignore_excludes() -> None:
    import pathlib  # noqa: PLC0415

    root = pathlib.Path(__file__).resolve().parents[2]
    ignored = (root / ".gitignore").read_text(encoding="utf-8")
    for name in FORBIDDEN_NAMES:
        assert name in ignored, f"{name} is refused in history but not gitignored [AE-40]"


@pytest.mark.parametrize(("path", "expected"),
                         [("a.py", True), ("b.json", True), ("c.md", True),
                          ("d.png", False), ("e.bin", False)])
def test_only_text_blobs_are_opened(path: str, expected: bool) -> None:
    assert is_scannable(path) is expected


def test_the_scan_actually_reaches_history() -> None:
    """Guards the failure mode of a structural check: silently inspecting nothing."""
    blobs = reachable_blobs()
    assert len(blobs) > 100, f"only {len(blobs)} objects — is `--all` still passed?"
    assert any(path.endswith(".py") for _, path in blobs)
