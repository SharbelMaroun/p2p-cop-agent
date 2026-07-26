"""Tests for deterministic shared-contract byte parity."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.shared_contract_integrity import (
    MANIFEST_PATH,
    ContractIntegrityError,
    build_manifest,
    canonical_bytes,
    compare_repository_roots,
    manifest_self_hash,
    verify_manifest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_manifest_is_deterministic_and_current() -> None:
    first = build_manifest(PROJECT_ROOT)
    second = build_manifest(PROJECT_ROOT)
    raw = (PROJECT_ROOT / MANIFEST_PATH).read_bytes()

    assert first == second
    assert raw == canonical_bytes(first)
    assert verify_manifest(PROJECT_ROOT) == len(first["files"])


def test_changed_bytes_are_detected(contract_copy: Path) -> None:
    path = contract_copy / "config/game.json"
    path.write_bytes(path.read_bytes() + b" ")

    with pytest.raises(ContractIntegrityError, match="changed controlled files: config/game.json"):
        verify_manifest(contract_copy)


def test_missing_controlled_file_is_detected(contract_copy: Path) -> None:
    (contract_copy / "config/rate_limits.json").unlink()

    with pytest.raises(ContractIntegrityError, match="missing controlled files"):
        verify_manifest(contract_copy)


def test_unexpected_controlled_file_is_detected(contract_copy: Path) -> None:
    path = contract_copy / "docs/schemas/unexpected.json"
    path.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ContractIntegrityError, match="unexpected controlled files"):
        verify_manifest(contract_copy)


def test_private_files_are_not_parity_controlled(contract_copy: Path) -> None:
    (contract_copy / "config/game.toml.example").write_text("[local]\n", encoding="utf-8")
    (contract_copy / ".env").write_text("OPTIONAL=dummy\n", encoding="utf-8")

    assert verify_manifest(contract_copy) > 0


def test_manifest_itself_has_no_circular_entry() -> None:
    manifest = json.loads((PROJECT_ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))

    assert MANIFEST_PATH not in {entry["path"] for entry in manifest["files"]}


def test_manifest_self_hash_is_reported_separately() -> None:
    digest = manifest_self_hash(PROJECT_ROOT)

    assert len(digest) == 64
    assert all(character in "0123456789abcdef" for character in digest)


def test_read_only_cross_root_comparison_accepts_exact_copy(contract_copy: Path) -> None:
    assert compare_repository_roots(PROJECT_ROOT, contract_copy) > 0


def test_cross_root_comparison_reports_missing_paths(contract_copy: Path) -> None:
    (contract_copy / "config/rate_limits.json").unlink()

    with pytest.raises(ContractIntegrityError, match="comparison root missing paths"):
        compare_repository_roots(PROJECT_ROOT, contract_copy)


def test_cross_root_comparison_reports_differing_bytes(contract_copy: Path) -> None:
    path = contract_copy / "config/game.json"
    path.write_bytes(path.read_bytes() + b" ")

    with pytest.raises(ContractIntegrityError, match="comparison root differs at: config/game.json"):
        compare_repository_roots(PROJECT_ROOT, contract_copy)
