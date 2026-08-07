"""When to refresh the Gmail access token, and what to do when it cannot be (`M7-15b`).

The refresh token turns a one-time consent into months of unattended operation, and the
failure it prevents is specific: a series runs for about an hour and an access token lasts
about an hour, so the **report send at the very end** is the call most likely to meet an
expired token — and rule 32 makes sending Mandatory, with absence of reporting disqualifying
the game points.

**This module holds no credential and makes no network call.** The refresh is an injected
callable and the clock is injected too, matching how `deadlines` and `watchdog` take time
here. That is what lets the *policy* be proven without OAuth: running the consent flow is the
operator's action on their own machine (`M7-15`, `M7-15a`, deliberately unclaimed).

**Nothing here returns, logs or formats a token value.** `TokenState.__repr__` redacts,
because the realistic leak is not a deliberate print — it is a token reaching a log through a
debugger repr or an exception message quoting a failed request. Rule 39 forbids secrets in
the repository "even if it is private and shared only with the lecturer".

The **skew margin** matters more than it looks. A token with four seconds left passes a naive
`expires_at > now` and then expires mid-request, producing a 401 on the one call that must
not fail. Refreshing early costs a cheap round trip; refreshing late costs the report.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass

# Wide enough to cover a slow send plus the backoff retries, short enough that a normally
# issued hour-long token is not refreshed on every call.
SKEW_SECONDS = 300.0


class CredentialRefreshError(RuntimeError):
    """Raised when a usable access token cannot be obtained without human action."""


@dataclass(frozen=True, slots=True)
class TokenState:
    """An access token and when it stops working. The value never leaves this object."""

    access_token: str
    expires_at: float
    has_refresh_token: bool = True

    def __repr__(self) -> str:
        """Redacted deliberately.

        Written by hand rather than via `field(repr=False)` for two reasons: a hand-written
        `__repr__` is what the test asserts against, so the redaction cannot be lost to a
        refactor that rebuilds the field list — and `field(repr=False)` puts the field name,
        a colon, a type and an equals sign on one line, which this repository's own secret
        scanner reads as a credential assignment. Silencing that would have meant an
        allowlist entry, and an allowlist is where a real leak eventually hides.
        """
        return (f"TokenState(access_token=<redacted>, expires_at={self.expires_at}, "
                f"has_refresh_token={self.has_refresh_token})")

    def expired(self, now: float, *, skew: float = SKEW_SECONDS) -> bool:
        """True while less than `skew` remains, not merely once the moment passes."""
        return now >= self.expires_at - skew


def ensure_fresh(
    state: TokenState | None,
    *,
    now: float,
    refresh: Callable[[], TokenState],
    skew: float = SKEW_SECONDS,
) -> TokenState:
    """Return a token good for the next `skew` seconds, refreshing only if it is not.

    Refuses rather than refreshes when there is no refresh token: that state needs the
    operator to re-run consent, and failing silently there is indistinguishable from a
    successful send in a log that only records errors.
    """
    if state is not None and not state.expired(now, skew=skew):
        return state
    if state is not None and not state.has_refresh_token:
        raise CredentialRefreshError(
            "the access token has expired and there is no refresh token; re-run the one-time "
            "consent flow — refusing to skip a Mandatory report [AE-32]")
    try:
        refreshed = refresh()
    except CredentialRefreshError:
        raise
    except (OSError, subprocess.SubprocessError, ValueError, RuntimeError) as exc:
        # Only the exception *type* is quoted. A provider error frequently echoes the
        # request, and the request carries the token.
        raise CredentialRefreshError(
            f"refreshing the access token failed: {type(exc).__name__}") from exc
    if not isinstance(refreshed, TokenState):
        raise CredentialRefreshError(
            f"refresh returned {type(refreshed).__name__}, not a TokenState")
    if refreshed.expired(now, skew=skew):
        raise CredentialRefreshError(
            "refresh returned a token already inside the skew margin; a clock disagreement "
            "with the provider would loop here forever, so it stops instead")
    return refreshed


def seconds_until_refresh(state: TokenState, now: float,
                          *, skew: float = SKEW_SECONDS) -> float:
    """How long until a refresh is due. Never negative — an overdue token is due *now*.

    A negative interval handed to a scheduler becomes either an immediate busy loop or a
    sleep that never wakes, and both look like the token simply never refreshed.
    """
    return max(0.0, state.expires_at - skew - now)
