"""`M7-15b`: the access token is refreshed before it expires, never after.

A series runs for about an hour and an access token lasts about an hour, so the report send
at the **end** of a series is the call most likely to meet an expired one — and rule 32 makes
absence of reporting a disqualification of the game points.

Nothing here touches a real credential: the clock and the refresh call are both injected, so
the policy is provable without OAuth. That is also why `M7-15`/`M7-15a` stay unclaimed —
running the consent flow is the operator's action on their own machine.

Two properties get most of the attention, because both fail quietly: the **skew margin**, and
the fact that no message or repr ever carries a token value.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.services.credential_refresh import (
    SKEW_SECONDS,
    CredentialRefreshError,
    TokenState,
    ensure_fresh,
    seconds_until_refresh,
)

NOW = 1_000_000.0
# Valued so this repository's own secret scanner reads it as a placeholder rather than a
# credential assignment. Silencing that finding with an allowlist entry would be the one
# change that lets a real leak hide later.
DUMMY_TOKEN = "dummy-not-a-real-access-token"


def token(seconds_left: float, *, refreshable: bool = True) -> TokenState:
    return TokenState(access_token=DUMMY_TOKEN, expires_at=NOW + seconds_left,
                      has_refresh_token=refreshable)


def test_a_token_with_plenty_of_life_is_not_refreshed() -> None:
    state = token(3600)
    assert ensure_fresh(state, now=NOW, refresh=lambda: token(1)) is state


def test_a_token_inside_the_skew_margin_is_refreshed_before_it_expires() -> None:
    """**The case a naive check misses.** Four seconds of life passes `expires_at > now`,
    then expires mid-request — a 401 on the one call that must not fail."""
    assert ensure_fresh(token(4), now=NOW, refresh=lambda: token(3600)).expires_at == NOW + 3600


def test_the_margin_covers_a_slow_send_and_its_retries() -> None:
    """Named rather than assumed: the send path backs off across retries, so a margin under
    a minute would refresh into the middle of that."""
    assert SKEW_SECONDS >= 60


def test_no_token_at_all_is_obtained_rather_than_refused() -> None:
    """First run after consent. Nothing to refresh, but something to fetch."""
    assert ensure_fresh(None, now=NOW, refresh=lambda: token(3600)).expires_at == NOW + 3600


def test_an_expired_token_with_no_refresh_token_is_refused() -> None:
    """This state needs the operator to re-run consent. Failing silently here is
    indistinguishable from a successful send in a log that only records errors."""
    calls: list[int] = []

    def refresh() -> TokenState:
        calls.append(1)
        return token(3600)

    with pytest.raises(CredentialRefreshError, match="AE-32"):
        ensure_fresh(token(-1, refreshable=False), now=NOW, refresh=refresh)
    assert calls == [], "no refresh was attempted without a refresh token"


def test_a_valid_token_with_no_refresh_token_is_still_used() -> None:
    """Missing a refresh token is not a reason to refuse one that currently works — the
    report can still go out, and the operator can re-consent afterwards."""
    state = token(3600, refreshable=False)
    assert ensure_fresh(state, now=NOW, refresh=lambda: token(1)) is state


def test_a_failing_refresh_is_wrapped_as_a_credential_error() -> None:
    """Wrapped so callers handle one type. The provider's own class is not part of this
    interface and would leak an implementation detail into every caller."""
    def broken() -> TokenState:
        raise ConnectionError("network down")

    with pytest.raises(CredentialRefreshError, match="ConnectionError"):
        ensure_fresh(None, now=NOW, refresh=broken)


def test_a_refresh_returning_an_already_stale_token_stops_rather_than_looping() -> None:
    """**A clock disagreement with the provider would loop forever otherwise** — every
    refresh returns a token our clock calls expired, and we ask again immediately."""
    with pytest.raises(CredentialRefreshError, match="clock disagreement"):
        ensure_fresh(None, now=NOW, refresh=lambda: token(1))


def test_a_refresh_returning_the_wrong_type_is_refused() -> None:
    with pytest.raises(CredentialRefreshError, match="not a TokenState"):
        ensure_fresh(None, now=NOW, refresh=lambda: {"access_token": DUMMY_TOKEN})


def test_seconds_until_refresh_counts_to_the_margin_not_to_expiry() -> None:
    assert seconds_until_refresh(token(3600), NOW) == 3600 - SKEW_SECONDS


def test_an_overdue_token_is_due_now_rather_than_negative() -> None:
    """A negative interval handed to a scheduler becomes a busy loop or a sleep that never
    wakes, and both look like the token simply never refreshed."""
    assert seconds_until_refresh(token(-500), NOW) == 0.0


# --- the token value never leaves ---------------------------------------------------------


def test_the_repr_redacts_the_token() -> None:
    """The realistic leak is a token reaching a log through a debugger repr, not a
    deliberate print."""
    assert DUMMY_TOKEN not in repr(token(3600))
    assert "<redacted>" in repr(token(3600))


def test_the_refusal_messages_carry_no_token_value() -> None:
    with pytest.raises(CredentialRefreshError) as caught:
        ensure_fresh(token(-1, refreshable=False), now=NOW, refresh=lambda: token(3600))
    assert DUMMY_TOKEN not in str(caught.value)


def test_a_wrapped_provider_error_quotes_only_the_exception_type() -> None:
    """A provider error often echoes the request, and the request carries the token."""
    def leaky() -> TokenState:
        raise ValueError(f"bad grant for {DUMMY_TOKEN}")

    with pytest.raises(CredentialRefreshError) as caught:
        ensure_fresh(None, now=NOW, refresh=leaky)
    assert DUMMY_TOKEN not in str(caught.value)
