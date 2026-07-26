"""Tests for neutral match binding and semantic offer comparison."""

from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.shared.contracts import (
    ContractValidationError,
    SharedContract,
    require_same_match_configuration,
    verify_config_sha256,
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


def test_missing_participant_agreement_is_rejected(contract_copy: Path) -> None:
    path = contract_copy / "config/game.json"
    game = read_json(path)
    del game["agreed_between"]
    write_json(path, game)

    with pytest.raises(ContractValidationError, match="agreed_between.*required property"):
        CopSDK.from_repository(contract_copy)


def test_changed_negotiated_value_is_rejected_before_play(contract_copy: Path) -> None:
    path = contract_copy / "config/game.json"
    game = read_json(path)
    world = game["world"]
    assert isinstance(world, dict)
    world["map_area"] = "Different agreed area"
    write_json(path, game)

    sdk = CopSDK.from_repository(PROJECT_ROOT)
    with pytest.raises(ContractValidationError, match="game configuration differs"):
        sdk.validate_match_offer(contract_copy)


@pytest.mark.parametrize("malformed", ["bad", "A" * 64, "0" * 63])
def test_malformed_configuration_hash_is_rejected(
    malformed: str,
) -> None:
    game = read_json(PROJECT_ROOT / "config/game.json")

    with pytest.raises(ContractValidationError, match="config_sha256"):
        verify_config_sha256(game, malformed)


@pytest.mark.parametrize(
    "private_field",
    ["port", "opponent_url", "model", "credentials", "strategy", "nonce", "secret"],
)
def test_private_field_leakage_is_rejected(contract_copy: Path, private_field: str) -> None:
    path = contract_copy / "config/game.json"
    game = read_json(path)
    game[private_field] = "must-stay-private"
    write_json(path, game)

    with pytest.raises(ContractValidationError, match="Additional properties are not allowed"):
        CopSDK.from_repository(contract_copy)


def test_rate_limit_mirror_must_agree(contract_copy: Path) -> None:
    path = contract_copy / "config/rate_limits.json"
    rates = read_json(path)
    limits = rates["rate_limiter_gatekeeper"]
    assert isinstance(limits, dict)
    limits["requests_per_minute"] = 31
    write_json(path, rates)

    with pytest.raises(ContractValidationError, match="rate-limit mirror differs"):
        CopSDK.from_repository(contract_copy)


def test_participant_order_is_byte_significant(contract_copy: Path) -> None:
    path = contract_copy / "config/game.json"
    game = read_json(path)
    participants = game["agreed_between"]
    assert isinstance(participants, list)
    game["agreed_between"] = list(reversed(participants))
    write_json(path, game)

    sdk = CopSDK.from_repository(PROJECT_ROOT)
    with pytest.raises(ContractValidationError, match="game configuration differs"):
        sdk.validate_match_offer(contract_copy)


def test_semantic_match_comparison_rejects_each_contract_layer() -> None:
    base = SharedContract("candidate", {"field": "game"}, {"field": "rates"}, "hash")

    with pytest.raises(ContractValidationError, match="contract version differs"):
        require_same_match_configuration(
            base,
            SharedContract("different", {"field": "game"}, {"field": "rates"}, "hash"),
        )
    with pytest.raises(ContractValidationError, match="game configuration differs"):
        require_same_match_configuration(
            base,
            SharedContract("candidate", {"field": "changed"}, {"field": "rates"}, "changed"),
        )
    with pytest.raises(ContractValidationError, match="rate-limit configuration differs"):
        require_same_match_configuration(
            base,
            SharedContract("candidate", {"field": "game"}, {"field": "changed"}, "hash"),
        )
    with pytest.raises(ContractValidationError, match="configuration hash differs"):
        require_same_match_configuration(
            base,
            SharedContract("candidate", {"field": "game"}, {"field": "rates"}, "changed"),
        )


@pytest.mark.parametrize("unsupported", ["1.1", "1.3", "9.9"])
def test_unsupported_config_profile_fails_clearly(
    contract_copy: Path,
    unsupported: str,
) -> None:
    path = contract_copy / "config/game.json"
    game = read_json(path)
    game["schema_version"] = unsupported
    write_json(path, game)

    with pytest.raises(ContractValidationError, match="game config"):
        CopSDK.from_repository(contract_copy)
