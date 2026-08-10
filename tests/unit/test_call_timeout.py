"""Every outbound call is capped strictly below the deadline we signed.

Guards the 2026-08-10 addition. ``FastMCPClient`` has always accepted a ``timeout``, but
``serve`` never passed one, so live calls were unbounded. Nothing failed in testing: the
breach is arithmetic, and it only appears when a real peer accepts a push and then goes quiet.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.services.deadlines import RetryPolicy

APPENDIX_F = RetryPolicy(max_retries=3, backoff_sec=5.0, response_timeout_sec=30.0)


def test_cap_is_strictly_under_the_signed_deadline() -> None:
    """The whole purpose: a cap equal to the deadline leaves a retry no room."""
    assert APPENDIX_F.call_timeout_sec < APPENDIX_F.response_timeout_sec


def test_every_permitted_attempt_fits_inside_the_deadline() -> None:
    """`attempts` calls at the cap must not outlive the budget they are drawn from."""
    assert APPENDIX_F.call_timeout_sec * APPENDIX_F.attempts <= APPENDIX_F.response_timeout_sec


@pytest.mark.parametrize("retries", range(0, 6))
def test_cap_stays_legal_for_any_negotiated_retry_count(retries: int) -> None:
    """Opponents negotiate different retry counts; the invariant may not depend on ours."""
    policy = RetryPolicy(max_retries=retries, backoff_sec=5.0, response_timeout_sec=30.0)
    assert 0 < policy.call_timeout_sec < policy.response_timeout_sec
    assert policy.call_timeout_sec * policy.attempts <= policy.response_timeout_sec


def test_cap_scales_with_a_shorter_agreed_deadline() -> None:
    """A peer who signs a tighter deadline must tighten our calls, not just our bookkeeping."""
    tight = RetryPolicy(max_retries=1, backoff_sec=1.0, response_timeout_sec=6.0)
    assert tight.call_timeout_sec == 3.0
