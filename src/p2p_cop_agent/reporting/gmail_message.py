"""Compose the report email: an attachment, and almost nothing else (`M7-16`).

Four Mandatory rules and one Prohibition constrain this message, and between them they
leave very little room:

* **Rule 33** — "Design the game report as a standard JSON data structure. Sanction: the
  code cannot process free text, and the report will be rejected."
* **Rule 34 (Prohibited)** — "Do not send a game completion report in free text; only
  send an attached JSON file. Sanction: a report that is not JSON will be rejected and
  **result in a zero score**."
* **Rule 45** — "Enter a unique **8-character team identification code** without spaces.
  Sanction: organizational failure that will prevent **automatic report assignment** to
  the team."
* **Rule 30** — "Use authorized sending only for the Gmail interface."

So the body is not where the report goes; it is not even a place to be helpful. A polite
covering note is precisely the "free text" rule 34 prohibits, and the sanction is a zero
score rather than a request to resend. The body here is a fixed pointer to the attachment.

**The subject is machine-read, which is why it is generated rather than written.** Rule 45
ties automatic assignment to the eight-character team code, so the code and the `game_id`
both appear in a fixed order. A subject a human composed per game would sort and assign
inconsistently the first time someone was in a hurry.

*The address.* `rmisegal+uoh26finalgame@gmail.com`, on lecturer answer `AF-020`. The book
prints both spellings — `:3040` has `rmisegal`, `:3605-3606` have `rimesegal` — so this is
a confirmed source inconsistency (`C-004`), not a choice, and the ruling settles it.
"""

from __future__ import annotations

import base64
import json
import re
from collections.abc import Mapping
from email.message import EmailMessage

# `AF-020`. Deliberately not read from the shared config: the destination is not
# negotiable with an opponent, and a peer that could move it could silence our reporting.
REPORT_ADDRESS = "rmisegal+uoh26finalgame@gmail.com"
GENERAL_ADDRESS = "rmisegal@gmail.com"
# Rule 30: least privilege. Send only -- no read, no modify.
REQUIRED_SCOPE = "https://www.googleapis.com/auth/gmail.send"
BODY = "Automated game report. The result is the attached JSON file; this body carries no data."
_TEAM_CODE = re.compile(r"[A-Za-z0-9]{8}")


class ReportMessageError(ValueError):
    """Raised when a message would breach a reporting rule if it were sent."""


def report_subject(team_code: str, game_id: str) -> str:
    """Return the machine-stable subject. Rule 45 makes assignment depend on the code."""
    if not isinstance(team_code, str) or _TEAM_CODE.fullmatch(team_code) is None:
        raise ReportMessageError(
            f"team code {team_code!r} must be exactly 8 characters without spaces [AE-45]"
        )
    if not isinstance(game_id, str) or not game_id or " " in game_id:
        raise ReportMessageError("game_id must be a non-empty string without spaces")
    return f"[{team_code}] final-result {game_id}"


def _require_agreed(settlement: Mapping[str, object]) -> None:
    """Refuse to compose a report for a result that was not audited and then agreed.

    Rule 36 puts the comprehensive mutual audit **before** agreement on the JSON result, and
    rule 35 scores a conflicting report 0 for *both* teams. So the expensive mistake is not
    sending a wrong number — it is sending one the opponent contradicts, and an unaudited
    send maximises exactly that.

    `is not True`, never truthiness: a JSON round trip that turned the flag into the string
    `"True"` would satisfy a truthiness check while proving nothing.
    """
    if not isinstance(settlement, Mapping):
        raise ReportMessageError("build_report_message needs the settlement record [AE-36]")
    if settlement.get("state") != "agreed" or settlement.get("audit_passed") is not True:
        raise ReportMessageError(
            f"refusing to compose a report for a settlement in state "
            f"{settlement.get('state')!r} with audit_passed="
            f"{settlement.get('audit_passed')!r}; rule 36 makes the mutual audit a mandatory "
            "condition before agreement, and rule 35 scores a conflicting report 0 for BOTH "
            "teams [AE-35] [AE-36]"
        )


def build_report_message(
    *,
    team_code: str,
    game_id: str,
    result: Mapping[str, object],
    settlement: Mapping[str, object],
    sender: str,
    to: str = REPORT_ADDRESS,
) -> EmailMessage:
    """Assemble the MIME message: fixed body, JSON attachment, generated subject.

    `settlement` is `orchestration.settlement.settlement_record` (`X-09`). Passing it is not
    ceremony: `require_reportable` already refuses a non-agreed settlement, but it is a call
    a caller can forget, and nothing here would have noticed. Rule 36 makes the mutual audit
    "a mandatory condition before agreement on the JSON result", so the ordering belongs in
    the signature rather than in a caller's discipline — the same argument that made
    `agree()` take its audit first.
    """
    _require_agreed(settlement)
    if not isinstance(result, Mapping) or not result:
        raise ReportMessageError("the result artifact is the report; it cannot be empty")
    if result.get("_schema") != "result-report":
        raise ReportMessageError(
            "only the result artifact is the report [AE-33]; refusing to attach "
            f"{result.get('_schema')!r}"
        )
    message = EmailMessage()
    message["To"] = to
    message["From"] = sender
    message["Subject"] = report_subject(team_code, game_id)
    message.set_content(BODY)
    message.add_attachment(
        json.dumps(dict(result), sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8"),
        maintype="application",
        subtype="json",
        filename=f"result_{game_id}.json",
    )
    return message


def encoded_message(message: EmailMessage) -> dict[str, str]:
    """Return the `users().messages().send` body: base64url of the raw MIME (`M7-16c`)."""
    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")}


def attachment_json(message: EmailMessage) -> dict:
    """Read the attachment back — used by tests and by an operator checking a draft.

    Recovering the artifact from the assembled message, rather than trusting the object
    that went in, is the only way to know the attachment survived encoding intact.
    """
    for part in message.iter_attachments():
        if part.get_content_type() == "application/json":
            return json.loads(part.get_payload(decode=True).decode("utf-8"))
    raise ReportMessageError("message carries no JSON attachment [AE-34]")
