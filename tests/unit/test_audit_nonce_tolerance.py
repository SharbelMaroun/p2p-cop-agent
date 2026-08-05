"""`C-033`: a verifying audit is honest, whatever shape its nonce is.

Appendix E rule 19 is an **iron rule** with no appeal, so a false accusation is as
costly as missing a real one. The book defines the offence narrowly: "Any mismatch
between the **recomputed hash** and the hash declared during the commitment phase proves
that tampering occurred" (`inst/police_thief_p2p_Summary.md:1270`). A nonce of an
unusual length that still reproduces the digest is the opposite of tampering -- it is
proof the peer never changed its move.

This peer used to score such an opponent `TAMPERED`, because generation and verification
shared one 32-hex format check. Generation keeps it; verification does not.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from p2p_cop_agent.protocol.audit import AuditVerdict, audit_reveal
from p2p_cop_agent.protocol.commit import (
    CommitError,
    generate_commitment_nonce,
    move_commit,
    verify_commit,
)

PAYLOAD = {"step": 1, "move": "N", "intent": "truth"}


def _digest(payload: dict, nonce: str) -> str:
    """Recompute a commitment the way any conformant peer would, from scratch."""
    canonical = json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(f"{canonical}|{nonce}".encode()).hexdigest()


def _audit(nonce: str) -> dict:
    return {
        "sender": "thief",
        "records": [{"payload": PAYLOAD, "nonce": nonce, "commit": _digest(PAYLOAD, nonce)}],
        "result_claim": "survival",
    }


@pytest.mark.parametrize(
    ("label", "nonce"),
    [
        ("our own 16-byte convention", "a" * 32),
        ("a 32-byte nonce, secrets.token_hex(32)", "b" * 64),
        ("an 8-byte nonce", "c" * 16),
        ("a 64-byte nonce", "d" * 128),
    ],
)
def test_any_nonce_that_reproduces_its_digest_is_verified(label: str, nonce: str) -> None:
    report = audit_reveal(_audit(nonce))
    assert report.verdict is AuditVerdict.VERIFIED, f"{label} was wrongly refused"


def test_a_digest_that_does_not_reproduce_is_still_tampered() -> None:
    """The rule still bites where the book says it should: on the digest."""
    forged = _audit("a" * 32)
    forged["records"][0]["payload"] = {"step": 1, "move": "S", "intent": "truth"}
    assert audit_reveal(forged).verdict is AuditVerdict.TAMPERED


def test_verification_accepts_a_foreign_nonce_length_directly() -> None:
    long_nonce = "e" * 64
    assert verify_commit(PAYLOAD, long_nonce, _digest(PAYLOAD, long_nonce))


def test_verification_refuses_a_wrong_digest_for_a_foreign_nonce() -> None:
    assert not verify_commit(PAYLOAD, "e" * 64, "0" * 64)


def test_our_own_generation_stays_strict() -> None:
    """We hold ourselves to 32 lowercase hex; we simply do not impose it on others."""
    assert len(generate_commitment_nonce()) == 32
    with pytest.raises(CommitError, match="32 lowercase hexadecimal"):
        move_commit(PAYLOAD, "b" * 64)


def test_a_non_string_nonce_is_refused_rather_than_crashing() -> None:
    assert not verify_commit(PAYLOAD, None, "0" * 64)
    assert not verify_commit(PAYLOAD, 12345, "0" * 64)
