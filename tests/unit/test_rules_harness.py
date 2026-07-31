"""Tests for the single-process rules harness.

The Thief policies here are neutral local stubs written for these tests only.
They share no code with any opponent implementation and encode no assumption
about how a real opponent plays.
"""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.domain import (
    Action,
    BarrierField,
    Board,
    BoardError,
    CaptureReason,
    Coordinate,
    Outcome,
    apply_move,
    legal_moves,
)
from p2p_cop_agent.orchestration import CopState, StateError, run_sub_game
from p2p_cop_agent.strategy import choose_action

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"


def base_config() -> dict:
    """Return a mutable copy of the example match config."""
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def pursuing_cop(state: CopState) -> Action:
    """Pursue a caller-supplied presumption without referee private truth."""
    presumed_target = Coordinate(3, 3)
    return choose_action(state.board, state.position, presumed_target, state.blocked)


def motionless_thief(
    board: Board, thief: Coordinate, cop: Coordinate, barriers: BarrierField
) -> Action:
    """Neutral stub: never moves."""
    return Action.STAY


def fleeing_thief(
    board: Board, thief: Coordinate, cop: Coordinate, barriers: BarrierField
) -> Action:
    """Neutral stub: takes the legal action maximising distance from the Cop."""
    return max(
        legal_moves(board, thief, barriers.cells),
        key=lambda action: _distance(board, thief, action, cop),
    )


def _distance(board: Board, thief: Coordinate, action: Action, cop: Coordinate) -> int:
    """Return the Manhattan distance from the Cop after one Thief action."""
    cell = apply_move(board, thief, action, frozenset())
    return abs(cell.row - cop.row) + abs(cell.col - cop.col)


def test_a_motionless_thief_is_captured() -> None:
    result = run_sub_game(base_config(), pursuing_cop, motionless_thief)
    assert result.outcome is Outcome.CAPTURE


def test_capture_awards_the_appendix_f_score() -> None:
    result = run_sub_game(base_config(), pursuing_cop, motionless_thief)
    assert result.score.as_pair() == (20, 5)


def test_capture_records_a_reason_and_a_turn() -> None:
    result = run_sub_game(base_config(), pursuing_cop, motionless_thief)
    assert result.reason is CaptureReason.COP_ON_THIEF and result.turns >= 1


def test_a_passive_cop_lets_the_thief_survive() -> None:
    result = run_sub_game(base_config(), lambda state: Action.STAY, fleeing_thief)
    assert result.outcome is Outcome.SURVIVAL


def test_survival_awards_the_appendix_f_score() -> None:
    result = run_sub_game(base_config(), lambda state: Action.STAY, fleeing_thief)
    assert result.score.as_pair() == (5, 10)


def test_survival_runs_to_the_configured_threshold() -> None:
    config = base_config()
    config["movement_and_barriers"]["survival_threshold"] = 3
    result = run_sub_game(config, lambda state: Action.STAY, fleeing_thief)
    assert result.turns == 3


def test_the_survival_horizon_is_inclusive_at_the_threshold() -> None:
    """Surviving exactly `[Survival Threshold]` turns is a Thief win (`U-027`).

    Chapter 3 table 2 defines survival as surviving "the limit of valid moves", and
    Appendix F table 15 sets the step limit equal to the survival threshold, so the
    boundary turn itself must score as survival rather than run one turn short.
    """
    config = base_config()
    config["movement_and_barriers"]["survival_threshold"] = 1
    result = run_sub_game(config, lambda state: Action.STAY, fleeing_thief)
    assert result.outcome is Outcome.SURVIVAL
    assert result.turns == 1
    assert result.score.as_pair() == (5, 10)


def test_a_capture_on_the_final_turn_still_outranks_survival() -> None:
    """The inclusive horizon must not convert a boundary-turn capture into a win."""
    config = base_config()
    config["movement_and_barriers"]["survival_threshold"] = 1
    config["board_and_agents"]["cop_start"] = [3, 2]
    result = run_sub_game(config, pursuing_cop, motionless_thief)
    assert result.outcome is Outcome.CAPTURE
    assert result.turns == 1


def test_the_sub_game_always_terminates() -> None:
    result = run_sub_game(base_config(), pursuing_cop, fleeing_thief)
    assert result.outcome in (Outcome.CAPTURE, Outcome.SURVIVAL)


def test_identical_input_produces_an_identical_result() -> None:
    first = run_sub_game(base_config(), pursuing_cop, fleeing_thief)
    second = run_sub_game(base_config(), pursuing_cop, fleeing_thief)
    assert first == second


def test_rejects_a_non_positive_survival_threshold() -> None:
    config = base_config()
    config["movement_and_barriers"]["survival_threshold"] = 0
    with pytest.raises(StateError, match="survival_threshold must be a positive integer"):
        run_sub_game(config, pursuing_cop, motionless_thief)


def test_rejects_a_missing_board_section() -> None:
    config = base_config()
    del config["board_and_agents"]
    with pytest.raises(BoardError, match="missing a board_and_agents object"):
        run_sub_game(config, pursuing_cop, motionless_thief)
