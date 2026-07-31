"""Private per-peer configuration: the opponent's address (M5-03f).

Appendix B splits configuration in two. The **shared** match JSON is byte-identical
between the peers, signed, and hashed. The **private** ``config/game.toml`` is
local, never negotiated and never shared: it holds this peer's own port, the
opponent's URL, model choices, and credentials.

Verified against the reference implementation on 2026-07-31: a peer reads
``config/police/game.toml`` or ``config/thief/game.toml`` -- separate directories
per role -- and takes the opponent's address from the ``[network]`` section under
``opponent_url``. Asked directly whether the shared negotiated ``game.json`` ever
carries a URL, port, host, or any network address, the answer was **no**: local
settings must not "leak into the agreement". Book page 131 publishes the same
skeleton, and the shipped ``[network]`` section carries ``my_port``,
``opponent_url``, ``turn_timeout_seconds``, ``poll_interval_seconds``,
``connect_timeout_seconds``, ``retry_interval_seconds``, and
``audit_send_timeout_seconds``.

This module is therefore the only door to an opponent address, and
:func:`assert_no_network_address` is the lock on the other one: it refuses a shared
match object that carries a network address at all `[AE-10]` `[AE-39]` `[ADR-004]`.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path

import tomllib

from p2p_cop_agent.shared.config import JsonObject

NETWORK_SECTION = "network"
OPPONENT_URL_KEY = "opponent_url"
_ALLOWED_SCHEMES = ("http://", "https://")

# Member names that carry a network address and so may live only in private TOML.
PRIVATE_NETWORK_KEYS = frozenset(
    {
        "address",
        "bind_host",
        "bind_port",
        "endpoint",
        "host",
        "hostname",
        "mcp_servers",
        "my_port",
        "opponent_url",
        "port",
        "public_url",
        "tunnel_url",
        "url",
    }
)


class PrivateConfigError(ValueError):
    """Raised when private configuration is missing, malformed, or unusable."""


class SharedConfigLeakError(ValueError):
    """Raised when a shared match object carries a private network address."""


def load_private_config(path: str | Path) -> JsonObject:
    """Load one explicit private TOML path, never a guessed or shared one."""
    config_path = Path(path)
    try:
        with config_path.open("rb") as handle:
            return tomllib.load(handle)
    except OSError as exc:
        raise PrivateConfigError(f"cannot read private config {config_path}: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise PrivateConfigError(f"private config {config_path} is not valid TOML: {exc}") from exc


def opponent_url(config: Mapping[str, object]) -> str:
    """Return ``[network].opponent_url``: the only address this peer may dial."""
    section = config.get(NETWORK_SECTION)
    if not isinstance(section, Mapping):
        raise PrivateConfigError(f"private config has no [{NETWORK_SECTION}] section")
    value = section.get(OPPONENT_URL_KEY)
    if not isinstance(value, str) or not value.strip():
        raise PrivateConfigError(f"[{NETWORK_SECTION}].{OPPONENT_URL_KEY} must be a non-empty string")
    url = value.strip()
    if not url.startswith(_ALLOWED_SCHEMES):
        raise PrivateConfigError(f"[{NETWORK_SECTION}].{OPPONENT_URL_KEY} must be http(s), got {url!r}")
    return url


def load_opponent_url(path: str | Path) -> str:
    """Read the opponent's address from one explicit private TOML path."""
    return opponent_url(load_private_config(path))


def assert_no_network_address(shared: Mapping[str, object]) -> None:
    """Refuse a shared match object that carries any network address.

    Two independent checks, because either alone is evadable: a member *named*
    like an address (``opponent_url``, ``port``, ``host``), and any string value
    that *is* one (anything carrying a URL scheme). The shared object legitimately
    holds timeouts and league counts, so `network_and_league` is not itself
    suspect -- only addresses are.
    """
    for trail, key, value in _walk(shared):
        if key.lower() in PRIVATE_NETWORK_KEYS:
            raise SharedConfigLeakError(
                f"shared match object carries private network member {trail!r}; "
                f"addresses belong only in config/game.toml [{NETWORK_SECTION}]"
            )
        if isinstance(value, str) and "://" in value:
            raise SharedConfigLeakError(
                f"shared match object carries a network address at {trail!r}: {value!r}"
            )


def _walk(node: object, trail: str = "") -> Iterator[tuple[str, str, object]]:
    """Yield ``(dotted path, member name, value)`` for every member of a tree."""
    if isinstance(node, Mapping):
        for key, value in node.items():
            here = f"{trail}.{key}" if trail else str(key)
            yield here, str(key), value
            yield from _walk(value, here)
    elif isinstance(node, Sequence) and not isinstance(node, str | bytes):
        for index, value in enumerate(node):
            here = f"{trail}[{index}]"
            yield here, "", value
            yield from _walk(value, here)
