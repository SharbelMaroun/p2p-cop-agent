"""`M6-14` / `M6-14b`: the strategy PRDs still describe the code that ships.

`PRD_scent_belief.md` and `PRD_strategy.md` are what a grader reads to learn what this
agent does, and they carry **numbers** — a locked SHA-256 digest, the canonical record that
produced it, the emission profile, the belief floor, the trust rate. Prose containing
numbers is the most reliably wrong kind of documentation: the code moves, the paragraph
still reads as current, and nobody notices because it is still a fluent sentence.

`M6-14b` asks specifically for "the exact bytes that were locked". Documenting a digest is
only worth something if the digest is *this* build's; a stale one is worse than none, because
an opponent comparing locks would trust the document and be refused by the code.

The digest is the load-bearing assertion here. Rule 23's sanction is cancellation of the
game for deviating from the scent formula, and the digest is the whole mechanism by which a
deviation is detected — so a document quoting a digest that no longer matches would send an
opponent to negotiate against a model we do not run.

The check is deliberately narrow: it pins values that must agree with the code, not the
prose that explains them. A test asserting whole paragraphs would fail on every rewording and
be deleted within a week.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from p2p_cop_agent.strategy import scent
from p2p_cop_agent.strategy.belief import DEFAULT_LIKELIHOOD_FLOOR
from p2p_cop_agent.strategy.hint_consumption import TRUST_UPDATE_RATE
from p2p_cop_agent.strategy.scent_lock import scent_model_hash, scent_model_record
from p2p_cop_agent.strategy.trust import NEUTRAL_SUPPORT, expected_fresh_scent

DOCS = Path(__file__).resolve().parents[2] / "docs"
SCENT_BELIEF = (DOCS / "PRD_scent_belief.md").read_text(encoding="utf-8")
STRATEGY = (DOCS / "PRD_strategy.md").read_text(encoding="utf-8")


def test_the_documented_digest_is_this_builds_digest() -> None:
    """**`M6-14b`.** A stale digest here is worse than no digest: an opponent would
    negotiate against a model we do not run, and rule 23 cancels the game for the
    deviation that would then be detected."""
    digests = set(re.findall(r"\b[0-9a-f]{64}\b", SCENT_BELIEF))
    assert scent_model_hash() in digests, (
        f"PRD_scent_belief.md documents {sorted(digests)}, but this build locks "
        f"{scent_model_hash()}. Update the PRD, or find out what changed the model")


@pytest.mark.parametrize("member", sorted(scent_model_record()))
def test_every_member_of_the_locked_record_is_named_in_the_prd(member: str) -> None:
    """The record shape *is* the interop contract — two peers agree only because their
    member names and order match — so a member added in code and not in the document is a
    silent contract revision."""
    assert f"`{member}`" in SCENT_BELIEF or member in SCENT_BELIEF, (
        f"the locked record contains {member!r}, which PRD_scent_belief.md does not mention")


def test_the_documented_constants_are_the_live_ones() -> None:
    """Each of these appears as a bare number in the PRDs, where nothing ties it to the
    constant it claims to report."""
    for value, label in (
        (scent.CENTER_INTENSITY, "centre intensity"),
        (scent.DECAY_RATE, "decay"),
        (DEFAULT_LIKELIHOOD_FLOOR, "likelihood floor"),
        (TRUST_UPDATE_RATE, "trust rate"),
        (NEUTRAL_SUPPORT, "neutral support"),
    ):
        assert str(value) in SCENT_BELIEF, f"{label} {value} is not documented"


def test_the_expected_fresh_trail_is_documented_as_derived_not_typed() -> None:
    """The book's `0.81` must be shown as a product of the locked constants. Written as a
    literal it would survive a negotiated change to either one and quietly disagree with
    the field it is compared against."""
    assert "CENTER_INTENSITY * (1 - DECAY_RATE)" in SCENT_BELIEF
    assert abs(expected_fresh_scent() - 0.81) < 1e-9


def test_the_field_size_and_profile_classes_are_documented() -> None:
    assert str(scent.FIELD_SIZE) in SCENT_BELIEF
    for tau in sorted(set(scent.DOCUMENTED_EMISSION.values())):
        assert str(tau) in SCENT_BELIEF, f"emission class {tau} is undocumented"


def test_the_strategy_prd_still_describes_the_shipped_arms() -> None:
    """`M6-14`. The measured table names three arms; a renamed or dropped arm would leave
    the reported capture rates attached to something that no longer exists."""
    for arm in ("blind", "belief", "oracle"):
        assert f"`{arm}`" in STRATEGY


def test_the_checks_are_not_vacuous() -> None:
    """The failure mode of a document test is matching against an empty document."""
    assert len(SCENT_BELIEF) > 2000 and len(STRATEGY) > 2000
    assert "0000000000000000000000000000000000000000000000000000000000000000" not in SCENT_BELIEF
