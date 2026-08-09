"""Bounded re-send of an already-sealed turn over a flaky carrier (M5-14b).

Appendix F table 19 carries ``max_retries`` (3) and ``retry_backoff_sec`` (5) as
**minimum** values, and `services/deadlines.py` states the rule they serve: when a
request fails the system must *"retry or declare a technical loss"*. Until now this
peer only ever did the second half. One dropped HTTPS request — the ordinary
behaviour of a free tunnel, and the carrier both peers actually run on — took
``_deliver`` straight to ``machine.fail()`` and the sub-game to ``TECHNICAL_LOSS``,
with three permitted retries left unused.

**Only a carrier fault is retried.** ``TransportError`` means the exchange did not
happen; re-sending is the correct response. ``PeerRejectionError`` is the opposite —
a *decided game outcome*, the peer refusing our move — and re-submitting it would be
appealing a lost game as though it were a network blip, which `M5-14a` forbids.
``CommitRevealError`` is our own sealing defect and no retry can cure it. Those two
propagate on the first raise. That distinction was already documented in
``turn_loop._deliver`` but inert, because nothing retried; wiring the retry is what
makes it load-bearing.

**The turn is never re-sealed, only re-sent.** ``_deliver`` receives a message the
ledger has already committed to, so every attempt puts identical bytes on the wire and
the commitment hash the audit checks is untouched.

**Duplicate delivery becomes ordinary traffic.** If a request arrives but its
acknowledgement is lost, the retry delivers the same step twice; our own inbox is
idempotent on redelivery (`M5-05e`), and a peer that treats a repeated step as a replay
attack rather than a duplicate would see one. That is the interop cost of the trade,
taken deliberately: a certain loss on every blip is worse than a possible disagreement
with a peer that does not tolerate redelivery.

**The clock is bounded by construction**, which is what keeps the opponent's watchdog
out of this. :func:`~p2p_cop_agent.services.deadlines.attempt` opens a fresh
``response_timeout_sec`` deadline per try and retries *only* while that deadline is
unexpired, so a fast failure (a refused connection, a tunnel 502) costs the backoff and
a slow one — a request that hangs to its own timeout — is not retried at all. At the
Appendix F values the worst fast-fail path is 4 attempts and 3 backoffs, about 15 s,
well inside the 60 s watchdog.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field

from p2p_cop_agent.adapters.fastmcp_client import TransportError
from p2p_cop_agent.services.deadlines import RetryPolicy, attempt
from p2p_cop_agent.shared.config import JsonObject

# The only failure a re-send can cure: the exchange never happened.
RETRY_ON: tuple[type[BaseException], ...] = (TransportError,)


@dataclass(frozen=True, slots=True)
class DeliveryRetry:
    """The bounded re-send policy, with its clock and sleep injected for tests."""

    policy: RetryPolicy
    clock: Callable[[], float] = field(default=time.monotonic)
    sleep: Callable[[float], None] = field(default=time.sleep)

    @classmethod
    def from_match(cls, game: JsonObject) -> DeliveryRetry:
        """Read the agreed retry limits out of the shared, signed match object."""
        return cls(RetryPolicy.from_match(game))


def send_turn(
    send: Callable[[JsonObject], object],
    message: JsonObject,
    retry: DeliveryRetry | None,
) -> object:
    """Deliver ``message``, re-sending it on a carrier fault while attempts remain.

    ``retry`` of ``None`` keeps the single-attempt behaviour, so a caller that has no
    match object (and every existing test) is unchanged.
    """
    if retry is None:
        return send(message)
    return attempt(
        lambda: send(message),
        retry.policy,
        clock=retry.clock,
        sleep=retry.sleep,
        retry_on=RETRY_ON,
    )
