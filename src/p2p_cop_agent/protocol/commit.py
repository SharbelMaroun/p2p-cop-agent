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


def _commit_bytes_hash(payload: object, nonce: str) -> str:
    """Return the digest for a payload and a nonce, with no format opinion.

    The hash construction only; the *policy* about what a well-formed nonce looks like
    belongs to :func:`move_commit`, which is what we send, not to verification, which
    judges what an opponent sent (see :func:`verify_commit`).
    """
    suffix = f"{DELIMITER}{nonce}".encode()
    return hashlib.sha256(canonical_payload_bytes(payload) + suffix).hexdigest()


def move_commit(payload: object, nonce: str) -> str:
    """Return the hash for a payload bound to a validated commitment nonce.

    Generation is strict on purpose: **our** nonce must be 32 lowercase hex, so we
    cannot ship a weak or malformed one. Verification is deliberately not (`C-033`).
    """
    return _commit_bytes_hash(payload, _require_commitment_nonce(nonce))


def verify_commit(payload: object, nonce: object, commit: object) -> bool:
    """Return whether payload and commitment nonce reproduce a claimed hash.

    **The opponent's nonce format is not our business (corrected 2026-08-06).** This
    used to run the same ``_require_commitment_nonce`` check as generation, so a peer
    revealing a longer nonce -- ``secrets.token_hex(32)`` rather than ``(16)`` -- failed
    verification even when its digest reproduced perfectly, and was scored a forger.

    The book does not permit that. It defines the offence precisely: "Any mismatch
    between the **recomputed hash** and the hash declared during the commitment phase
    proves that tampering occurred" (`inst/police_thief_p2p_Summary.md:1270`), and
    Appendix E rule 19 sanctions exactly that mismatch. A nonce of a different length
    that still reproduces the digest is not a mismatch -- it is proof the peer was
    honest. Calling it forgery is both wrong and expensive: rule 19 is an iron rule with
    no appeal, so a false verdict ends a game that was played fairly.

    So verification hashes **whatever it is given**. Our own nonces stay 32 lowercase
    hex (`generate_commitment_nonce`, still enforced on the way out by ``move_commit``);
    what an opponent chose is only ever judged by whether the arithmetic works.
    """
    if not isinstance(commit, str) or not isinstance(nonce, str):
        return False
    try:
        expected = _commit_bytes_hash(payload, nonce)
    except CommitError:
        return False
    return hmac.compare_digest(expected, commit)
