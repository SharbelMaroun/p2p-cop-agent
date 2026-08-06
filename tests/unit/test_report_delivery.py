"""`M7-17`, `M7-15c`: the report leaves once, or loudly not at all.

`M7-17`'s condition is "no failure mode silently loses a report", and rule 32 (Mandatory)
gives the stakes: "absence of reporting **disqualifies the game points**". A send that
fails quietly costs the game as surely as never trying.

Three failures, three answers. A **429** retries with backoff — Appendix F table 19 makes
the delay a `Minimum` of 5s and attempts a `Minimum` of 3, floors to honour rather than
values to tune down. A **permanent failure** raises, because there is no useful fallback.
A **second send** is refused: rule 35 scores a conflicting report 0 for *both* teams, and
two sends for one game is the easiest way to produce one by accident.

`test_gmail_report.py` carries the composition half.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from p2p_cop_agent.reporting.send_report import (
    MIN_RETRY_ATTEMPTS,
    MIN_RETRY_BACKOFF_SECONDS,
    ReportAlreadySentError,
    ReportNotSentError,
    ReportSender,
)


def _sender(tmp_path: Path, **kw) -> ReportSender:
    credential = tmp_path / "token.json"
    credential.write_text("{}", encoding="utf-8")
    return ReportSender(credential_path=credential, **kw)


def test_a_throttle_backs_off_and_then_succeeds(tmp_path: Path) -> None:
    """`M7-17a`. Appendix F table 19 makes the delay a `Minimum` of 5s and attempts a
    `Minimum` of 3 — floors to honour, not values to tune down."""
    slept: list[float] = []
    attempts = {"n": 0}

    def transmit() -> str:
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("429")
        return "ok"

    outcome = _sender(tmp_path).send(
        game_id="g1", transmit=transmit, sleep=slept.append, status_of=lambda e: 429,
    )
    assert outcome.attempts == 3 and outcome.response == "ok"
    assert slept == [MIN_RETRY_BACKOFF_SECONDS, MIN_RETRY_BACKOFF_SECONDS * 2]


def test_a_non_throttle_error_is_not_retried(tmp_path: Path) -> None:
    """Retrying a 400 just spends quota on a request that will fail identically."""
    slept: list[float] = []
    with pytest.raises(ReportNotSentError):
        _sender(tmp_path).send(
            game_id="g1", transmit=lambda: (_ for _ in ()).throw(RuntimeError("400")),
            sleep=slept.append, status_of=lambda e: 400,
        )
    assert slept == []


def test_a_permanent_failure_raises_loudly(tmp_path: Path) -> None:
    """`M7-17b`. Rule 32: "absence of reporting disqualifies the game points", so there is
    no useful fallback — a caller that could quietly continue would turn a lost game into
    a silent one."""
    with pytest.raises(ReportNotSentError, match="was NOT reported"):
        _sender(tmp_path).send(
            game_id="g1", transmit=lambda: (_ for _ in ()).throw(RuntimeError("429")),
            sleep=lambda _s: None, status_of=lambda e: 429,
        )


def test_a_second_send_for_one_game_is_refused(tmp_path: Path) -> None:
    """`M7-17c`. Rule 35: a conflicting report scores **0 for both teams**, and two sends
    for one game is the easiest way to produce one by accident."""
    sender = _sender(tmp_path)
    sender.send(game_id="g1", transmit=lambda: "ok", sleep=lambda _s: None, status_of=lambda e: None)
    with pytest.raises(ReportAlreadySentError, match="0 for BOTH teams"):
        sender.send(game_id="g1", transmit=lambda: "ok", sleep=lambda _s: None,
                    status_of=lambda e: None)


def test_a_missing_credential_fails_closed(tmp_path: Path) -> None:
    """`M7-15c`. A skipped report looks identical to a successful one in a log that only
    records errors, which is exactly why this must raise."""
    with pytest.raises(ReportNotSentError, match="refusing to skip"):
        ReportSender(credential_path=tmp_path / "absent.json").send(
            game_id="g1", transmit=lambda: "ok", sleep=lambda _s: None, status_of=lambda e: None,
        )


def test_retry_settings_below_the_appendix_f_floors_are_refused() -> None:
    with pytest.raises(ValueError, match="MINIMUM"):
        ReportSender(max_attempts=MIN_RETRY_ATTEMPTS - 1)
    with pytest.raises(ValueError, match="MINIMUM"):
        ReportSender(backoff_seconds=1.0)
