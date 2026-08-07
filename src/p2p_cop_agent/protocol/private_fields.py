"""What may leave this process, per channel (`M8-09b`).

Rule 2 (Prohibited): "Do not share memory or variables between parties at all. Sanction:
**Immediate disqualification due to data leakage**." `:2897` draws the line the rule
implies — "everything that both sides must agree upon is written in JSON; everything that
is private and local is written in TOML" — and `:2901` names what private means: "network
port, choice of strategy models, language mode, LLM settings, email, and group identity".

**The rule is per channel, not global, and that is the whole difficulty.** The same key is
forbidden in one document and mandatory in another:

* `llm_model` is an LLM setting, so it is private — **and the pre-game declaration is
  required to disclose it** (rule 24 and `:2229`). Asked directly, the declaration must
  carry `group_id`, `group_name`, `members`, `repos`, `mcp_servers`, `llm_model`, the
  hardware spec and a `signature`.
* `mcp_servers` is a network detail, so it is private — and a peer that is never told the
  opponent's URL cannot play at all.

A single blanket guard would therefore either refuse a mandatory field or guard nothing.
So each channel declares what it is *required* to disclose, and everything else in a
private class is refused.

**What stays private everywhere**, confirmed against the reference: the LLM `provider`
(as distinct from the model name), the RNG `seed`, the strategy or brain selector, any API
key, the reporting email, and internal deadlines. The distinction between `llm_model` and
`provider` is fine but real — the declaration says *which model*, never *how we reach it*.

**Keys, not values.** An `mcp_servers` URL legitimately contains a port; matching on values
would flag it. Matching on key names keeps the required disclosure legal while still
refusing a bare `port`.
"""

from __future__ import annotations

from collections.abc import Mapping

# `:2901`'s six classes. Grouped rather than flattened so a leak reports *what kind* of
# thing escaped, which is what `M8-09b`'s "leakage vector per private field class" asks for.
PRIVATE_FIELD_CLASSES: dict[str, tuple[str, ...]] = {
    "network": ("port", "my_port", "host", "hostname", "url", "endpoint", "opponent_url",
                "mcp_server", "mcp_servers", "ngrok", "tunnel"),
    "strategy": ("strategy", "brain", "policy", "thief_class", "police_class", "cop_class",
                 "model_selection", "seed", "rng_seed"),
    # `llm_model` belongs here even though the declaration must publish it. It is an LLM
    # setting under `:2901`, and leaving it out would mean the shared config could carry it
    # unnoticed -- which is exactly what the first version of this file allowed.
    "llm": ("llm", "llm_model", "provider", "llm_provider", "api_key", "openai_api_key",
            "anthropic_api_key", "temperature", "step_deadline_seconds"),
    "language": ("language_mode", "verbal_mode", "banter", "trash_talk"),
    "contact": ("email", "gmail", "recipient", "report_to"),
    "credential": ("token", "secret", "credentials", "password", "private_key",
                   "client_secret", "refresh_token"),
}

# What each outbound channel is *required* to disclose, and may therefore keep.
CHANNEL_DISCLOSURES: dict[str, frozenset[str]] = {
    # The signed terms both sides hold byte-identically (rule 11). A private value here is
    # one side's local truth inside a document the other side also signs.
    "shared_config": frozenset(),
    # Asked directly: the declaration must carry exactly these. `llm_model` is disclosed;
    # the `provider` behind it is not.
    "declaration": frozenset({"llm_model", "mcp_servers"}),
    # Commit phase carries only the digest; reveal carries move and hint. Neither needs
    # anything from the private file.
    "turn": frozenset(),
    "audit": frozenset(),
    # Rule 49's four repository links are not private under `:2901` -- group identity is
    # published by design -- so `result` needs no disclosure of its own.
    "result": frozenset(),
}


class PrivateFieldLeakError(ValueError):
    """Raised when a document would carry a private field out of this process."""


def _walk(node: object, path: str = "") -> list[tuple[str, str]]:
    """Every (key, path) pair in a nested document, so a leak nested three deep is found."""
    found: list[tuple[str, str]] = []
    if isinstance(node, Mapping):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            found.append((str(key), here))
            found.extend(_walk(value, here))
    elif isinstance(node, (list, tuple)):
        for index, value in enumerate(node):
            found.extend(_walk(value, f"{path}[{index}]"))
    return found


def private_fields_in(document: object, channel: str) -> list[str]:
    """Return `class:path` for every private field this channel may not disclose.

    Unknown channels are refused rather than defaulted: a new outbound message type must
    state what it discloses, because defaulting to permissive is how a channel ships
    unguarded and defaulting to strict is how a mandatory field gets dropped.
    """
    if channel not in CHANNEL_DISCLOSURES:
        raise PrivateFieldLeakError(
            f"unknown channel {channel!r}; declare its disclosures in CHANNEL_DISCLOSURES"
        )
    allowed = CHANNEL_DISCLOSURES[channel]
    leaks: list[str] = []
    for key, path in _walk(document):
        lowered = key.lower()
        if lowered in allowed:
            continue
        for name, members in PRIVATE_FIELD_CLASSES.items():
            if lowered in members:
                leaks.append(f"{name}:{path}")
                break
    return sorted(set(leaks))


def check_outbound(document: object, channel: str) -> None:
    """Refuse to send a document carrying a private field. Rule 2's sanction is immediate
    disqualification, so this raises rather than filtering — silently stripping a field
    would hide the bug that put it there."""
    leaks = private_fields_in(document, channel)
    if leaks:
        raise PrivateFieldLeakError(
            f"{channel} would carry private field(s) {', '.join(leaks)}; rule 2 sanctions "
            "data leakage with immediate disqualification [AE-2], and `:2901` keeps these "
            "in the private TOML"
        )
