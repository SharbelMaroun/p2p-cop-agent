"""Cross-field board validation applied after JSON Schema validation.

Coordinator blocker 7: coordinates were accepted as any integer pair without
checking them against the negotiated grid size, axis origin, and start index.
"""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.shared.contracts import ContractValidationError, load_match_contract

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"


def base_config() -> dict:
    """Return a mutable copy of the example match config."""
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def write_config(tmp_path: Path, config: dict) -> Path:
    """Write a candidate match config and return its path."""
    path = tmp_path / "match.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def test_valid_starts_are_accepted() -> None:
    contract = load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    assert contract.game["board_and_agents"]["cop_start"]


@pytest.mark.parametrize("start", ["cop_start", "thief_start"])
def test_rejects_a_start_beyond_the_grid(tmp_path: Path, start: str) -> None:
    config = base_config()
    config["board_and_agents"][start] = [7, 0]
    with pytest.raises(ContractValidationError, match="outside board bounds"):
        load_match_contract(
            PROJECT_ROOT,
            write_config(tmp_path, config),
            rate_limits_path=RATE_LIMITS,
        )


@pytest.mark.parametrize("start", ["cop_start", "thief_start"])
def test_rejects_a_negative_start(tmp_path: Path, start: str) -> None:
    config = base_config()
    config["board_and_agents"][start] = [-1, 0]
    with pytest.raises(ContractValidationError, match="outside board bounds"):
        load_match_contract(
            PROJECT_ROOT,
            write_config(tmp_path, config),
            rate_limits_path=RATE_LIMITS,
        )


def test_rejects_identical_starts(tmp_path: Path) -> None:
    config = base_config()
    config["board_and_agents"]["cop_start"] = config["board_and_agents"]["thief_start"]
    with pytest.raises(ContractValidationError, match="must be different cells"):
        load_match_contract(
            PROJECT_ROOT,
            write_config(tmp_path, config),
            rate_limits_path=RATE_LIMITS,
        )


def test_rejects_a_negative_axis_start_index(tmp_path: Path) -> None:
    config = base_config()
    config["board_and_agents"]["axis_start_index"] = -1
    with pytest.raises(ContractValidationError, match="match config"):
        load_match_contract(
            PROJECT_ROOT,
            write_config(tmp_path, config),
            rate_limits_path=RATE_LIMITS,
        )


def test_start_is_validated_against_a_shifted_axis_start_index(tmp_path: Path) -> None:
    config = base_config()
    config["board_and_agents"]["axis_start_index"] = 1
    with pytest.raises(ContractValidationError, match="outside board bounds"):
        load_match_contract(
            PROJECT_ROOT,
            write_config(tmp_path, config),
            rate_limits_path=RATE_LIMITS,
        )
