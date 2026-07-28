"""Bundle hardening: LF bytes, a read-only verifier, and owner-only manifest gen."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUNDLE = PROJECT_ROOT / "shared_contract"
STUB = PROJECT_ROOT / "tests" / "conformance" / "neutral_stub.py"
WRITE_TOKENS = ("write_text", "write_bytes", "open(", ".write(")


def _bundle_files() -> list[Path]:
    return [
        path
        for path in BUNDLE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    ]


def test_all_controlled_bundle_files_use_lf() -> None:
    for path in _bundle_files():
        assert b"\r\n" not in path.read_bytes(), f"{path.name} contains CRLF"


def test_gitattributes_forces_lf_for_the_bundle() -> None:
    attributes = (PROJECT_ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "/shared_contract/** text eol=lf" in attributes


def test_verifier_is_read_only_source() -> None:
    source = (BUNDLE / "verify.py").read_text(encoding="utf-8")
    for token in WRITE_TOKENS:
        assert token not in source, f"verifier must not contain {token!r}"


def test_verify_does_not_modify_the_manifest() -> None:
    sys.path.insert(0, str(BUNDLE))
    import verify  # noqa: PLC0415  (path-injected neutral module)

    manifest = BUNDLE / "PARITY_MANIFEST.json"
    before = manifest.read_bytes()
    count = verify.verify()
    assert count > 0
    assert manifest.read_bytes() == before


def test_manifest_generation_lives_outside_the_verifier() -> None:
    assert (PROJECT_ROOT / "scripts" / "generate_shared_manifest.py").is_file()
    source = (BUNDLE / "verify.py").read_text(encoding="utf-8")
    assert "def write_manifest" not in source


def test_neutral_stub_does_not_import_cop_runtime() -> None:
    for line in STUB.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        assert not stripped.startswith("import p2p_cop_agent")
        assert not stripped.startswith("from p2p_cop_agent")
