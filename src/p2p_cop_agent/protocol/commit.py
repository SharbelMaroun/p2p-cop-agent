"""Option-B per-turn commit-reveal — a distinct hash domain.

The per-turn commitment binds a hidden payload to a secret commitment nonce:

    commit = SHA256( canonical_json(payload) + "|" + nonce )

``canonical_json`` uses sorted keys, ``ensure_ascii=False``, compact separators,
and ``allow_nan=False``. This is kept separate from the config hash domains: it
mixes in a commitment nonce and the literal ``"|"`` delimiter, whereas
``config_sha256`` hashes a bare object and ``config_file_sha256`` hashes exact file
bytes. The public ``negotiate.nonce`` challenge is a separate protocol value.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets

DELIMITER = "|"
COMMITMENT_NONCE_BYTES = 16
_COMMITMENT_NONCE_PATTERN = re.compile(r"^[0-9a-f]{32}$")


class CommitError(ValueError):
    """Raised for a non-serializable payload or malformed commitment nonce."""


def canonical_payload_bytes(payload: object) -> bytes:
    """Return the canonical UTF-8 bytes of a commit payload."""
    try:
        text = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise CommitError(f"cannot canonicalize payload: {exc}") from exc
    return text.encode("utf-8")


def generate_commitment_nonce() -> str:
    """Return a fresh secret commitment nonce as 32 lowercase hex characters."""
    return secrets.token_hex(COMMITMENT_NONCE_BYTES)


def _require_commitment_nonce(nonce: object) -> str:
    if not isinstance(nonce, str) or _COMMITMENT_NONCE_PATTERN.fullmatch(nonce) is None:
        raise CommitError("commitment nonce must be 32 lowercase hexadecimal characters")
    return nonce


def move_commit(payload: object, nonce: str) -> str:
    """Return the hash for a payload bound to a validated commitment nonce."""
    valid_nonce = _require_commitment_nonce(nonce)
    suffix = f"{DELIMITER}{valid_nonce}".encode("ascii")
    return hashlib.sha256(canonical_payload_bytes(payload) + suffix).hexdigest()


def verify_commit(payload: object, nonce: str, commit: object) -> bool:
    """Return whether payload and commitment nonce reproduce a claimed hash."""
    if not isinstance(commit, str):
        return False
    try:
        expected = move_commit(payload, nonce)
    except CommitError:
        return False
    return hmac.compare_digest(expected, commit)
