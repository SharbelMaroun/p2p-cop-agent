"""`M9-09` / `X-15`: the bundle, and the line between sent and received.

The book's decisive layer of proof is **receipt at the lecturer's address** (p.78/183) — and
a sender cannot observe it; only the recipient can. `M9-09c`'s wording ("record proof that
each report was sent") invites the stronger reading, so the test that matters most here is
that no record ever makes the stronger claim.

The reference stores nothing at all: its sender returns `{status, reason}` for a CLI line
that never reaches the four artifacts.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.reporting.evidence import (
    CountedGame,
    EvidenceBundle,
    EvidenceError,
    SendReceipt,
    archive_is_complete,
    minimums_met,
    missing_evidence,
)

SHA = "b" * 40
PROV = {"github_commit": SHA, "working_tree_clean": True}
FULL = ["declaration_g.json", "config_g_g01.json", "log_g_g01.json", "result_g.json"]


def receipt(gid: str) -> SendReceipt:
    return SendReceipt.from_api_response({"id": f"msg-{gid}"}, game_id=gid, sent_at="t",
                                         recipient="rmisegal+uoh26finalgame@gmail.com")


def bundle(*pairs, receipts: bool = True) -> EvidenceBundle:
    b = EvidenceBundle()
    for gid, opponent in pairs:
        b.add_game(CountedGame(gid, opponent), provenance=PROV)
        if receipts:
            b.add_receipt(receipt(gid))
    return b


def test_a_record_states_it_evidences_acceptance_not_receipt() -> None:
    """**The test this file exists for.** Overstating this in an artifact would be a claim
    the lecturer's own inbox could contradict."""
    assert receipt("g1").as_record()["evidences"] == (
        "API acceptance, not receipt by the lecturer")


@pytest.mark.parametrize("response", [{}, {"id": ""}, {"id": None}, {"id": 7}])
def test_a_response_without_a_usable_id_is_refused(response: dict) -> None:
    with pytest.raises(EvidenceError, match="AE-32"):
        SendReceipt.from_api_response(response, game_id="g", sent_at="t", recipient="r")


def test_a_game_without_a_resolved_commit_is_refused() -> None:
    """The reference hard-codes `"unknown"`, which satisfies every shape check and names
    nothing."""
    with pytest.raises(EvidenceError, match="AE-53"):
        EvidenceBundle().add_game(CountedGame("g1", "rival"),
                                  provenance={"github_commit": "unknown"})


def test_a_second_receipt_for_one_game_is_refused() -> None:
    b = bundle(("g1", "rival"))
    with pytest.raises(EvidenceError, match="BOTH teams"):
        b.add_receipt(receipt("g1"))


def test_a_counted_game_with_no_receipt_is_unreported() -> None:
    assert bundle(("g1", "rival"), receipts=False).unreported() == ("g1",)


def test_every_declared_mismatch_is_reported_in_one_pass() -> None:
    """Rule 38's sanction lands on the project, not the game."""
    b = bundle(("g1", "rival"), ("g2", "other"))
    with pytest.raises(EvidenceError) as caught:
        b.reconcile({"rival": 5, "other": 9})
    assert "rival" in str(caught.value) and "other" in str(caught.value)


def test_matching_declared_counts_pass() -> None:
    bundle(("g1", "rival"), ("g2", "other")).reconcile({"rival": 1, "other": 1})


def test_two_games_against_two_groups_meets_the_minimum() -> None:
    met, why = minimums_met(bundle(("g1", "rival"), ("g2", "other")))
    assert met, why


def test_two_games_against_one_group_does_not() -> None:
    """Rule 52: a repeat game cannot substitute for a second opponent."""
    met, why = minimums_met(bundle(("g1", "rival"), ("g2", "rival")))
    assert not met and "distinct opponent" in why


def test_an_unreported_game_fails_before_the_counting_does() -> None:
    """Played and unreported scores zero, so "minimum met" would be the more misleading
    answer."""
    met, why = minimums_met(bundle(("g1", "rival"), ("g2", "other"), receipts=False))
    assert not met and "AE-32" in why


@pytest.mark.parametrize(("files", "ok"), [(FULL, True), (FULL[:3], False), ([], False)])
def test_an_archive_needs_all_four_kinds(files, ok) -> None:
    assert archive_is_complete(files) is ok


def test_gaps_are_listed_per_game_rather_than_raised() -> None:
    b = EvidenceBundle()
    b.add_game(CountedGame("g1", "rival"), provenance=PROV)
    assert missing_evidence(b, {}) == {"g1": ["archived artifact set", "send receipt"]}
