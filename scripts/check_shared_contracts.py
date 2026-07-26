"""CLI for local contract integrity and optional read-only cross-root comparison."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from shared_contract_integrity import (
    ContractIntegrityError,
    compare_repository_roots,
    manifest_self_hash,
    verify_manifest,
    write_manifest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    """Write, locally verify, or compare the Cop-authored contract bundle."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="regenerate the local manifest")
    parser.add_argument(
        "--compare-root",
        type=Path,
        help="read-only compare with another repository root after local verification",
    )
    args = parser.parse_args(argv)
    if args.write and args.compare_root:
        parser.error("--write and --compare-root cannot be combined")

    try:
        if args.write:
            path = write_manifest(PROJECT_ROOT)
            print(f"Wrote {path.relative_to(PROJECT_ROOT).as_posix()}")
            return 0

        count = verify_manifest(PROJECT_ROOT)
        self_hash = manifest_self_hash(PROJECT_ROOT)
        print(
            f"Cop-local contract integrity OK: {count} controlled files; "
            f"manifest SHA-256 {self_hash}."
        )
        if args.compare_root:
            compared = compare_repository_roots(PROJECT_ROOT, args.compare_root)
            print(
                f"Cross-root exact-byte comparison OK: {compared} controlled files; "
                f"manifest SHA-256 {self_hash}."
            )
    except ContractIntegrityError as exc:
        print(f"Shared-contract check FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
