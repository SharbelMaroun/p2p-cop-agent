"""Contract tests for loading a per-match config against the stable bundle."""

from pathlib import Path

import pytest

from p2p_cop_agent.shared.contracts import (
    ContractValidationError,
    load_match_contract,
    shared_config_sha256,
    verify_config_sha256,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"
CANONICAL_SHA = "adac9efe6d51b9487c400a04c2e185af9fb3622e1a7d74f18d400425656d82db"
FILE_SHA = "70758af55f178a049a438b81eb5f9acd389c568214cb3006358c66f8d10abd06"


def test_example_template_loads_with_expected_identity() -> None:
    contract = load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    assert contract.version == "0.2.15-proposed"
    assert contract.game["board_and_agents"]["grid_size"] == 7  # type: ignore[index]
    assert contract.config_sha256 == CANONICAL_SHA
    assert contract.config_file_sha256 == FILE_SHA


def test_config_sha256_covers_agreed_between() -> None:
    contract = load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    mutated = dict(contract.game)
    mutated["agreed_between"] = ["other-a", "other-b"]
    assert shared_config_sha256(mutated) != contract.config_sha256


def test_verify_config_sha256_accepts_the_correct_claim() -> None:
    contract = load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    verify_config_sha256(contract.game, contract.config_sha256)


@pytest.mark.parametrize("claim", ["", "ZZ", "a" * 63, "A" * 64])
def test_verify_config_sha256_rejects_malformed_claims(claim: str) -> None:
    contract = load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    with pytest.raises(ContractValidationError, match="64 lowercase hexadecimal"):
        verify_config_sha256(contract.game, claim)


def test_verify_config_sha256_rejects_wrong_hash() -> None:
    contract = load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    with pytest.raises(ContractValidationError, match="does not match"):
        verify_config_sha256(contract.game, "0" * 64)


def test_rate_limit_mirror_matches_shared_gatekeeper() -> None:
    contract = load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    assert (
        contract.game["rate_limiter_gatekeeper"]
        == contract.rate_limits["rate_limiter_gatekeeper"]
    )
