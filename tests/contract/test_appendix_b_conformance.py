"""Conformance: an opponent following Appendix B's structure must be accepted.

Coordinator blocker 2: requiring root `version` and `extensions` under
`additionalProperties: false` rejected a peer whose game.json follows the
official Appendix B structure, which carries neither field.
"""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.shared.contracts import ContractValidationError, load_match_contract

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = PROJECT_ROOT / "shared_contract" / "fixtures"
APPENDIX_B = FIXTURES / "match_config.appendix_b.json"
EXAMPLE = FIXTURES / "match_config.example.json"


def base_config() -> dict:
    """Return a mutable copy of the Appendix B conformance fixture."""
    return json.loads(APPENDIX_B.read_text(encoding="utf-8"))


def write_config(tmp_path: Path, config: dict) -> Path:
    """Write a candidate match config and return its path."""
    path = tmp_path / "match.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def test_appendix_b_fixture_carries_neither_disputed_field() -> None:
    config = base_config()
    assert "version" not in config and "extensions" not in config


def test_appendix_b_structure_is_accepted() -> None:
    assert load_match_contract(PROJECT_ROOT, APPENDIX_B).game == base_config()


def test_our_own_example_with_both_fields_is_still_accepted() -> None:
    assert load_match_contract(PROJECT_ROOT, EXAMPLE).game["version"] == "1.00"


def test_optional_extensions_alone_is_accepted(tmp_path: Path) -> None:
    config = base_config()
    config["extensions"] = {}
    assert load_match_contract(PROJECT_ROOT, write_config(tmp_path, config)).game == config


def test_unknown_root_field_is_still_rejected(tmp_path: Path) -> None:
    config = base_config()
    config["unexpected"] = 1
    with pytest.raises(ContractValidationError, match="match config"):
        load_match_contract(PROJECT_ROOT, write_config(tmp_path, config))


def test_genuinely_missing_section_is_still_rejected(tmp_path: Path) -> None:
    config = base_config()
    del config["board_and_agents"]
    with pytest.raises(ContractValidationError, match="match config"):
        load_match_contract(PROJECT_ROOT, write_config(tmp_path, config))
