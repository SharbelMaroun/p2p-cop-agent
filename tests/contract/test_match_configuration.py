"""Tests for neutral match binding and semantic offer comparison."""

from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.shared.contracts import (
    ContractValidationError,
    SharedContract,
    require_same_match_configuration,
)
from tests.contract.conftest import read_json, write_json

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_parameter_schema_records_status_and_ownership() -> None:
    schema = read_json(PROJECT_ROOT / "docs/schemas/game-config.schema.json")
    properties = schema["properties"]
    assert isinstance(properties, dict)
    board = properties["board_and_agents"]
    assert isinstance(board, dict)
    board_properties = board["properties"]
    assert isinstance(board_properties, dict)

    assert board_properties["num_agents"]["x-appendix-f-status"] == "fixed"  # type: ignore[index]
    assert board_properties["num_agents"]["x-value-owner"] == "appendix_f"  # type: ignore[index]
    assert board_properties["grid_size"]["x-appendix-f-status"] == "minimum"  # type: ignore[index]
    assert board_properties["grid_size"]["x-value-owner"] == "mutual_agreement"  # type: ignore[index]
    assert board_properties["thief_start"]["x-appendix-f-status"] == "negotiated"  # type: ignore[index]


def test_identical_neutral_offer_is_accepted(contract_copy: Path) -> None:
    sdk = CopSDK.from_repository(PROJECT_ROOT)

    sdk.validate_match_offer(contract_copy)


def test_cross_file_match_identity_must_agree(contract_copy: Path) -> None:
    path = contract_copy / "config/rate_limits.json"
    rates = read_json(path)
    rates["game_id"] = "different-match"
    write_json(path, rates)

    with pytest.raises(ContractValidationError, match="match binding differs for game_id"):
        CopSDK.from_repository(contract_copy)


def test_config_name_must_bind_book_filename_identity(contract_copy: Path) -> None:
    path = contract_copy / "config/game.json"
    game = read_json(path)
    game["config_name"] = "config_different_g01.json"
    write_json(path, game)

    with pytest.raises(ContractValidationError, match="config_neutral-match_g01.json"):
        CopSDK.from_repository(contract_copy)


def test_semantic_match_comparison_rejects_each_contract_layer() -> None:
    base = SharedContract("candidate", {"field": "game"}, {"field": "rates"})

    with pytest.raises(ContractValidationError, match="contract version differs"):
        require_same_match_configuration(
            base,
            SharedContract("different", {"field": "game"}, {"field": "rates"}),
        )
    with pytest.raises(ContractValidationError, match="game configuration differs"):
        require_same_match_configuration(
            base,
            SharedContract("candidate", {"field": "changed"}, {"field": "rates"}),
        )
    with pytest.raises(ContractValidationError, match="rate-limit configuration differs"):
        require_same_match_configuration(
            base,
            SharedContract("candidate", {"field": "game"}, {"field": "changed"}),
        )


def test_unsupported_config_profile_fails_clearly(contract_copy: Path) -> None:
    path = contract_copy / "config/game.json"
    game = read_json(path)
    game["schema_version"] = "9.9"
    write_json(path, game)

    with pytest.raises(ContractValidationError, match="game config"):
        CopSDK.from_repository(contract_copy)


def test_unsupported_contract_version_fails_clearly(contract_copy: Path) -> None:
    (contract_copy / "docs/contracts/CONTRACT_VERSION").write_text(
        "9.9-unsupported\n",
        encoding="utf-8",
    )

    with pytest.raises(ContractValidationError, match="Unsupported contract version"):
        CopSDK.from_repository(contract_copy)
