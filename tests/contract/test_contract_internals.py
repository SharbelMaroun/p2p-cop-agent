"""Boundary and mismatch tests for the shared-contract loader."""

import shutil
from pathlib import Path

import pytest

from p2p_cop_agent.shared.contracts import (
    ContractValidationError,
    SharedContract,
    load_match_contract,
    require_same_match_configuration,
    shared_config_sha256,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _contract(**overrides: object) -> SharedContract:
    base = {
        "version": "0.2.2-proposed",
        "game": {"a": 1},
        "rate_limits": {},
        "config_sha256": "a" * 64,
        "config_file_sha256": "b" * 64,
    }
    base.update(overrides)
    return SharedContract(**base)  # type: ignore[arg-type]


def test_missing_contract_version_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ContractValidationError, match="Cannot load contract version"):
        load_match_contract(tmp_path)


def test_schema_profile_mismatch_is_rejected(tmp_path: Path) -> None:
    bundle = tmp_path / "shared_contract"
    (bundle / "schemas").mkdir(parents=True)
    (bundle / "CONTRACT_VERSION").write_text("9.9.9-proposed\n", encoding="utf-8")
    shutil.copy2(
        PROJECT_ROOT / "shared_contract" / "schemas" / "match-config.schema.json",
        bundle / "schemas" / "match-config.schema.json",
    )
    with pytest.raises(ContractValidationError, match="Unsupported contract version"):
        load_match_contract(tmp_path)


def test_non_serializable_config_is_rejected() -> None:
    with pytest.raises(ContractValidationError, match="Cannot canonicalize"):
        shared_config_sha256({"bad": {1, 2, 3}})  # type: ignore[dict-item]


def test_offer_version_mismatch_rejected() -> None:
    with pytest.raises(ContractValidationError, match="contract version differs"):
        require_same_match_configuration(_contract(), _contract(version="other"))


def test_offer_hash_mismatch_rejected() -> None:
    with pytest.raises(ContractValidationError, match="configuration hash differs"):
        require_same_match_configuration(_contract(), _contract(config_sha256="c" * 64))


def test_offer_source_byte_mismatch_rejected() -> None:
    with pytest.raises(ContractValidationError, match="source bytes differ"):
        require_same_match_configuration(_contract(), _contract(config_file_sha256="d" * 64))
