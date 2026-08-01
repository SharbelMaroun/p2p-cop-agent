"""M5-05: the agreed reliability limits, and where they come from.

All four live in the **shared, signed** match object, so both peers are bound to the
same numbers — a peer cannot quietly give itself a longer rope. Appendix F table 19
marks the first three `Minimum` and the watchdog timeout `Negotiation`.

Timing behaviour lives in `test_deadlines.py`.
"""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.services.deadlines import (
    RetryPolicy,
    limits_from_match,
    read_limit,
)
from p2p_cop_agent.services.limits import LimitError

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"


def game() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_the_agreed_limits_come_from_the_controlled_match_object() -> None:
    """Both peers are bound to the same numbers because they are in the signed JSON."""
    assert limits_from_match(game()) == {
        "response_timeout_sec": 30,
        "watchdog_timeout_sec": 60,
        "retry_backoff_sec": 5,
        "max_retries": 3,
    }


def test_the_defaults_match_appendix_f_table_19() -> None:
    """Verified against the book PDF 2026-08-01: 30 / 60 / 5 s / 3."""
    policy = RetryPolicy.from_match({})
    assert (policy.response_timeout_sec, policy.backoff_sec, policy.max_retries) == (30, 5, 3)
    assert policy.attempts == 4


@pytest.mark.parametrize("bad", [-1, True, "30", 1.5])
def test_a_nonsensical_limit_is_refused_rather_than_coerced(bad: object) -> None:
    with pytest.raises(LimitError, match="non-negative integer"):
        read_limit({"network_and_league": {"response_timeout_sec": bad}},
                   "network_and_league", "response_timeout_sec", 30)

