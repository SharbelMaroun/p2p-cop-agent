"""Tests for safe snapshots of the supplied artifact-template key sets."""

from __future__ import annotations

from pathlib import Path

import pytest

from p2p_cop_agent.shared.contracts import ContractValidationError, load_artifact_keysets
from tests.contract.conftest import read_json, write_json

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_all_observed_artifact_keysets_parse() -> None:
    fixtures = load_artifact_keysets(PROJECT_ROOT)

    assert set(fixtures) == {
        "pre_game_declaration",
        "agreed_config",
        "game_log",
        "final_result",
    }
    assert {item["observed_schema_version"] for item in fixtures.values()} == {"1.1"}
    assert fixtures["pre_game_declaration"]["key_sets"]["$.groups"] == ["*"]  # type: ignore[index]
    assert fixtures["game_log"]["key_sets"]["$.records[]"] == [  # type: ignore[index]
        "payload",
        "nonce",
        "commit",
    ]
    assert fixtures["game_log"]["key_sets"][  # type: ignore[index]
        "$.records[].payload[move].prompt_discussion"
    ] == [
        "llm_prompt",
        "llm_reasoning",
        "bluff_classification",
    ]


def test_fixture_missing_descriptor_field_fails(contract_copy: Path) -> None:
    path = contract_copy / "tests/fixtures/contracts/declaration.keyset.json"
    fixture = read_json(path)
    del fixture["key_sets"]
    write_json(path, fixture)

    with pytest.raises(ContractValidationError, match="key_sets.*required property"):
        load_artifact_keysets(contract_copy)


def test_unsupported_observed_artifact_profile_fails(contract_copy: Path) -> None:
    path = contract_copy / "tests/fixtures/contracts/agreed_config.keyset.json"
    fixture = read_json(path)
    fixture["observed_schema_version"] = "1.2"
    write_json(path, fixture)

    with pytest.raises(ContractValidationError, match="1.1.*was expected"):
        load_artifact_keysets(contract_copy)
