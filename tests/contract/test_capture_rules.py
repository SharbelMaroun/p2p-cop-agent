"""Prove capture conditions against the real shared config start cells."""

from pathlib import Path

from p2p_cop_agent import CopSDK
from p2p_cop_agent.domain import (
    BarrierField,
    Board,
    CaptureReason,
    Coordinate,
    capture_reason,
    is_captured,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"


def _board_starts_and_field() -> tuple[Board, Coordinate, Coordinate, BarrierField]:
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    board = Board.from_config(sdk.game_config)
    field = BarrierField.from_config(sdk.game_config)
    section = sdk.game_config["board_and_agents"]
    assert isinstance(section, dict)
    cop = Coordinate.from_pair(section["cop_start"])
    thief = Coordinate.from_pair(section["thief_start"])
    return board, cop, thief, field


def test_start_positions_are_not_a_capture() -> None:
    """cop_start [0,0] and thief_start [3,3] are not a capture at kickoff."""
    board, cop, thief, field = _board_starts_and_field()
    assert is_captured(board, cop, thief, field) is False


def test_cop_landing_on_thief_start_is_a_capture() -> None:
    board, _cop, thief, field = _board_starts_and_field()
    assert capture_reason(board, thief, thief, field) is CaptureReason.COP_ON_THIEF


def test_barrier_on_thief_start_is_a_capture() -> None:
    board, cop, thief, field = _board_starts_and_field()
    placed = field.place(board, thief)
    assert capture_reason(board, cop, thief, placed) is CaptureReason.BARRIER_ON_THIEF
