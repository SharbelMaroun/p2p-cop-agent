"""Prove the three hash domains are distinct and reproduce their vectors."""

import hashlib
import re
from pathlib import Path

from p2p_cop_agent.protocol.commit import canonical_payload_bytes, move_commit
from p2p_cop_agent.shared.config import load_json_object
from p2p_cop_agent.shared.contracts import load_match_contract, shared_config_sha256

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VECTORS = PROJECT_ROOT / "shared_contract" / "vectors"
FIXTURES = PROJECT_ROOT / "shared_contract" / "fixtures"
EXAMPLE = FIXTURES / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"


def test_example_match_hash_domains_are_all_distinct() -> None:
    contract = load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    canonical_object_hash = contract.config_sha256
    raw_bytes_hash = contract.config_file_sha256
    commitment = move_commit(contract.game, "0" * 32)

    assert canonical_object_hash != raw_bytes_hash
    assert commitment not in {canonical_object_hash, raw_bytes_hash}


def test_config_sha256_vectors_reproduce() -> None:
    data = load_json_object(VECTORS / "config-sha256.vectors.json")
    for vector in data["vectors"]:  # type: ignore[union-attr]
        if "object" in vector:
            assert shared_config_sha256(vector["object"]) == vector["config_sha256"]


def test_example_vector_matches_loaded_contract() -> None:
    contract = load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    data = load_json_object(VECTORS / "config-sha256.vectors.json")
    example = next(v for v in data["vectors"] if v["name"] == "example_match_object")  # type: ignore[union-attr]
    assert contract.config_sha256 == example["config_sha256"]
    assert contract.config_file_sha256 == example["config_file_sha256"]


def test_negotiation_projection_is_distinct_from_full_object() -> None:
    fixture = load_json_object(FIXTURES / "negotiation_terms.projection.json")
    game_object = fixture["game_object"]
    projection = fixture["negotiation_terms"]

    assert shared_config_sha256(game_object) == fixture["game_object_config_sha256"]
    projection_hash = hashlib.sha256(canonical_payload_bytes(projection)).hexdigest()
    assert projection_hash != fixture["game_object_config_sha256"]
    assert projection["board_size"] == game_object["board_and_agents"]["grid_size"]  # type: ignore[index]


def test_lecturer_supplied_65_char_value_is_not_a_valid_sha256() -> None:
    data = load_json_object(VECTORS / "config-sha256.vectors.json")
    note = data["not_adopted_lecturer_hashes"]["invalid_length_65"]  # type: ignore[index]
    assert "65-character" in note
    assert re.fullmatch(r"[0-9a-f]{64}", "9f2c" + "a" * 61) is None
