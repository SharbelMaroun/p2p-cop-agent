"""The pre-game declaration, written after negotiation and locked before play (M5-17f-iii).

**`links` names the four artifacts; `repositories` carries rule 49's four repo URLs.**
Those were one field until `X-06`, which was a conflation rather than a shortcut: the
template's `links` points at `declaration`/`config`/`log`/`result` filenames, while rule
49 requires "four links in the JSON files of the two teams" meaning the two repositories
per group. Both are required; neither substitutes for the other.

The book requires a pre-game declaration "signed and locked cryptographically before
play". This module builds that object from already-agreed, injected sources and
produces its lock -- a plain canonical SHA-256 over the declaration, the same public,
reproducible construction as the config lock (nothing here is secret, so no nonce).

Deliberately the **minimal M5 form**. What M5 owns is the *timing-and-lock* obligation:
a declaration exists after negotiation, complete in the fields both peers can compute
before the first move, and cryptographically locked before it. The full declaration
*artifact* -- its JSON Schema envelope (`_schema`/`schema_version`), file emission, and
email reporting -- is M7 (`M7-02a`, `M7-22`), and the exact ``game_id``/``game_uid``
derivation is M7's to fix; both are **injected** here rather than invented, so pulling
this forward does not pre-empt M7's contract. ``game_ended_at`` is null at lock time
and is M7's to fill and re-lock post-game.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping

from p2p_cop_agent.protocol.commit import canonical_payload_bytes
from p2p_cop_agent.shared.config import JsonObject

DECLARATION_TYPE = "pre_game"
SCHEMA_VERSION = "1.1"
_SHA256 = re.compile(r"[0-9a-f]{64}")
# `:2229` requires "addresses of the MCP server" in the declaration. Rule 39 (Prohibited)
# forbids pushing secrets, so a URL carrying a credential must never reach a committed,
# emailed artifact -- the two requirements meet here and only public URLs survive.
_CREDENTIAL_IN_URL = re.compile(
    r"://[^/@\s]+@"                                       # user:pass@host — the @ is
    #   required, or a plain host:port like 127.0.0.1:8000 is refused as a credential
    r"|[?&][^=&]*(token|key|secret|password|passwd|auth)[^=&]*=",  # a credential in a query parameter
    re.I,
)


class DeclarationError(ValueError):
    """Raised when a pre-game declaration lacks a member it must carry before play."""


def build_declaration(
    *,
    game_id: str,
    game_uid: str,
    our_identity: Mapping[str, object],
    opponent_identity: Mapping[str, object],
    config_sha256: str,
    num_sub_games: int,
    max_tokens_per_game: int,
    started_at: str,
    timezone: str = "UTC",
) -> JsonObject:
    """Assemble the pre-game declaration from injected, already-agreed sources."""
    for name, value in (("game_id", game_id), ("game_uid", game_uid), ("started_at", started_at)):
        if not isinstance(value, str) or not value:
            raise DeclarationError(f"{name} must be a non-empty string")
    if not isinstance(config_sha256, str) or _SHA256.fullmatch(config_sha256) is None:
        raise DeclarationError("config_sha256 must be 64 lowercase hexadecimal characters")
    for name, value in (("num_sub_games", num_sub_games),
                        ("max_tokens_per_game", max_tokens_per_game)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise DeclarationError(f"{name} must be a positive integer")
    # `:2229` wants "details of the hardware, language model"; both are already members
    # of the negotiated identity block, so they are read there rather than passed again --
    # a second source for the same fact is a second thing that can disagree.
    llm_model = our_identity.get("llm_model")
    host_spec = our_identity.get("spec")
    if not isinstance(llm_model, str) or not llm_model:
        raise DeclarationError("our identity must declare llm_model [AE-24]")
    if not isinstance(host_spec, Mapping) or not host_spec:
        raise DeclarationError("our identity must declare its hardware spec [AE-24]")
    groups = [_group(our_identity), _group(opponent_identity)]
    # `X-06`: two different requirements had been collapsed into one field. The template's
    # `links` points at the four ARTIFACT filenames; rule 49's "four links in the JSON
    # files of the two teams" is about REPOSITORY urls. Both are required and they are not
    # the same thing, so they get separate keys.
    repositories = [url for group in groups for url in group["repos"].values()]
    return {
        "_schema": "declaration",
        "schema_version": SCHEMA_VERSION,
        "declaration_type": DECLARATION_TYPE,
        "game_id": game_id,
        "game_uid": game_uid,
        "config_sha256": config_sha256,
        "groups": groups,
        "links": {
            "declaration": f"declaration_{game_id}.json",
            "config": f"config_{game_id}_g<NN>.json",
            "log": f"log_{game_id}_g<NN>.json",
            "result": f"result_{game_id}.json",
        },
        "repositories": repositories,
        "num_sub_games": num_sub_games,
        "max_tokens_per_game": max_tokens_per_game,
        "hardware": dict(host_spec),
        "llm_model": llm_model,
        "timezone": timezone,
        "game_started_at": started_at,
        "game_ended_at": None,
    }


def _group(identity: Mapping[str, object]) -> JsonObject:
    """Project one peer's identity into the declaration's group entry."""
    group_id = identity.get("group_id")
    if not isinstance(group_id, str) or not group_id:
        raise DeclarationError("each group needs a non-empty group_id")
    repos = identity.get("repos")
    if not isinstance(repos, Mapping) or not repos:
        raise DeclarationError(f"group {group_id!r} must carry at least one repo link")
    servers = identity.get("mcp_servers")
    if not isinstance(servers, Mapping) or not servers:
        raise DeclarationError(f"group {group_id!r} must declare its MCP addresses [`:2229`]")
    for role, url in servers.items():
        if not isinstance(url, str) or not url:
            raise DeclarationError(f"group {group_id!r} MCP address {role!r} must be a URL")
        if _CREDENTIAL_IN_URL.search(url):
            raise DeclarationError(
                f"group {group_id!r} MCP address {role!r} carries a credential; the "
                "declaration is committed and emailed, and rule 39 forbids that"
            )
    return {
        "group_id": group_id,
        "members": list(identity.get("members") or []),
        "repos": dict(repos),
        "mcp_servers": dict(servers),
    }


def lock_declaration(declaration: Mapping[str, object]) -> str:
    """Return the declaration's cryptographic lock: a canonical SHA-256, before play.

    Public and reproducible, so both peers and a later auditor derive the same lock
    from the same declaration -- the tamper-evidence the book's "lock it
    cryptographically before play" requires, not a secret.
    """
    return hashlib.sha256(canonical_payload_bytes(dict(declaration))).hexdigest()
