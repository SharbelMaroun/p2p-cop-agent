"""Tests for source-backed shared configuration validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.shared.contracts import ContractValidationError
from tests.contract.conftest import read_json, write_json

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def nested_set(value: dict[str, object], path: tuple[str, ...], replacement: object) -> None:
    """Replace one nested field in a JSON-like object."""
    current = value
    for part in path[:-1]:
        child = current[part]
        assert isinstance(child, dict)
        current = child
    current[path[-1]] = replacement


def test_shared_bundle_loads_all_confirmed_values() -> None:
    sdk = CopSDK.from_repository(PROJECT_ROOT)
    game = sdk.game_config
    rates = sdk.rate_limits_config["rate_limiter_gatekeeper"]

    assert sdk.contract_version == "0.1.0-proposed"
    assert game["version"] == "1.00"
    assert game["schema_version"] == "1.2"
    assert game["agreed_between"] == ["neutral-group-alpha", "neutral-group-beta"]
    assert sdk.config_sha256 == "adac9efe6d51b9487c400a04c2e185af9fb3622e1a7d74f18d400425656d82db"
    assert sdk.rate_limits_config["version"] == "1.00"
    assert game["movement_and_barriers"] == {
        "move_set": ["N", "S", "E", "W", "STAY"],
        "max_barriers": 14,
        "max_moves": 35,
        "survival_threshold": 35,
    }
    assert game["scoring"] == {
        "capture_cop": 20,
        "capture_thief": 5,
        "survival_cop": 5,
        "survival_thief": 10,
        "tie_score": 2,
        "technical_loss": 0,
    }
    assert game["pheromones"] == {
        "pheromone_center_intensity": 0.9,
        "pheromone_decay": 0.1,
        "pheromone_grid_size": 5,
    }
    assert game["network_and_league"]["num_games"] == 6  # type: ignore[index]
    assert game["network_and_league"]["response_timeout_sec"] == 30  # type: ignore[index]
    assert rates == {
        "requests_per_minute": 30,
        "concurrent_requests": 2,
        "retry_backoff_sec": 5,
        "max_retries": 3,
        "queue_depth": 100,
    }
    assert game["rate_limiter_gatekeeper"] == rates


@pytest.mark.parametrize(
    ("filename", "path", "invalid"),
    [
        ("game.json", ("board_and_agents", "grid_size"), 6),
        ("game.json", ("movement_and_barriers", "max_barriers"), 13),
        ("game.json", ("movement_and_barriers", "max_moves"), 34),
        ("game.json", ("movement_and_barriers", "survival_threshold"), 34),
        ("game.json", ("rate_limiter_gatekeeper", "requests_per_minute"), 29),
        ("rate_limits.json", ("rate_limiter_gatekeeper", "requests_per_minute"), 29),
        ("rate_limits.json", ("rate_limiter_gatekeeper", "concurrent_requests"), 1),
        ("rate_limits.json", ("rate_limiter_gatekeeper", "retry_backoff_sec"), 4),
        ("rate_limits.json", ("rate_limiter_gatekeeper", "max_retries"), 2),
        ("rate_limits.json", ("rate_limiter_gatekeeper", "queue_depth"), 99),
    ],
)
def test_values_below_official_minimum_are_rejected(
    contract_copy: Path,
    filename: str,
    path: tuple[str, ...],
    invalid: int,
) -> None:
    config_path = contract_copy / "config" / filename
    value = read_json(config_path)
    nested_set(value, path, invalid)
    write_json(config_path, value)

    with pytest.raises(ContractValidationError, match="less than the minimum"):
        CopSDK.from_repository(contract_copy)


def test_missing_shared_field_is_rejected(contract_copy: Path) -> None:
    path = contract_copy / "config/game.json"
    game = read_json(path)
    del game["scoring"]
    write_json(path, game)

    with pytest.raises(ContractValidationError, match="required property"):
        CopSDK.from_repository(contract_copy)


def test_invalid_movement_vocabulary_is_rejected(contract_copy: Path) -> None:
    path = contract_copy / "config/game.json"
    game = read_json(path)
    nested_set(game, ("movement_and_barriers", "move_set"), ["N", "S", "E", "W", "NE"])
    write_json(path, game)

    with pytest.raises(ContractValidationError, match="was expected"):
        CopSDK.from_repository(contract_copy)


def test_negotiated_values_are_loaded_from_files(contract_copy: Path) -> None:
    path = contract_copy / "config/game.json"
    game = read_json(path)
    nested_set(game, ("world", "map_area"), "Haifa")
    nested_set(game, ("network_and_league", "token_budget_per_series"), 240000)
    write_json(path, game)

    sdk = CopSDK.from_repository(contract_copy)

    assert sdk.game_config["world"]["map_area"] == "Haifa"  # type: ignore[index]
    assert sdk.game_config["network_and_league"]["token_budget_per_series"] == 240000  # type: ignore[index]
