"""Reading an agreed numeric limit from the shared, signed match object.

Shared infrastructure, deliberately **below** the subsystem line. The deadline
tracker, the watchdog, and the gatekeeper all read their bounds from the same signed
match object, and Appendix E rule 3 forbids one subsystem referencing another
directly (M5-08b). So the reader and the key/default constants live here, in a
neutral module none of them owns, and each subsystem depends only on this rather than
on a sibling. Every default is the Appendix F value `[AF-t19]`.
"""

from __future__ import annotations

from collections.abc import Mapping

# Shared-config location of each limit, and its Appendix F default.
RESPONSE_TIMEOUT = ("network_and_league", "response_timeout_sec", 30)
WATCHDOG_TIMEOUT = ("network_and_league", "watchdog_timeout_sec", 60)
RETRY_BACKOFF = ("rate_limiter_gatekeeper", "retry_backoff_sec", 5)
MAX_RETRIES = ("rate_limiter_gatekeeper", "max_retries", 3)


class LimitError(ValueError):
    """Raised when an agreed limit is present but malformed."""


def read_limit(game: Mapping[str, object], section: str, key: str, default: int) -> int:
    """Return one agreed numeric limit, falling back to the Appendix F default."""
    block = game.get(section)
    value = block.get(key) if isinstance(block, Mapping) else None
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LimitError(f"{section}.{key} must be a non-negative integer, got {value!r}")
    return value
