"""Prove board geometry derives correctly from the shared config."""

from pathlib import Path

from p2p_cop_agent import CopSDK
from p2p_cop_agent.domain import Board, Coordinate

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"


def test_board_geometry_matches_shared_config() -> None:
    """A board built from the explicit example match spans the negotiated 7x7 grid."""
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    board = Board.from_config(sdk.game_config)

    assert board.grid_size == 7
    assert (board.min_index, board.max_index) == (0, 6)
    assert board.axis_origin_corner == "top-left"


def test_configured_start_cells_are_on_the_board() -> None:
    """The negotiated cop and thief start cells must lie on the board."""
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    board = Board.from_config(sdk.game_config)
    section = sdk.game_config["board_and_agents"]
    assert isinstance(section, dict)

    assert board.contains(Coordinate.from_pair(section["cop_start"]))
    assert board.contains(Coordinate.from_pair(section["thief_start"]))
