"""Three-way agreement with an implementation this project did not write.

``test_cross_implementation_vectors`` proves the Cop runtime and the neutral
stub agree, but both reproduce vectors *this project authored*: we chose the
payloads and computed the expected digests. That cannot detect a wrong shared
assumption, only an inconsistent one.

This module pins a record emitted by the reference simulator during a real
match. Reproducing it means the runtime, the independent stub, and a foreign
implementation all produce identical bytes. Appendix E rule 19 scores any audit
mismatch as zero with no appeal, so this is the assertion that matters most for
league play against an unknown classmate.
"""

import hashlib
import json
from pathlib import Path

import pytest

from p2p_cop_agent.protocol.commit import canonical_payload_bytes, move_commit, verify_commit
from tests.conformance import neutral_stub

VECTOR = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "reference_commit_vector.json").read_text(
        encoding="utf-8"
    )
)
PAYLOAD = VECTOR["payload"]
NONCE = VECTOR["nonce"]
COMMIT = VECTOR["commit"]


def test_runtime_reproduces_the_reference_commit() -> None:
    assert move_commit(PAYLOAD, NONCE) == COMMIT


def test_neutral_stub_reproduces_the_reference_commit() -> None:
    assert neutral_stub.commit(PAYLOAD, NONCE) == COMMIT


def test_all_three_implementations_agree() -> None:
    """Cop runtime, this repo's neutral stub, and the reference simulator."""
    assert move_commit(PAYLOAD, NONCE) == neutral_stub.commit(PAYLOAD, NONCE) == COMMIT


def test_verify_accepts_the_reference_record() -> None:
    assert verify_commit(PAYLOAD, NONCE, COMMIT) is True


def test_float_rendering_matches_the_reference() -> None:
    """`6.0` must not collapse to `6`; `31.8` must not gain precision.

    A peer whose serializer renders 6.0 as `6` produces different bytes and a
    different commitment. Same-language tests never surface this.
    """
    canonical = canonical_payload_bytes(PAYLOAD).decode("utf-8")
    assert '"vram_gb":6.0' in canonical
    assert '"ram_gb":31.8' in canonical


def test_the_book_construction_would_not_reproduce_it() -> None:
    """Evidence for `C-019`: the book's Chapter 5.3 sketch is not interoperable.

    The book seals the nonce inside the payload with no delimiter. Against real
    reference data that yields a different digest, so following the book
    literally would fail every cross-peer audit. Disclosed under book p. 5.
    """
    inside = dict(PAYLOAD) | {"nonce": NONCE}
    book_digest = hashlib.sha256(
        json.dumps(inside, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert book_digest != COMMIT


@pytest.mark.parametrize("field", ["step", "model", "code_version", "group_name"])
def test_mutation_breaks_the_commitment(field: str) -> None:
    mutated = dict(PAYLOAD) | {field: "tampered"}
    assert move_commit(mutated, NONCE) != COMMIT
