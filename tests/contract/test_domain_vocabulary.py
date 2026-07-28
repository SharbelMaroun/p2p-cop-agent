"""Prove the domain move vocabulary matches the Fixed shared move set."""

from pathlib import Path

from p2p_cop_agent import CopSDK
from p2p_cop_agent.domain import Action

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_action_vocabulary_matches_shared_move_set() -> None:
    """The domain enum must equal the Fixed Appendix F move_set exactly."""
    sdk = CopSDK.from_repository(PROJECT_ROOT)
    movement = sdk.game_config["movement_and_barriers"]
    assert isinstance(movement, dict)
    assert list(Action.tokens()) == movement["move_set"]
