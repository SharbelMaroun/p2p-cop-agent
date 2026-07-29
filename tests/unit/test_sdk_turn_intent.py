"""Tests for SDK-reachable deterministic move-or-barrier decisions."""

from pathlib import Path

from p2p_cop_agent import CopSDK
from p2p_cop_agent.domain import BarrierField, Coordinate
from p2p_cop_agent.strategy import BarrierIntent, MoveIntent

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"


def sdk() -> CopSDK:
    """Return an SDK bound to the example match configuration."""
    return CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)


def test_sdk_exposes_the_barrier_aware_turn_decision() -> None:
    instance = sdk()
    barriers = BarrierField(max_barriers=14).place(instance.board(), Coordinate(1, 0))
    intent = instance.choose_turn_intent(
        cop=Coordinate(0, 2),
        target=Coordinate(0, 0),
        barriers=barriers,
    )
    assert intent == BarrierIntent(Coordinate(0, 1))


def test_sdk_turn_decision_falls_back_to_movement_without_quota() -> None:
    intent = sdk().choose_turn_intent(
        cop=Coordinate(6, 6),
        target=Coordinate(0, 0),
        barriers=BarrierField(max_barriers=0),
    )
    assert isinstance(intent, MoveIntent)
