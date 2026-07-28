"""Tests for immutable Cop-local state and its truth boundary."""

import dataclasses
import json
from pathlib import Path

import pytest

from p2p_cop_agent.domain import Action, BoardError, Coordinate, MovementError
from p2p_cop_agent.orchestration import CopState, StateError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"


def base_config() -> dict:
    """Return a mutable copy of the example match config."""
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def state() -> CopState:
    """Return the opening Cop-local state from the example config."""
    return CopState.opening(base_config())


def test_no_field_can_hold_an_opponent_position() -> None:
    names = {field.name for field in dataclasses.fields(CopState)}
    assert names == {"board", "position", "barriers", "turn"}


def test_opening_state_comes_from_the_negotiated_configuration() -> None:
    opening = state()
    assert (opening.position, opening.turn, opening.barriers.max_barriers) == (
        Coordinate(0, 0),
        0,
        14,
    )


def test_opening_discards_the_configured_thief_start() -> None:
    first = base_config()
    second = base_config()
    second["board_and_agents"]["thief_start"] = [5, 6]
    assert CopState.opening(first) == CopState.opening(second)


def test_state_is_immutable() -> None:
    with pytest.raises(AttributeError):
        state().turn = 5  # type: ignore[misc]


def test_moving_returns_a_new_state_and_leaves_the_original_intact() -> None:
    opening = state()
    moved = opening.moved(Action.SOUTH)
    assert (moved.position, opening.position) == (Coordinate(1, 0), Coordinate(0, 0))


def test_illegal_move_is_rejected() -> None:
    with pytest.raises(MovementError, match="is not a legal move"):
        state().moved(Action.NORTH)


def test_legal_actions_respect_placed_barriers() -> None:
    blocked = state().with_barrier_at(Coordinate(1, 0))
    assert Action.SOUTH not in blocked.legal_actions()


def test_barrier_placement_is_recorded_and_disclosed() -> None:
    placed = state().with_barrier_at(Coordinate(0, 1))
    assert placed.barriers.has_barrier(Coordinate(0, 1)) and placed.barriers.count == 1


def test_next_turn_advances_only_the_counter() -> None:
    advanced = state().next_turn()
    assert (advanced.turn, advanced.position) == (1, Coordinate(0, 0))


def test_rejects_an_off_board_position() -> None:
    opening = state()
    with pytest.raises(BoardError, match="outside board bounds"):
        dataclasses.replace(opening, position=Coordinate(9, 9))


def test_rejects_a_negative_turn() -> None:
    with pytest.raises(StateError, match="turn must not be negative"):
        dataclasses.replace(state(), turn=-1)


def test_rejects_a_non_integer_turn() -> None:
    with pytest.raises(StateError, match="turn must be an integer"):
        dataclasses.replace(state(), turn="1")


def test_rejects_a_missing_movement_section() -> None:
    config = base_config()
    del config["movement_and_barriers"]
    with pytest.raises(StateError, match="missing a movement_and_barriers object"):
        CopState.opening(config)


def test_rejects_a_non_integer_barrier_quota() -> None:
    config = base_config()
    config["movement_and_barriers"]["max_barriers"] = "14"
    with pytest.raises(StateError, match="max_barriers must be an integer"):
        CopState.opening(config)
