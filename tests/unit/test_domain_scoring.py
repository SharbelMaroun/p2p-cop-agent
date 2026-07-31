"""Table-driven tests for fixed scoring and the technical-loss sanction."""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.domain import Outcome, ScoringError, ScoringTable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"


def base_config() -> dict:
    """Return a mutable copy of the example match config."""
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def table() -> ScoringTable:
    """Return the score table built from the example match config."""
    return ScoringTable.from_config(base_config())


@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        (Outcome.CAPTURE, (20, 5)),
        (Outcome.SURVIVAL, (5, 10)),
        (Outcome.TIE, (2, 2)),
        (Outcome.TECHNICAL_LOSS, (0, 0)),
    ],
)
def test_appendix_f_table_17_awards(outcome: Outcome, expected: tuple[int, int]) -> None:
    assert table().award(outcome).as_pair() == expected


def test_technical_loss_is_zero_for_both_peers() -> None:
    """Chapter 3 table 2 and rule 48 fix the row at 0/0 for both sides (`U-026`)."""
    assert table().technical_loss_award() == 0
    assert table().award(Outcome.TECHNICAL_LOSS).as_pair() == (0, 0)


def test_values_come_from_configuration_not_source_constants() -> None:
    config = base_config()
    config["scoring"]["capture_cop"] = 99
    assert ScoringTable.from_config(config).award(Outcome.CAPTURE).cop == 99


def test_rejects_a_missing_scoring_section() -> None:
    config = base_config()
    del config["scoring"]
    with pytest.raises(ScoringError, match="missing a scoring object"):
        ScoringTable.from_config(config)


@pytest.mark.parametrize("bad", [None, "20", 20.0, True])
def test_rejects_non_integer_awards(bad: object) -> None:
    config = base_config()
    config["scoring"]["capture_cop"] = bad
    with pytest.raises(ScoringError, match="capture_cop must be an integer"):
        ScoringTable.from_config(config)


def test_rejects_an_unknown_outcome() -> None:
    with pytest.raises(ScoringError, match="unknown outcome"):
        table().award("capture")  # type: ignore[arg-type]


def test_score_table_is_immutable() -> None:
    with pytest.raises(AttributeError):
        table().capture_cop = 1  # type: ignore[misc]
