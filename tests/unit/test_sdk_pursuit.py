"""Tests for SDK-reachable deterministic pursuit."""

from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.domain import Action, BoardError, Coordinate

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def sdk() -> CopSDK:
    """Return an SDK bound to the repository's example match configuration."""
    return CopSDK.from_repository(PROJECT_ROOT)


def test_board_comes_from_the_negotiated_match_configuration() -> None:
    assert sdk().board().grid_size == 7


def test_pursuit_is_reachable_through_the_sdk() -> None:
    action = sdk().choose_pursuit_action(Coordinate(0, 0), Coordinate(3, 0))
    assert action is Action.SOUTH


def test_sdk_pursuit_respects_supplied_barriers() -> None:
    blocked = frozenset({Coordinate(1, 0)})
    action = sdk().choose_pursuit_action(Coordinate(0, 0), Coordinate(3, 0), blocked)
    assert action is Action.EAST


def test_sdk_pursuit_rejects_cells_outside_the_negotiated_board() -> None:
    with pytest.raises(BoardError, match="outside board bounds"):
        sdk().choose_pursuit_action(Coordinate(0, 0), Coordinate(9, 9))


def test_sdk_pursuit_is_repeatable() -> None:
    instance = sdk()
    calls = [instance.choose_pursuit_action(Coordinate(6, 6), Coordinate(0, 0)) for _ in range(5)]
    assert len(set(calls)) == 1
