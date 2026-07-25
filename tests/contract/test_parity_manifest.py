"""Tests for deterministic shared-contract byte parity."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_shared_contracts import (
    MANIFEST_PATH,
    ContractParityError,
    build_manifest,
    canonical_bytes,
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

    with pytest.raises(ContractParityError, match="changed controlled files: config/game.json"):
        verify_manifest(contract_copy)


def test_missing_controlled_file_is_detected(contract_copy: Path) -> None:
    (contract_copy / "config/rate_limits.json").unlink()

    with pytest.raises(ContractParityError, match="missing controlled files"):
        verify_manifest(contract_copy)


def test_unexpected_controlled_file_is_detected(contract_copy: Path) -> None:
    path = contract_copy / "docs/schemas/unexpected.json"
    path.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ContractParityError, match="unexpected controlled files"):
        verify_manifest(contract_copy)


def test_private_files_are_not_parity_controlled(contract_copy: Path) -> None:
    (contract_copy / "config/game.toml.example").write_text("[local]\n", encoding="utf-8")
    (contract_copy / ".env").write_text("OPTIONAL=dummy\n", encoding="utf-8")

    assert verify_manifest(contract_copy) > 0


def test_manifest_itself_has_no_circular_entry() -> None:
    manifest = json.loads((PROJECT_ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))

    assert MANIFEST_PATH not in {entry["path"] for entry in manifest["files"]}
