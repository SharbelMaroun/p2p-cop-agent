"""Fixtures for isolated shared-contract mutation tests."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def contract_copy(tmp_path: Path) -> Path:
    """Copy only files needed to validate and parity-check the shared bundle."""
    for relative in ("config", "docs/contracts", "docs/schemas", "tests/fixtures/contracts"):
        shutil.copytree(PROJECT_ROOT / relative, tmp_path / relative)
    (tmp_path / "scripts").mkdir()
    for filename in ("check_shared_contracts.py", "shared_contract_integrity.py"):
        shutil.copy2(PROJECT_ROOT / "scripts" / filename, tmp_path / "scripts" / filename)
    shutil.copy2(PROJECT_ROOT / ".gitattributes", tmp_path / ".gitattributes")
    return tmp_path


def read_json(path: Path) -> dict[str, object]:
    """Read a mutable JSON object for a mutation test."""
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def write_json(path: Path, value: object) -> None:
    """Write deterministic JSON for a mutation test."""
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
