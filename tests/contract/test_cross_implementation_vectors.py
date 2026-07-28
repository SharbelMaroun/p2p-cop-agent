"""M4-02: two independent implementations reproduce the exact published hashes.

The Cop runtime (``p2p_cop_agent.protocol``/``shared``) and the neutral stub
(``tests.conformance.neutral_stub``, which shares no code with the runtime) must
each reproduce every published vector *and* agree byte-for-byte with each other.
This is stronger than each implementation separately matching the stored value.
No controlled ``shared_contract`` file is modified.
"""

import hashlib
import json
import re
from pathlib import Path

from p2p_cop_agent.protocol.commit import generate_commitment_nonce, move_commit
from p2p_cop_agent.shared.contracts import shared_config_sha256
from tests.conformance import neutral_stub

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VECTORS = PROJECT_ROOT / "shared_contract" / "vectors"
NONCE_RE = re.compile(r"^[0-9a-f]{32}$")


def _load(name: str) -> dict:
    return json.loads((VECTORS / name).read_text(encoding="utf-8"))


def test_move_commit_vectors_agree_across_implementations() -> None:
    data = _load("move-commit.vectors.json")
    for vector in data["vectors"]:
        payload, nonce, expected = vector["payload"], vector["nonce"], vector["commit"]
        runtime = move_commit(payload, nonce)
        independent = neutral_stub.commit(payload, nonce)
        assert runtime == expected, vector["name"]
        assert independent == expected, vector["name"]
        assert runtime == independent, vector["name"]


def test_config_sha256_vectors_agree_across_implementations() -> None:
    data = _load("config-sha256.vectors.json")
    for vector in data["vectors"]:
        if "object" not in vector:
            continue
        obj, expected = vector["object"], vector["config_sha256"]
        runtime = shared_config_sha256(obj)
        independent = hashlib.sha256(neutral_stub.canonical(obj)).hexdigest()
        assert runtime == expected, vector["name"]
        assert independent == expected, vector["name"]
        assert runtime == independent, vector["name"]


def test_delimiter_and_profile_are_published() -> None:
    data = _load("move-commit.vectors.json")
    assert data["delimiter"] == "|"
    assert data["commitment_nonce_profile"] == {"bytes": 16, "hex_length": 32}


def test_every_vector_nonce_matches_the_commitment_profile() -> None:
    data = _load("move-commit.vectors.json")
    for vector in data["vectors"]:
        assert NONCE_RE.fullmatch(vector["nonce"]), vector["name"]


def test_generated_commitment_nonces_are_fresh_and_well_formed() -> None:
    nonces = {generate_commitment_nonce() for _ in range(64)}
    assert len(nonces) == 64  # fresh each call; not derived from a fixed challenge
    assert all(NONCE_RE.fullmatch(value) for value in nonces)


def test_neutral_stub_imports_no_runtime_code() -> None:
    source = (PROJECT_ROOT / "tests" / "conformance" / "neutral_stub.py").read_text(
        encoding="utf-8"
    )
    for line in source.splitlines():
        stripped = line.strip()
        assert not stripped.startswith(("import p2p_cop_agent", "from p2p_cop_agent"))
