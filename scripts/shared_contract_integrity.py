"""Exact-byte integrity primitives for the Cop-authored shared contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

MANIFEST_PATH = "docs/contracts/PARITY_MANIFEST.json"
EXACT_PATHS = (
    ".gitattributes",
    "config/game.json",
    "scripts/check_shared_contracts.py",
    "scripts/shared_contract_integrity.py",
)
GLOB_PATHS: tuple[str, ...] = ()
RECURSIVE_ROOTS = (
    "docs/contracts",
    "docs/schemas",
    "tests/fixtures/contracts",
)
EXCLUDED_PATHS = (
    MANIFEST_PATH,
    "docs/schemas/rate-limits.schema.json",
)


class ContractIntegrityError(RuntimeError):
    """Raised when local integrity or optional cross-root comparison fails."""


ContractParityError = ContractIntegrityError


def canonical_bytes(value: object) -> bytes:
    """Serialize manifest data deterministically as UTF-8 JSON with LF."""
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def controlled_paths(root: Path) -> list[str]:
    """Discover controlled files using the checker-owned proposed policy."""
    paths = {path for path in EXACT_PATHS if (root / path).is_file()}
    for pattern in GLOB_PATHS:
        paths.update(_relative(path, root) for path in root.glob(pattern) if path.is_file())
    for relative_root in RECURSIVE_ROOTS:
        directory = root / relative_root
        if directory.is_dir():
            paths.update(
                _relative(path, root) for path in directory.rglob("*") if path.is_file()
            )
    paths.difference_update(EXCLUDED_PATHS)
    return sorted(paths)


def sha256_file(path: Path) -> str:
    """Hash exact file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(root: Path) -> dict[str, object]:
    """Build the deterministic local-integrity manifest."""
    version_path = root / "docs/contracts/CONTRACT_VERSION"
    try:
        contract_version = version_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ContractIntegrityError(f"missing contract version: {version_path}") from exc
    files = [{"path": path, "sha256": sha256_file(root / path)} for path in controlled_paths(root)]
    return {
        "contract_version": contract_version,
        "freeze_status": "proposed_unfrozen",
        "hash_algorithm": "sha256",
        "policy": {
            "exact_paths": list(EXACT_PATHS),
            "glob_paths": list(GLOB_PATHS),
            "recursive_roots": list(RECURSIVE_ROOTS),
            "excluded_paths": list(EXCLUDED_PATHS),
        },
        "files": files,
    }


def _load_manifest(root: Path) -> tuple[bytes, dict[str, object]]:
    path = root / MANIFEST_PATH
    try:
        raw = path.read_bytes()
        stored = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractIntegrityError(f"cannot read parity manifest: {exc}") from exc
    if not isinstance(stored, dict):
        raise ContractIntegrityError("parity manifest root must be an object")
    if raw != canonical_bytes(stored):
        raise ContractIntegrityError("parity manifest is not canonical deterministic JSON")
    return raw, stored


def _file_map(manifest: dict[str, object]) -> dict[str, str]:
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise ContractIntegrityError("manifest has an invalid files list")
    mapped = {
        entry["path"]: entry["sha256"]
        for entry in entries
        if isinstance(entry, dict)
        and isinstance(entry.get("path"), str)
        and isinstance(entry.get("sha256"), str)
    }
    if len(mapped) != len(entries):
        raise ContractIntegrityError("manifest has an invalid or duplicate file entry")
    return mapped


def verify_manifest(root: Path) -> int:
    """Verify local scope, presence, metadata, and every controlled byte hash."""
    _, stored = _load_manifest(root)
    recorded = _file_map(stored)
    discovered = set(controlled_paths(root))
    missing = sorted(set(recorded) - discovered)
    unexpected = sorted(discovered - set(recorded))
    changed = sorted(
        path for path in discovered & set(recorded) if sha256_file(root / path) != recorded[path]
    )
    failures = []
    if missing:
        failures.append(f"missing controlled files: {', '.join(missing)}")
    if unexpected:
        failures.append(f"unexpected controlled files: {', '.join(unexpected)}")
    if changed:
        failures.append(f"changed controlled files: {', '.join(changed)}")
    if not failures and stored != build_manifest(root):
        failures.append("manifest metadata or ordering differs from checker policy")
    if failures:
        raise ContractIntegrityError("; ".join(failures))
    return len(recorded)


def manifest_self_hash(root: Path) -> str:
    """Return the manifest's separately computed exact-byte SHA-256."""
    return sha256_file(root / MANIFEST_PATH)


def compare_repository_roots(source: Path, other: Path) -> int:
    """Read-only compare another root with a verified source bundle."""
    count = verify_manifest(source)
    _, source_manifest = _load_manifest(source)
    recorded = _file_map(source_manifest)
    missing = sorted(path for path in recorded if not (other / path).is_file())
    differing = sorted(
        path
        for path in recorded
        if (other / path).is_file() and sha256_file(other / path) != recorded[path]
    )
    other_paths = set(controlled_paths(other))
    unexpected = sorted(other_paths - set(recorded))
    failures = []
    if missing:
        failures.append(f"comparison root missing paths: {', '.join(missing)}")
    if unexpected:
        failures.append(f"comparison root has unexpected paths: {', '.join(unexpected)}")
    if differing:
        failures.append(f"comparison root differs at: {', '.join(differing)}")
    other_manifest = other / MANIFEST_PATH
    if not other_manifest.is_file():
        failures.append(f"comparison root missing manifest: {MANIFEST_PATH}")
    elif manifest_self_hash(source) != manifest_self_hash(other):
        failures.append("manifest exact bytes differ between roots")
    if failures:
        raise ContractIntegrityError("; ".join(failures))
    return count


def write_manifest(root: Path) -> Path:
    """Write the manifest, which remains excluded from its own file list."""
    path = root / MANIFEST_PATH
    path.write_bytes(canonical_bytes(build_manifest(root)))
    return path
