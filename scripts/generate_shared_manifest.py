"""Repository-owner-only generator for the shared-contract parity manifest.

This is deliberately separate from the role-neutral read-only verifier
(``shared_contract/verify.py``): the verifier never writes, and manifest
generation is a Cop-owner operation. It reuses the neutral verifier's discovery
and hashing so the written manifest is exactly what the verifier expects.
"""

from __future__ import annotations

import sys
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parents[1] / "shared_contract"
sys.path.insert(0, str(BUNDLE_ROOT))

from verify import (  # noqa: E402  (path injected above)
    MANIFEST_NAME,
    build_manifest,
    canonical_manifest_bytes,
    manifest_self_hash,
)


def write_manifest(root: Path = BUNDLE_ROOT) -> Path:
    """Write the deterministic manifest; it is excluded from its own file list."""
    path = root / MANIFEST_NAME
    path.write_bytes(canonical_manifest_bytes(build_manifest(root)))
    return path


def main() -> int:
    """Regenerate the manifest and report its exact-byte self-hash."""
    path = write_manifest()
    print(f"Wrote {path.name}; manifest SHA-256 {manifest_self_hash()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
