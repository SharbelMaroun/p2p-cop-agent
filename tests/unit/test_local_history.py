"""Tests for append-only, reproducible Cop-local history."""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.domain import Action, Coordinate, MovementError
from p2p_cop_agent.orchestration import CopHistory, CopState, StateError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
WALK = (Action.SOUTH, Action.EAST, Action.SOUTH, Action.STAY, Action.EAST)


def opening() -> CopState:
    """Return the opening Cop-local state from the example config."""
    return CopState.opening(json.loads(EXAMPLE.read_text(encoding="utf-8")))


def history() -> CopHistory:
    """Return a history holding only the opening state."""
    return CopHistory.starting(opening())


def test_history_starts_with_the_opening_state() -> None:
    started = history()
    assert len(started) == 1 and started.current == started.opening


def test_identical_input_produces_an_equal_history() -> None:
    assert history().apply_all(WALK) == history().apply_all(WALK)


def test_identical_input_produces_the_same_positions() -> None:
    assert history().apply_all(WALK).positions == history().apply_all(WALK).positions


def test_recording_does_not_mutate_the_earlier_history() -> None:
    started = history()
    started.apply_all(WALK)
    assert len(started) == 1


def test_history_grows_by_one_per_action() -> None:
    assert len(history().apply_all(WALK)) == len(WALK) + 1


def test_opening_snapshot_survives_every_later_action() -> None:
    walked = history().apply_all(WALK)
    assert walked.opening.position == Coordinate(0, 0)


def test_current_tracks_the_latest_state() -> None:
    assert history().apply(Action.SOUTH).current.position == Coordinate(1, 0)


def test_snapshots_are_ordered_oldest_first() -> None:
    positions = tuple(state.position for state in history().apply(Action.SOUTH))
    assert positions == (Coordinate(0, 0), Coordinate(1, 0))


def test_stay_records_a_snapshot_without_moving() -> None:
    stayed = history().apply(Action.STAY)
    assert len(stayed) == 2 and stayed.current.position == Coordinate(0, 0)


def test_an_illegal_action_records_nothing() -> None:
    started = history()
    with pytest.raises(MovementError, match="is not a legal move"):
        started.apply(Action.NORTH)
    assert len(started) == 1


def test_rejects_an_empty_history() -> None:
    with pytest.raises(StateError, match="at least the opening state"):
        CopHistory(())


def test_rejects_a_non_state_entry() -> None:
    with pytest.raises(StateError, match="must be a CopState"):
        CopHistory((opening(), "not-a-state"))  # type: ignore[arg-type]
