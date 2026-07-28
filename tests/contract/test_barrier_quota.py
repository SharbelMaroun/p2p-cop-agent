"""Prove the barrier quota derives from the shared config."""

from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.domain import BarrierError, BarrierField, Board, Coordinate

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _sdk_field_and_board() -> tuple[BarrierField, Board]:
    sdk = CopSDK.from_repository(PROJECT_ROOT)
    return BarrierField.from_config(sdk.game_config), Board.from_config(sdk.game_config)


def test_barrier_quota_matches_shared_config() -> None:
    """config/game.json sets the Appendix F Minimum-14 barrier quota."""
    field, _ = _sdk_field_and_board()
    assert field.max_barriers == 14
    assert field.remaining == 14


def test_quota_is_exhausted_after_the_configured_maximum() -> None:
    """Placing max_barriers cells exhausts the quota and blocks one more."""
    field, board = _sdk_field_and_board()
    cells = [Coordinate(row, col) for row in range(7) for col in range(7)]

    for cell in cells[: field.max_barriers]:
        field = field.place(board, cell)

    assert field.count == 14
    assert field.remaining == 0
    with pytest.raises(BarrierError, match="is exhausted"):
        field.place(board, cells[field.max_barriers])
