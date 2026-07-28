"""Tests for the Option-B move/negotiation commit domain."""

import hashlib
import json
from pathlib import Path

import pytest

from p2p_cop_agent.protocol.commit import (
    CommitError,
    canonical_payload_bytes,
    generate_nonce,
    move_commit,
    verify_commit,
)

VECTORS = (
    Path(__file__).resolve().parents[2]
    / "shared_contract"
    / "vectors"
    / "move-commit.vectors.json"
)


def load_vectors() -> list[dict]:
    data = json.loads(VECTORS.read_text(encoding="utf-8"))
    return data["vectors"]


@pytest.mark.parametrize("vector", load_vectors(), ids=lambda v: v["name"])
def test_move_commit_reproduces_recorded_vectors(vector: dict) -> None:
    assert move_commit(vector["payload"], vector["nonce"]) == vector["commit"]


def test_commit_uses_pipe_delimiter_and_utf8() -> None:
    payload = {"hint": "שלום", "step": 2}
    nonce = "abcdefabcdefabcdefabcdefabcdefab"
    manual = hashlib.sha256(canonical_payload_bytes(payload) + b"|" + nonce.encode()).hexdigest()
    assert move_commit(payload, nonce) == manual


def test_key_order_does_not_change_the_commit() -> None:
    nonce = "0" * 32
    assert move_commit({"x": 1, "y": 2}, nonce) == move_commit({"y": 2, "x": 1}, nonce)


def test_array_order_changes_the_commit() -> None:
    nonce = "0" * 32
    assert move_commit({"a": [1, 2]}, nonce) != move_commit({"a": [2, 1]}, nonce)


def test_field_mutation_changes_the_commit() -> None:
    nonce = "0" * 32
    assert move_commit({"move": "N"}, nonce) != move_commit({"move": "S"}, nonce)


def test_wrong_nonce_changes_the_commit() -> None:
    payload = {"move": "N"}
    assert move_commit(payload, "0" * 32) != move_commit(payload, "1" * 32)


@pytest.mark.parametrize("bad", ["", "0" * 31, "0" * 33, "ABCDEF0123456789ABCDEF0123456789", "xyz"])
def test_move_commit_rejects_malformed_nonce(bad: str) -> None:
    with pytest.raises(CommitError, match="32 lowercase hexadecimal"):
        move_commit({"move": "N"}, bad)


def test_move_commit_rejects_non_string_nonce() -> None:
    with pytest.raises(CommitError, match="32 lowercase hexadecimal"):
        move_commit({"move": "N"}, 123)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_canonicalization_rejects_non_finite_numbers(bad: float) -> None:
    with pytest.raises(CommitError, match="cannot canonicalize"):
        canonical_payload_bytes({"x": bad})


def test_generate_nonce_is_32_hex_and_varies() -> None:
    first = generate_nonce()
    assert len(first) == 32
    assert all(ch in "0123456789abcdef" for ch in first)
    assert first != generate_nonce()


def test_verify_commit_accepts_matching_and_rejects_mutations() -> None:
    payload = {"move": "E", "step": 4}
    nonce = generate_nonce()
    commit = move_commit(payload, nonce)
    assert verify_commit(payload, nonce, commit) is True
    assert verify_commit({"move": "W", "step": 4}, nonce, commit) is False
    assert verify_commit(payload, "0" * 32, commit) is False
    assert verify_commit(payload, nonce, 123) is False
    assert verify_commit(payload, "not-a-valid-nonce", commit) is False
