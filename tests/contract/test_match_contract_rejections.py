"""Rejection vectors for per-match config loading and offer comparison."""

import json
from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.shared.config import ConfigLoadError
from p2p_cop_agent.shared.contracts import ContractValidationError, load_match_contract

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"


def base_config() -> dict:
    """Return a mutable copy of the example match config."""
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def write_config(tmp_path: Path, config: dict) -> Path:
    """Write a candidate match config and return its path."""
    path = tmp_path / "match.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


@pytest.mark.parametrize("schema_version", ["1.1", "1.3"])
def test_rejects_unsupported_schema_version(tmp_path: Path, schema_version: str) -> None:
    config = base_config()
    config["schema_version"] = schema_version
    with pytest.raises(ContractValidationError, match="match config"):
        load_match_contract(PROJECT_ROOT, write_config(tmp_path, config))


def test_rejects_grid_size_below_minimum(tmp_path: Path) -> None:
    config = base_config()
    config["board_and_agents"]["grid_size"] = 5
    with pytest.raises(ContractValidationError, match="match config"):
        load_match_contract(PROJECT_ROOT, write_config(tmp_path, config))


def test_rejects_duplicate_json_member(tmp_path: Path) -> None:
    path = tmp_path / "match.json"
    path.write_text('{"version": "1.00", "version": "1.00"}', encoding="utf-8")
    with pytest.raises(ConfigLoadError, match="Duplicate JSON member"):
        load_match_contract(PROJECT_ROOT, path)


def test_rejects_rate_limit_mirror_mismatch(tmp_path: Path) -> None:
    config = base_config()
    config["rate_limiter_gatekeeper"]["requests_per_minute"] = 999
    with pytest.raises(ContractValidationError, match="rate-limit mirror differs"):
        load_match_contract(PROJECT_ROOT, write_config(tmp_path, config))


def test_offer_with_different_game_is_rejected(tmp_path: Path) -> None:
    sdk = CopSDK.from_repository(PROJECT_ROOT)
    config = base_config()
    config["board_and_agents"]["grid_size"] = 9
    with pytest.raises(ContractValidationError, match="negotiated game configuration differs"):
        sdk.validate_match_offer(PROJECT_ROOT, write_config(tmp_path, config))


def test_offer_matching_the_example_is_accepted() -> None:
    sdk = CopSDK.from_repository(PROJECT_ROOT)
    sdk.validate_match_offer(PROJECT_ROOT)
