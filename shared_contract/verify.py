"""Role-neutral read-only verifier for the shared contract bundle.

This file is part of the stable bundle and is copied into the opponent repository
byte-for-byte. It imports no Cop or Thief runtime code and never writes any file.
It verifies that every controlled file under the bundle root matches the recorded
hash in ``PARITY_MANIFEST.json`` and that the manifest is canonical. Manifest
generation is a repository-owner operation and lives outside this verifier.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parent
MANIFEST_NAME = "PARITY_MANIFEST.json"
_IGNORED_DIRS = {"__pycache__"}


class ContractVerificationError(RuntimeError):
    """Raised when the bundle does not match its recorded manifest."""


def canonical_manifest_bytes(value: object) -> bytes:
    """Serialize manifest data deterministically as sorted UTF-8 JSON with LF."""
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    """Return the SHA-256 of exact file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def controlled_files(root: Path = BUNDLE_ROOT) -> list[str]:
    """List every controlled bundle file except the manifest, in sorted order."""
    found: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        relative = path.relative_to(root).as_posix()
        if relative == MANIFEST_NAME:
            continue
        found.append(relative)
    return sorted(found)


def build_manifest(root: Path = BUNDLE_ROOT) -> dict[str, object]:
    """Build the deterministic manifest for the bundle at ``root``."""
    version_path = root / "CONTRACT_VERSION"
    try:
        contract_version = version_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ContractVerificationError(f"missing contract version: {version_path}") from exc
    files = [{"path": rel, "sha256": sha256_file(root / rel)} for rel in controlled_files(root)]
    return {
        "contract_version": contract_version,
        "freeze_status": "proposed_unfrozen",
        "hash_algorithm": "sha256",
        "files": files,
    }


def _load_manifest(root: Path) -> dict[str, object]:
    path = root / MANIFEST_NAME
    try:
        raw = path.read_bytes()
        stored = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractVerificationError(f"cannot read manifest: {exc}") from exc
    if not isinstance(stored, dict):
        raise ContractVerificationError("manifest root must be an object")
    if raw != canonical_manifest_bytes(stored):
        raise ContractVerificationError("manifest is not canonical deterministic JSON")
    return stored


def _recorded_hashes(manifest: dict[str, object]) -> dict[str, str]:
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise ContractVerificationError("manifest has an invalid files list")
    mapped = {
        entry["path"]: entry["sha256"]
        for entry in entries
        if isinstance(entry, dict)
        and isinstance(entry.get("path"), str)
        and isinstance(entry.get("sha256"), str)
    }
    if len(mapped) != len(entries):
        raise ContractVerificationError("manifest has an invalid or duplicate file entry")
    return mapped


def verify(root: Path = BUNDLE_ROOT) -> int:
    """Verify presence, scope, canonical form, and every controlled byte hash."""
    stored = _load_manifest(root)
    recorded = _recorded_hashes(stored)
    discovered = set(controlled_files(root))
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
        failures.append("manifest metadata or ordering differs from recomputed manifest")
    if failures:
        raise ContractVerificationError("; ".join(failures))
    return len(recorded)


def manifest_self_hash(root: Path = BUNDLE_ROOT) -> str:
    """Return the manifest's separately computed exact-byte SHA-256."""
    return sha256_file(root / MANIFEST_NAME)


def compare_bundles(source: Path, other: Path) -> int:
    """Read-only compare another bundle root against a verified source bundle."""
    count = verify(source)
    recorded = _recorded_hashes(_load_manifest(source))
    missing = sorted(path for path in recorded if not (other / path).is_file())
    differing = sorted(
        path
        for path in recorded
        if (other / path).is_file() and sha256_file(other / path) != recorded[path]
    )
    failures = []
    if missing:
        failures.append(f"comparison bundle missing paths: {', '.join(missing)}")
    if differing:
        failures.append(f"comparison bundle differs at: {', '.join(differing)}")
    if not (other / MANIFEST_NAME).is_file():
        failures.append(f"comparison bundle missing manifest: {MANIFEST_NAME}")
    elif manifest_self_hash(source) != manifest_self_hash(other):
        failures.append("manifest exact bytes differ between bundles")
    if failures:
        raise ContractVerificationError("; ".join(failures))
    return count


def main(argv: list[str] | None = None) -> int:
    """Verify this bundle and optionally compare with another bundle root."""
    args = list(sys.argv[1:] if argv is None else argv)
    compare_root: Path | None = None
    if args and args[0] == "--compare-root" and len(args) == 2:
        compare_root = Path(args[1])
    elif args:
        print("usage: verify.py [--compare-root <other_shared_contract_dir>]", file=sys.stderr)
        return 2
    try:
        count = verify()
        print(f"Shared contract OK: {count} controlled files; manifest {manifest_self_hash()}.")
        if compare_root is not None:
            compared = compare_bundles(BUNDLE_ROOT, compare_root)
            print(f"Cross-bundle comparison OK: {compared} controlled files.")
    except ContractVerificationError as exc:
        print(f"Shared contract verification FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
