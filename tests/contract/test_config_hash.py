"""Independent vectors for the shared source-configuration hash."""

from pathlib import Path

import pytest

from p2p_cop_agent.shared.contracts import (
    ContractValidationError,
    canonical_config_bytes,
    shared_config_sha256,
    validate_instance,
    verify_config_sha256,
)
from tests.contract.conftest import read_json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED = "adac9efe6d51b9487c400a04c2e185af9fb3622e1a7d74f18d400425656d82db"


def test_candidate_config_matches_recorded_hash_vector() -> None:
    game = read_json(PROJECT_ROOT / "config/game.json")
    vector = read_json(
        PROJECT_ROOT / "tests/fixtures/contracts/game-config-sha256.vector.json"
    )
    schema = read_json(PROJECT_ROOT / "docs/schemas/config-hash-vector.schema.json")

    validate_instance(vector, schema, "config hash vector")
    canonical = canonical_config_bytes(game)
    assert len(canonical) == vector["canonical_utf8_length"] == 965
    assert shared_config_sha256(game) == vector["sha256"] == EXPECTED
    verify_config_sha256(game, vector["sha256"])


def test_canonical_bytes_are_sorted_compact_unicode_utf8() -> None:
    first = {"z": "עכו", "a": {"y": 2, "x": 1}}
    second = {"a": {"x": 1, "y": 2}, "z": "עכו"}
    expected = '{"a":{"x":1,"y":2},"z":"עכו"}'.encode()

    assert canonical_config_bytes(first) == expected
    assert canonical_config_bytes(second) == expected


def test_hash_verification_rejects_changed_shared_value() -> None:
    game = read_json(PROJECT_ROOT / "config/game.json")
    world = game["world"]
    assert isinstance(world, dict)
    world["map_area"] = "Changed"

    with pytest.raises(ContractValidationError, match="does not match"):
        verify_config_sha256(game, EXPECTED)


def test_canonicalization_rejects_non_finite_values() -> None:
    with pytest.raises(ContractValidationError, match="Out of range float"):
        canonical_config_bytes({"invalid": float("nan")})
