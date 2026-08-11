"""Stay reachable after the last move, so the opponent's audit is not a 502 (`M7-19b`).

**Mirrors the companion Thief's `adapters/post_match.py`, for a defect this side had not yet
been punished for.** On 2026-08-11 the Thief played group `uoh-ay26`, survived all 35 steps,
wrote its log and exited. Their Cop's `submit_audit` arrived a moment later, met a live tunnel
with no process behind it, and they recorded:

    Opponent unreachable mid-match -- resolving as technical loss:
    submit_audit timed out: ... Server error '502 Bad Gateway'

Their artifact said `technical_loss`, ours said `survival`, and rule 35 scores conflicting
reports **0/0 for both**. A clean win became nothing.

**This repository had the identical shape** -- `write_match_log` then `return result`, with no
window in which an opponent Thief's audit could land. It had never cost a game only because
every Police-role game so far ended with *us* submitting the audit, so the missing window was
never exercised. The six-sub-game series ends that: this side plays Police in 2/4/6, and the
first opponent Thief that audits after the horizon would have done to us exactly what we did
to them.

**Rule 36 is why this is mandatory rather than courteous.** The mutual audit is "a mandatory
condition before agreement", and an agreement needs two peers present. A peer that stops
listening the instant its own result is decided can never satisfy it.

**Bounded, because the opposite failure is ours too.** An opponent may legitimately never
audit -- it may have crashed, or simply not implement the exchange. Waiting forever converts
their fault into our hang, and rule 6 makes a peer frozen on another's silence a technical
loss. So the window closes, and its expiry is an ordinary outcome we report rather than an
error we raise.

**Detected from the `Delivery` list rather than peer state.** This repository's `InboundPeer`
verifies an audit and returns `OK` without retaining it (the companion keeps an
`audits_verified` list). `drain` already reports every validated message and its verdict, so
the arrival is read from there -- no new state on the peer, and a rejected audit correctly
does not count as one received.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

DEFAULT_AUDIT_WINDOW = 60.0
POLL_INTERVAL = 0.5
AUDIT_TOOL = "submit_audit"


def audit_window_seconds(private: Mapping[str, object] | None,
                         default: float = DEFAULT_AUDIT_WINDOW) -> float:
    """Read `[network].audit_send_timeout_seconds`, the budget for one audit exchange.

    A `bool` is refused explicitly: `True` is an `int` in Python, and a one-second audit
    window would silently reproduce the very failure this module exists to prevent.
    """
    network = private.get("network") if isinstance(private, Mapping) else None
    value = network.get("audit_send_timeout_seconds") if isinstance(network, Mapping) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return float(default)
    return float(value)


def _has_audit(deliveries: Sequence[Any] | None) -> bool:
    """Whether a batch of drained messages contains an **accepted** opponent audit."""
    return any(getattr(item, "tool", None) == AUDIT_TOOL and getattr(item, "accepted", False)
               for item in (deliveries or ()))


def await_opponent_audit(
    *,
    drain: Callable[[], Sequence[Any]],
    clock: Callable[[], float],
    sleep: Callable[[float], None],
    timeout: float,
    poll_interval: float = POLL_INTERVAL,
) -> bool:
    """Keep draining until an opponent audit is accepted or the window closes.

    Returns whether one arrived. `drain` is injected rather than the inboxes themselves, so a
    test drives this without a socket -- the same injection `readiness` and the watchdog use.
    The mailbox is already serving in the background; nothing is re-bound here. All this does
    is refuse to let the process exit while the opponent may still be talking.
    """
    if timeout <= 0:
        return _has_audit(drain())
    deadline = clock() + timeout
    while True:
        if _has_audit(drain()):
            return True
        if clock() >= deadline:
            return False
        sleep(min(poll_interval, max(0.0, deadline - clock())))
