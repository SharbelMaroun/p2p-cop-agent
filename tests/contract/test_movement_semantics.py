"""Prove movement legality against the real shared config start cells."""

from pathlib import Path

from p2p_cop_agent import CopSDK
from p2p_cop_agent.domain import Action, Board, Coordinate, legal_moves

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"


def _board_and_section() -> tuple[Board, dict]:
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    section = sdk.game_config["board_and_agents"]
    assert isinstance(section, dict)
    return Board.from_config(sdk.game_config), section


def test_cop_start_corner_allows_only_inward_moves() -> None:
    """cop_start [0,0] on the top-left 7x7 board can go SOUTH, EAST, or STAY."""
    board, section = _board_and_section()
    cop_start = Coordinate.from_pair(section["cop_start"])
    assert legal_moves(board, cop_start) == (Action.SOUTH, Action.EAST, Action.STAY)


def test_thief_start_interior_allows_every_action() -> None:
    """thief_start [3,3] is interior, so all five actions stay on the board."""
    board, section = _board_and_section()
    thief_start = Coordinate.from_pair(section["thief_start"])
    assert legal_moves(board, thief_start) == (
        Action.NORTH,
        Action.SOUTH,
        Action.EAST,
        Action.WEST,
        Action.STAY,
    )
