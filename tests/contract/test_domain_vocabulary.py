"""Prove the domain move vocabulary matches the Fixed shared move set."""

from pathlib import Path

from p2p_cop_agent import CopSDK
from p2p_cop_agent.domain import Action

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"


def test_action_vocabulary_matches_shared_move_set() -> None:
    """The domain enum must equal the Fixed Appendix F move_set exactly."""
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    movement = sdk.game_config["movement_and_barriers"]
    assert isinstance(movement, dict)
    assert list(Action.tokens()) == movement["move_set"]
