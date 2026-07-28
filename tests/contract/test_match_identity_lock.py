"""Tests for exact shared match identity and local rate configuration."""

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


def test_local_rate_limit_extensions_are_not_match_terms(contract_copy: Path) -> None:
    path = contract_copy / "config/rate_limits.json"
    rates = read_json(path)
    extensions = rates["extensions"]
    assert isinstance(extensions, dict)
    extensions["local_queue_metric"] = True
    write_json(path, rates)

    CopSDK.from_repository(PROJECT_ROOT).validate_match_offer(contract_copy)


def test_semantically_equal_but_byte_different_game_is_rejected(contract_copy: Path) -> None:
    path = contract_copy / "config/game.json"
    path.write_bytes(path.read_bytes() + b" ")

    with pytest.raises(ContractValidationError, match="source bytes differ"):
        CopSDK.from_repository(PROJECT_ROOT).validate_match_offer(contract_copy)


def test_semantic_match_comparison_rejects_each_contract_layer() -> None:
    base = SharedContract("candidate", {"field": "game"}, {"field": "rates"}, "hash", "raw")

    with pytest.raises(ContractValidationError, match="contract version differs"):
        require_same_match_configuration(
            base,
            SharedContract(
                "different", {"field": "game"}, {"field": "rates"}, "hash", "raw"
            ),
        )
    with pytest.raises(ContractValidationError, match="game configuration differs"):
        require_same_match_configuration(
            base,
            SharedContract(
                "candidate", {"field": "changed"}, {"field": "rates"}, "changed", "raw"
            ),
        )
    with pytest.raises(ContractValidationError, match="configuration hash differs"):
        require_same_match_configuration(
            base,
            SharedContract(
                "candidate", {"field": "game"}, {"field": "rates"}, "changed", "raw"
            ),
        )
    with pytest.raises(ContractValidationError, match="source bytes differ"):
        require_same_match_configuration(
            base,
            SharedContract(
                "candidate", {"field": "game"}, {"field": "rates"}, "hash", "changed"
            ),
        )
