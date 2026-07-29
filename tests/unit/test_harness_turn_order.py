"""Tests for injectable local-referee events and Cop turn intents."""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.domain import (
    Action,
    BarrierField,
    Board,
    CaptureReason,
    Coordinate,
    Outcome,
)
from p2p_cop_agent.orchestration import CopState, StateError, TurnEvent, run_sub_game
from p2p_cop_agent.strategy import BarrierIntent, MoveIntent

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"


def adjacent_config() -> dict:
    """Return a one-turn game with adjacent opening cells."""
    config = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    config["board_and_agents"]["cop_start"] = [0, 0]
    config["board_and_agents"]["thief_start"] = [0, 1]
    config["movement_and_barriers"]["survival_threshold"] = 1
    return config


def east_cop(state: CopState) -> MoveIntent:
    """Move east using Cop-local state only."""
    return MoveIntent(Action.EAST)


def east_thief(
    board: Board,
    thief: Coordinate,
    cop: Coordinate,
    barriers: BarrierField,
) -> Action:
    """Move east without depending on a specific opponent implementation."""
    return Action.EAST


def test_default_schedule_preserves_thief_first_proposal() -> None:
    result = run_sub_game(adjacent_config(), east_cop, east_thief)
    assert result.outcome is Outcome.SURVIVAL


def test_cop_first_schedule_can_capture_before_the_thief_acts() -> None:
    thief_called = False

    def unexpected_thief(
        board: Board,
        thief: Coordinate,
        cop: Coordinate,
        barriers: BarrierField,
    ) -> Action:
        nonlocal thief_called
        thief_called = True
        return Action.EAST

    order = (
        TurnEvent.COP_ACTION,
        TurnEvent.CAPTURE_CHECK,
        TurnEvent.THIEF_ACTION,
        TurnEvent.CAPTURE_CHECK,
    )
    result = run_sub_game(adjacent_config(), east_cop, unexpected_thief, turn_order=order)
    assert result.reason is CaptureReason.COP_ON_THIEF
    assert not thief_called


def test_capture_checkpoint_position_is_injectable() -> None:
    order = (
        TurnEvent.COP_ACTION,
        TurnEvent.THIEF_ACTION,
        TurnEvent.CAPTURE_CHECK,
    )
    result = run_sub_game(adjacent_config(), east_cop, east_thief, turn_order=order)
    assert result.outcome is Outcome.SURVIVAL


def test_harness_executes_a_barrier_intent() -> None:
    config = adjacent_config()
    config["board_and_agents"]["cop_start"] = [0, 1]
    config["board_and_agents"]["thief_start"] = [0, 0]
    order = (
        TurnEvent.COP_ACTION,
        TurnEvent.CAPTURE_CHECK,
        TurnEvent.THIEF_ACTION,
    )
    def barrier_cop(state: CopState) -> BarrierIntent:
        return BarrierIntent(Coordinate(0, 0))

    result = run_sub_game(config, barrier_cop, east_thief, turn_order=order)
    assert result.reason is CaptureReason.BARRIER_ON_THIEF


@pytest.mark.parametrize(
    ("order", "message"),
    [
        ((TurnEvent.COP_ACTION, TurnEvent.CAPTURE_CHECK), "THIEF_ACTION"),
        ((TurnEvent.THIEF_ACTION, TurnEvent.CAPTURE_CHECK), "COP_ACTION"),
        ((TurnEvent.THIEF_ACTION, TurnEvent.COP_ACTION), "CAPTURE_CHECK"),
        ((TurnEvent.THIEF_ACTION, TurnEvent.THIEF_ACTION, TurnEvent.COP_ACTION), "THIEF_ACTION"),
        (("thief", TurnEvent.COP_ACTION, TurnEvent.CAPTURE_CHECK), "TurnEvent"),
        ([TurnEvent.THIEF_ACTION, TurnEvent.COP_ACTION, TurnEvent.CAPTURE_CHECK], "tuple"),
    ],
)
def test_invalid_turn_orders_are_rejected(order: object, message: str) -> None:
    with pytest.raises(StateError, match=message):
        run_sub_game(
            adjacent_config(),
            east_cop,
            east_thief,
            turn_order=order,  # type: ignore[arg-type]
        )


def test_invalid_cop_policy_result_is_rejected() -> None:
    order = (
        TurnEvent.COP_ACTION,
        TurnEvent.CAPTURE_CHECK,
        TurnEvent.THIEF_ACTION,
    )
    with pytest.raises(StateError, match="Action or TurnIntent"):
        run_sub_game(
            adjacent_config(),
            lambda state: object(),  # type: ignore[return-value]
            east_thief,
            turn_order=order,
        )
