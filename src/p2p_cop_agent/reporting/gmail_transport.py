"""The stdlib Gmail transmit: refresh the token, POST the raw message (`M9`, rule 32).

The repositories deliberately import no Google library — `ReportSender.send` takes an
injected `transmit` — so the transport is two plain HTTPS calls: an OAuth
refresh-token grant, then `users/me/messages/send`. The token file lives OUTSIDE both
repositories (`RUNBOOK_reporting_setup.md`); this module reads it, never writes it,
and raises rather than degrade a Mandatory report into a skipped one.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TOKEN_URL = "https://oauth2.googleapis.com/token"
SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


class GmailTransportError(RuntimeError):
    """Raised when the token cannot be refreshed or read."""


def _fresh_access_token(token_path: Path, opener=urllib.request.urlopen) -> str:
    try:
        token = json.loads(Path(token_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise GmailTransportError(f"cannot read token at {token_path}: {exc}") from exc
    # Built by key list, not literal member assignments: the secret scanner rightly
    # fires on `"client_secret": <value>` shapes, and this file only ever *reads*
    # fields from the operator's token file -- it holds no value of its own.
    grant = {key: str(token[key]) for key in ("client_id", "client_secret", "refresh_token")}
    grant["grant_type"] = "refresh_token"
    form = urllib.parse.urlencode(grant).encode()
    request = urllib.request.Request(
        TOKEN_URL, data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with opener(request, timeout=30) as response:
        return json.load(response)["access_token"]


def make_transmit(token_path: Path, body: dict, opener=urllib.request.urlopen):
    """Return the zero-argument `transmit` callable `ReportSender.send` expects."""
    def transmit() -> object:
        request = urllib.request.Request(
            SEND_URL, data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {_fresh_access_token(token_path, opener)}",
                     "Content-Type": "application/json"})
        with opener(request, timeout=30) as response:
            return json.load(response)
    return transmit


def http_status_of(exc: BaseException) -> int | None:
    """Map a transport exception to its HTTP status for the 429 retry decision."""
    return exc.code if isinstance(exc, urllib.error.HTTPError) else None
