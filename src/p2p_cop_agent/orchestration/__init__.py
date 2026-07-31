"""Cop orchestration boundary: local state, history, and a rules harness.

Transport stays absent; the harness is a single-process referee, not a peer.
"""

from p2p_cop_agent.orchestration.harness import (
    PROJECT_PROPOSED_TURN_ORDER,
    SubGameResult,
    TurnEvent,
    TurnOrder,
    run_sub_game,
)
from p2p_cop_agent.orchestration.history import CopHistory
from p2p_cop_agent.orchestration.phases import (
    TRANSITIONS,
    TURN_CYCLE,
    Phase,
    PhaseError,
    PhaseMachine,
)
from p2p_cop_agent.orchestration.state import CopState, StateError

__all__ = [
    "PROJECT_PROPOSED_TURN_ORDER",
    "TRANSITIONS",
    "TURN_CYCLE",
    "CopHistory",
    "CopState",
    "Phase",
    "PhaseError",
    "PhaseMachine",
    "StateError",
    "SubGameResult",
    "TurnEvent",
    "TurnOrder",
    "run_sub_game",
]
