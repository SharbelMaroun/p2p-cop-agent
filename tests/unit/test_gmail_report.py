"""`M7-05`, `M7-16`, `M7-17`, `M7-15c`: the report leaves once, correctly, or loudly not at all.

The sanctions here are unusually blunt, which is why every check refuses rather than warns:

* Rule 32 (Mandatory) — "absence of reporting **disqualifies the game points**".
* Rule 34 (Prohibited) — free text instead of an attached JSON file "will be rejected and
  **result in a zero score**".
* Rule 35 (Mandatory) — a conflicting report scores **0 for both teams**, which is what
  makes a duplicate send a P0 rather than an untidiness.
* Rule 45 (Mandatory) — the 8-character team code drives **automatic report assignment**.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.reporting.gmail_message import (
    GENERAL_ADDRESS,
    REPORT_ADDRESS,
    REQUIRED_SCOPE,
    ReportMessageError,
    attachment_json,
    build_report_message,
    encoded_message,
    report_subject,
)

TEAM = "sharNamr"
RESULT = {"_schema": "result-report", "game_id": "g1", "final_result": {"winner": "cop"}}


# `X-09`: the audited-and-agreed settlement is now a required argument rather than a
# caller's discipline. This is the shape `orchestration.settlement.settlement_record`
# produces, so the fixture and the producer cannot drift into disagreeing about key names.
AGREED = {"state": "agreed", "our_outcome": "capture", "their_outcome": "capture",
          "audit_passed": True, "audit_failed_at": None}


def _message(**kw):
    """Build a report message. `settlement` defaults to agreed and is **overridable**, so a
    test can drive the `X-09` refusals through the same path a caller uses."""
    kwargs = {"team_code": TEAM, "game_id": "g1", "result": RESULT,
              "sender": "us@example.com", "settlement": AGREED}
    kwargs.update(kw)
    return build_report_message(**kwargs)


# --- M7-05: the delivery constraints ------------------------------------------------------


def test_the_scope_is_send_only() -> None:
    """Rule 30 (Mandatory): "use authorized sending only", sanction "security breach that
    will lead to code disqualification". No read, no modify."""
    assert REQUIRED_SCOPE.endswith("/gmail.send")
    assert "readonly" not in REQUIRED_SCOPE and "modify" not in REQUIRED_SCOPE


def test_the_report_goes_to_the_confirmed_address() -> None:
    """`AF-020`. The book prints **both** spellings — `:3040` has `rmisegal`, `:3605-3606`
    have `rimesegal` — so this is a confirmed source inconsistency (`C-004`), and the
    lecturer's answer settles it. The general address is a different one and not this."""
    assert REPORT_ADDRESS == "rmisegal+uoh26finalgame@gmail.com"
    assert GENERAL_ADDRESS == "rmisegal@gmail.com"
    assert _message()["To"] == REPORT_ADDRESS


def test_the_json_rides_as_an_attachment_and_survives_encoding() -> None:
    """`M7-16a`/`M7-16c`. Read back **out of the assembled message** rather than trusting
    the object that went in — that is the only way to know it survived intact."""
    message = _message()
    assert attachment_json(message) == RESULT
    assert "raw" in encoded_message(message)


def test_the_body_carries_no_report_data() -> None:
    """Rule 34 (Prohibited). A helpful covering note *is* the free text the rule forbids,
    and the sanction is a zero score rather than a request to resend."""
    body = _message().get_body(preferencelist=("plain",)).get_content()
    assert "winner" not in body and "cop" not in body


def test_only_the_result_artifact_can_be_the_report() -> None:
    """Rule 33: the report is a specific JSON structure. Attaching the log or the config
    would be a well-formed email carrying the wrong document."""
    with pytest.raises(ReportMessageError, match="only the result artifact"):
        _message(result={"_schema": "game-log", "game_id": "g1"})


# --- M7-16b: the subject is machine-read ---------------------------------------------------


def test_the_subject_carries_the_team_code_and_game() -> None:
    """Rule 45 (Mandatory): assignment is automatic and keyed on the 8-character code."""
    assert report_subject(TEAM, "g1") == "[sharNamr] final-result g1"


def test_the_subject_is_deterministic_for_a_game() -> None:
    assert report_subject(TEAM, "g1") == report_subject(TEAM, "g1")


@pytest.mark.parametrize("bad", ["short", "waytoolongcode", "has spac", ""])
def test_a_team_code_that_is_not_eight_characters_is_refused(bad: str) -> None:
    with pytest.raises(ReportMessageError, match="exactly 8 characters"):
        report_subject(bad, "g1")


# --- X-09: the audit must precede the report -------------------------------------------------


@pytest.mark.parametrize("settlement", [
    {"state": "audit_failed", "audit_passed": False},
    {"state": "conflict", "audit_passed": True},
    {"state": "unanswered", "audit_passed": True},
    {"state": "agreed", "audit_passed": False},
    {"state": "agreed"},
    None,
])
def test_no_settlement_short_of_agreed_can_be_composed(settlement) -> None:
    """`X-09`. `require_reportable` already refuses these, but it is a call a caller can
    forget and nothing here would have noticed. Rule 36 puts the audit before agreement, so
    the ordering belongs in the signature — the same argument that made `agree()` take its
    audit first.

    `{"state": "agreed", "audit_passed": False}` is the shape that matters: a hand-assembled
    record claiming agreement without the audit that must precede it.
    """
    with pytest.raises(ReportMessageError, match=r"AE-3[56]"):
        _message(settlement=settlement)


@pytest.mark.parametrize("truthy", [1, "yes", "True", [1]])
def test_a_truthy_non_boolean_audit_flag_is_refused(truthy) -> None:
    """`is not True`, not truthiness — a JSON round trip turning the flag into the string
    "True" would otherwise pass while proving nothing."""
    with pytest.raises(ReportMessageError, match="AE-36"):
        _message(settlement={"state": "agreed", "audit_passed": truthy})


def test_the_refusal_names_the_state_so_the_operator_knows_the_remedy() -> None:
    """A conflict needs a human and the lecturer; a failed audit needs the evidence
    preserved. "Refused" alone sends someone to read the source."""
    with pytest.raises(ReportMessageError, match="'conflict'"):
        _message(settlement={"state": "conflict", "audit_passed": True})
