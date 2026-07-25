"""Tests for configuration-revision compatibility."""

from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.shared.contracts import ContractValidationError
from tests.contract.conftest import read_json, write_json


@pytest.mark.parametrize("filename", ["game.json", "rate_limits.json"])
def test_unsupported_configuration_revision_fails_clearly(
    contract_copy: Path,
    filename: str,
) -> None:
    path = contract_copy / "config" / filename
    config = read_json(path)
    config["version"] = "1.01"
    write_json(path, config)

    with pytest.raises(ContractValidationError, match="1.00.*was expected"):
        CopSDK.from_repository(contract_copy)
