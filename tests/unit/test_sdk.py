"""Tests for the behavior-free public SDK."""

import json
from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.shared.config import ConfigLoadError, load_json_object

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"


def write_json(path: Path, value: object) -> None:
    """Write compact test JSON."""
    path.write_text(json.dumps(value), encoding="utf-8")


def test_sdk_loads_validated_values_from_repository_files() -> None:
    """Load values from files instead of source constants."""
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)

    assert sdk.game_config["board_and_agents"]["grid_size"] == 7  # type: ignore[index]
    assert sdk.rate_limits_config["rate_limiter_gatekeeper"]["queue_depth"] == 100  # type: ignore[index]
    assert sdk.game_config["agreed_between"] == ["neutral-group-alpha", "neutral-group-beta"]
    assert sdk.config_sha256 == "adac9efe6d51b9487c400a04c2e185af9fb3622e1a7d74f18d400425656d82db"
    assert sdk.config_file_sha256 == (
        "70758af55f178a049a438b81eb5f9acd389c568214cb3006358c66f8d10abd06"
    )
    assert sdk.role == "cop"
    assert sdk.version == "1.00"
    assert sdk.contract_version == "0.2.9-proposed"


@pytest.mark.parametrize("value", [[], "not-an-object", 7])
def test_sdk_rejects_non_object_json(tmp_path: Path, value: object) -> None:
    """Reject JSON roots that cannot represent named configuration fields."""
    path = tmp_path / "config.json"
    write_json(path, value)

    with pytest.raises(ConfigLoadError, match="must contain an object"):
        load_json_object(path)


def test_sdk_reports_malformed_json(tmp_path: Path) -> None:
    """Translate decoder failures into a configuration-specific error."""
    path = tmp_path / "config.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(ConfigLoadError, match="Cannot load JSON configuration"):
        load_json_object(path)


def test_sdk_rejects_duplicate_json_members(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text('{"same": 1, "same": 2}', encoding="utf-8")

    with pytest.raises(ConfigLoadError, match="Duplicate JSON member 'same'"):
        load_json_object(path)


@pytest.mark.parametrize("invalid", ["NaN", "Infinity", "-Infinity"])
def test_sdk_rejects_non_finite_json_numbers(tmp_path: Path, invalid: str) -> None:
    path = tmp_path / "config.json"
    path.write_text(f'{{"value": {invalid}}}', encoding="utf-8")

    with pytest.raises(ConfigLoadError, match="Non-finite JSON number"):
        load_json_object(path)
