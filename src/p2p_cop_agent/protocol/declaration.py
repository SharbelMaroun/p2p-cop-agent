"""The pre-game declaration: written after negotiation, locked before the first move.

Two requirements were one field until `X-06`, and the collapse was a conflation rather than
a shortcut. `links` names the four **artifact** filenames; `repositories` carries rule 49's
four **repository** URLs. Both are required and neither substitutes for the other.

The book requires this artifact "signed and locked cryptographically before play". The lock
is a plain canonical SHA-256 over the declaration — public and reproducible, like the config
lock, because nothing here is secret and an auditor must be able to recompute it.

`game_ended_at` is null at lock time by design: the declaration is written before the first
move, so the end time is not knowable when the artifact is created. It is filled and
re-locked post-game.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping

from p2p_cop_agent.protocol.commit import canonical_payload_bytes
from p2p_cop_agent.protocol.declaration_groups import DeclarationError, _group
from p2p_cop_agent.protocol.private_fields import check_outbound
from p2p_cop_agent.reporting.naming import (
    MatchIdentity,
    config_filename,
    declaration_filename,
    log_filename,
    result_filename,
)
from p2p_cop_agent.shared.config import JsonObject

DECLARATION_TYPE = "pre_game"
SCHEMA_VERSION = "1.1"
_SHA256 = re.compile(r"[0-9a-f]{64}")
_COMMIT = re.compile(r"[0-9a-f]{7,40}")


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
    github_commit: str,
    games_played_declaration: Mapping[str, object],
    timezone: str = "UTC",
) -> JsonObject:
    """Assemble the pre-game declaration from injected, already-agreed sources."""
    for name, value in (("game_id", game_id), ("game_uid", game_uid), ("started_at", started_at)):
        if not isinstance(value, str) or not value:
            raise DeclarationError(f"{name} must be a non-empty string")
    if not isinstance(config_sha256, str) or _SHA256.fullmatch(config_sha256) is None:
        raise DeclarationError("config_sha256 must be 64 lowercase hexadecimal characters")
    # Rule 53, p.40/106. Hex-only, not a length floor: the reference ships "unknown",
    # which is exactly seven characters and identifies nothing.
    if not isinstance(github_commit, str) or _COMMIT.fullmatch(github_commit) is None:
        raise DeclarationError(
            "github_commit must be 7-40 lowercase hex characters; rule 53 requires the "
            "commit of the code that plays, and 'unknown' identifies nothing [AE-53]")
    # Rule 37, p.131/275: the count at game start. Rule 38 makes a false one absolute
    # disqualification, so `reporting.league` derives it from emitted result artifacts.
    if not isinstance(games_played_declaration, Mapping) or not games_played_declaration:
        raise DeclarationError(
            "games_played_declaration is required; rule 37 wants the count at the start "
            "of each game and rule 38 disqualifies the project for a false one [AE-37]")
    for name, value in (("num_sub_games", num_sub_games),
                        ("max_tokens_per_game", max_tokens_per_game)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise DeclarationError(f"{name} must be a positive integer")
    # `:2229` wants "details of the hardware, language model". Both are members of the
    # negotiated identity block, so they are read there rather than passed again -- a
    # second source for the same fact is a second thing that can disagree -- and they are
    # emitted **per group** by `_disclosure`, never once for the document (`M7-22f`).
    groups = [_group(our_identity), _group(opponent_identity, ours=False)]
    # `X-06`: two different requirements had been collapsed into one field. The template's
    # `links` points at the four ARTIFACT filenames; rule 49's "four links in the JSON
    # files of the two teams" is about REPOSITORY urls. Both are required and they are not
    # the same thing, so they get separate keys.
    repositories = [url for group in groups for url in group["repos"].values()]
    # Names come from `reporting.naming`, the single source that already derives every
    # filename from one identity. Restating the f-strings here is how the declaration and
    # the files on disk would drift apart without anything noticing.
    _identity = MatchIdentity(game_id=game_id, game_uid=game_uid)
    declaration: JsonObject = {
        "_schema": "declaration",
        "schema_version": SCHEMA_VERSION,
        "declaration_type": DECLARATION_TYPE,
        "game_id": game_id,
        "game_uid": game_uid,
        "config_sha256": config_sha256,
        "github_commit": github_commit,
        "games_played_declaration": dict(games_played_declaration),
        "groups": groups,
        # `M7-02`: **resolved** filenames, never the `g<NN>` pattern the book's naming
        # table writes. `X-04` fixed that pattern in the schema and left this builder
        # emitting the placeholder; the schema's own `links` description carries the
        # full reasoning. Arrays: a series has `num_sub_games` configs and logs.
        "links": {
            "declaration": declaration_filename(_identity),
            "config": [config_filename(_identity, n) for n in range(1, num_sub_games + 1)],
            "log": [log_filename(_identity, n) for n in range(1, num_sub_games + 1)],
            "result": result_filename(_identity),
        },
        "repositories": repositories,
        "num_sub_games": num_sub_games,
        "max_tokens_per_game": max_tokens_per_game,
        "timezone": timezone,
        "game_started_at": started_at,
        "game_ended_at": None,
    }
    # `M8-09b`: refuse to ship a private field. The declaration is the one artifact
    # *required* to disclose `llm_model` and `mcp_servers`, so the check is channel-aware
    # rather than a blanket ban -- see `private_fields.CHANNEL_DISCLOSURES`.
    check_outbound(declaration, "declaration")
    return declaration


def lock_declaration(declaration: Mapping[str, object]) -> str:
    """Return the declaration's cryptographic lock: a canonical SHA-256, before play.

    Public and reproducible, so both peers and a later auditor derive the same lock
    from the same declaration -- the tamper-evidence the book's "lock it
    cryptographically before play" requires, not a secret.
    """
    return hashlib.sha256(canonical_payload_bytes(dict(declaration))).hexdigest()
