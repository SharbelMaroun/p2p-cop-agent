"""Deadline tracking and bounded retry (M5-05a, M5-05b, M5-13).

Book section 8.4.1 is unusually direct about this, and its boxed note is the whole
design: *"Missing a Deadline is a Failure, Not Patience."* Every request carries a
timestamp and an expiry; when the expiry passes the system must **retry or declare a
technical loss and clear the queue cleanly** — never keep waiting. Leaving a request
pending without an expiry is named as the direct path to freezing.

So the rule here is that waiting is always bounded, and running out of attempts is a
decision rather than a hang.

**Where the numbers come from.** All four live in the *shared, signed* match object,
so both peers are bound to the same limits — confirmed against the reference
2026-08-01, which reads them from exactly these keys:

===========================  ==========================================  =======
Meaning                      Key in the shared match object              Default
===========================  ==========================================  =======
request expiry               ``network_and_league.response_timeout_sec``  30
wait before retrying         ``rate_limiter_gatekeeper.retry_backoff_sec`` 5
attempts after the first     ``rate_limiter_gatekeeper.max_retries``      3
watchdog trip                ``network_and_league.watchdog_timeout_sec``  60
===========================  ==========================================  =======

Appendix F table 19 marks the first three `Minimum` — they may be made stricter but
never looser — while the watchdog timeout is `Negotiation`. `check_appendix_f` in
`protocol/negotiation.py` owns enforcing that; this module only reads what was agreed.

**Time is injected.** ``now`` is a parameter, never a hidden call to the clock, so a
timeout is tested by passing a number rather than by sleeping.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from p2p_cop_agent.shared.config import JsonObject

# Shared-config location of each limit, and the Appendix F default.
RESPONSE_TIMEOUT = ("network_and_league", "response_timeout_sec", 30)
WATCHDOG_TIMEOUT = ("network_and_league", "watchdog_timeout_sec", 60)
RETRY_BACKOFF = ("rate_limiter_gatekeeper", "retry_backoff_sec", 5)
MAX_RETRIES = ("rate_limiter_gatekeeper", "max_retries", 3)


class DeadlineError(RuntimeError):
    """Raised when a bounded wait ran out: a decision, never a hang."""


def read_limit(game: Mapping[str, object], section: str, key: str, default: int) -> int:
    """Return one agreed numeric limit, falling back to the Appendix F default."""
    block = game.get(section)
    value = block.get(key) if isinstance(block, Mapping) else None
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise DeadlineError(f"{section}.{key} must be a non-negative integer, got {value!r}")
    return value


@dataclass(frozen=True, slots=True)
class Deadline:
    """One request's expiry. Past it, the request has failed."""

    started: float
    expires: float

    @classmethod
    def starting_at(cls, now: float, timeout: float) -> Deadline:
        """Open a deadline of ``timeout`` seconds from ``now``."""
        if timeout <= 0:
            raise DeadlineError(f"timeout must be positive, got {timeout!r}")
        return cls(started=now, expires=now + timeout)

    def expired(self, now: float) -> bool:
        """Return whether the expiry has passed. The boundary itself is expired."""
        return now >= self.expires

    def remaining(self, now: float) -> float:
        """Return seconds left, never negative."""
        return max(0.0, self.expires - now)


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """How many further attempts are allowed, and how long to wait between them."""

    max_retries: int
    backoff_sec: float
    response_timeout_sec: float

    @classmethod
    def from_match(cls, game: Mapping[str, object]) -> RetryPolicy:
        """Read the agreed limits out of the shared, signed match object."""
        return cls(
            max_retries=read_limit(game, *MAX_RETRIES),
            backoff_sec=read_limit(game, *RETRY_BACKOFF),
            response_timeout_sec=read_limit(game, *RESPONSE_TIMEOUT),
        )

    @property
    def attempts(self) -> int:
        """Total tries: the first one plus the permitted retries."""
        return self.max_retries + 1

    def deadline(self, now: float) -> Deadline:
        """Open one request's deadline at ``now``."""
        return Deadline.starting_at(now, self.response_timeout_sec)


def attempt(
    action: Callable[[], object],
    policy: RetryPolicy,
    *,
    clock: Callable[[], float],
    sleep: Callable[[float], None] = lambda _seconds: None,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
) -> object:
    """Run ``action`` under a deadline, retrying a bounded number of times.

    Each attempt gets its own deadline. A retry is taken only while attempts remain
    *and* the clock has not passed the current attempt's expiry; otherwise this
    raises, so the caller can declare a technical loss and clear its queue — the two
    outcomes section 8.4.1 allows. It never returns having silently given up.
    """
    last: BaseException | None = None
    for remaining in range(policy.attempts - 1, -1, -1):
        deadline = policy.deadline(clock())
        try:
            return action()
        except retry_on as exc:
            last = exc
            if remaining == 0:
                break
            if deadline.expired(clock()):
                raise DeadlineError(
                    f"attempt exceeded its {policy.response_timeout_sec}s expiry: {exc}"
                ) from exc
            sleep(policy.backoff_sec)
    raise DeadlineError(
        f"exhausted {policy.attempts} attempts ({policy.max_retries} retries): {last}"
    ) from last


def limits_from_match(game: Mapping[str, object]) -> JsonObject:
    """Return every agreed reliability limit, for logging and the report."""
    return {
        "response_timeout_sec": read_limit(game, *RESPONSE_TIMEOUT),
        "watchdog_timeout_sec": read_limit(game, *WATCHDOG_TIMEOUT),
        "retry_backoff_sec": read_limit(game, *RETRY_BACKOFF),
        "max_retries": read_limit(game, *MAX_RETRIES),
    }
