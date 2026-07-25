"""Generate and verify the byte-controlled shared-contract manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = "docs/contracts/PARITY_MANIFEST.json"
EXACT_PATHS = (
    ".gitattributes",
    "scripts/check_shared_contracts.py",
)
GLOB_PATHS = ("config/*.json",)
RECURSIVE_ROOTS = (
    "docs/contracts",
    "docs/schemas",
    "tests/fixtures/contracts",
)
EXCLUDED_PATHS = (MANIFEST_PATH,)


class ContractParityError(RuntimeError):
    """Raised when controlled contract bytes differ from the manifest."""


def canonical_bytes(value: object) -> bytes:
    """Serialize manifest data deterministically as UTF-8 JSON with LF."""
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def controlled_paths(root: Path) -> list[str]:
    """Discover controlled files using the checker-owned static policy."""
    paths = {path for path in EXACT_PATHS if (root / path).is_file()}
    for pattern in GLOB_PATHS:
        paths.update(
            _relative(path, root)
            for path in root.glob(pattern)
            if path.is_file()
        )
    for relative_root in RECURSIVE_ROOTS:
        directory = root / relative_root
        if directory.is_dir():
            paths.update(
                _relative(path, root)
                for path in directory.rglob("*")
                if path.is_file()
            )
    paths.difference_update(EXCLUDED_PATHS)
    return sorted(paths)


def sha256_file(path: Path) -> str:
    """Hash exact file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(root: Path = PROJECT_ROOT) -> dict[str, object]:
    """Build the deterministic manifest object from current controlled bytes."""
    version_path = root / "docs/contracts/CONTRACT_VERSION"
    try:
        contract_version = version_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ContractParityError(f"missing contract version: {version_path}") from exc
    files = [
        {"path": path, "sha256": sha256_file(root / path)}
        for path in controlled_paths(root)
    ]
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


def _file_map(manifest: dict[str, object]) -> dict[str, str]:
    try:
        entries = manifest["files"]
        if not isinstance(entries, list):
            raise TypeError
        return {
            entry["path"]: entry["sha256"]
            for entry in entries
            if isinstance(entry, dict)
            and isinstance(entry.get("path"), str)
            and isinstance(entry.get("sha256"), str)
        }
    except (KeyError, TypeError) as exc:
        raise ContractParityError("manifest has an invalid files list") from exc


def verify_manifest(root: Path = PROJECT_ROOT) -> int:
    """Verify canonical form, scope, presence, and every recorded byte hash."""
    path = root / MANIFEST_PATH
    try:
        raw = path.read_bytes()
        stored = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractParityError(f"cannot read parity manifest: {exc}") from exc
    if not isinstance(stored, dict):
        raise ContractParityError("parity manifest root must be an object")
    if raw != canonical_bytes(stored):
        raise ContractParityError("parity manifest is not canonical deterministic JSON")

    recorded = _file_map(stored)
    discovered = set(controlled_paths(root))
    missing = sorted(set(recorded) - discovered)
    unexpected = sorted(discovered - set(recorded))
    changed = sorted(
        relative
        for relative in discovered & set(recorded)
        if sha256_file(root / relative) != recorded[relative]
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
        raise ContractParityError("; ".join(failures))
    return len(recorded)


def write_manifest(root: Path = PROJECT_ROOT) -> Path:
    """Write the deterministic manifest, which is excluded from its own hash list."""
    path = root / MANIFEST_PATH
    path.write_bytes(canonical_bytes(build_manifest(root)))
    return path


def main(argv: list[str] | None = None) -> int:
    """Write or verify the manifest."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="regenerate the manifest")
    args = parser.parse_args(argv)
    try:
        if args.write:
            print(f"Wrote {write_manifest().relative_to(PROJECT_ROOT).as_posix()}")
        else:
            count = verify_manifest()
            print(f"Shared-contract parity OK: {count} controlled files.")
    except ContractParityError as exc:
        print(f"Shared-contract parity FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
