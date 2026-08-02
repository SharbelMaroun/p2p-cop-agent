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
from p2p_cop_agent.orchestration.negotiation_handshake import (
    Agreement,
    HandshakeError,
    negotiate_match,
)
from p2p_cop_agent.orchestration.orchestrator import Orchestrator
from p2p_cop_agent.orchestration.phases import (
    TRANSITIONS,
    TURN_CYCLE,
    Phase,
    PhaseError,
    PhaseMachine,
)
from p2p_cop_agent.orchestration.polling import (
    DEFAULT_POLL_INTERVAL,
    PollingError,
    poll_for_turn,
    turn_receiver,
)
from p2p_cop_agent.orchestration.ports import (
    DeadlineTracker,
    DecisionModule,
    LivenessWatchdog,
    LogManager,
    MCPConnector,
)
from p2p_cop_agent.orchestration.shutdown import (
    ShutdownError,
    ShutdownReport,
    controlled_shutdown,
    heartbeat_on_transition,
)
from p2p_cop_agent.orchestration.state import CopState, StateError
from p2p_cop_agent.orchestration.sub_game import (
    RESULT_CLAIMS,
    SubGameOutcome,
    run_sub_game_over_wire,
)
from p2p_cop_agent.orchestration.turn_loop import TurnLoopError, TurnRecord, run_turn

__all__ = [
    "DEFAULT_POLL_INTERVAL",
    "PROJECT_PROPOSED_TURN_ORDER",
    "RESULT_CLAIMS",
    "TRANSITIONS",
    "TURN_CYCLE",
    "Agreement",
    "CopHistory",
    "CopState",
    "HandshakeError",
    "DeadlineTracker",
    "DecisionModule",
    "LivenessWatchdog",
    "LogManager",
    "MCPConnector",
    "Orchestrator",
    "Phase",
    "PhaseError",
    "PhaseMachine",
    "PollingError",
    "ShutdownError",
    "ShutdownReport",
    "StateError",
    "SubGameOutcome",
    "controlled_shutdown",
    "heartbeat_on_transition",
    "SubGameResult",
    "TurnLoopError",
    "TurnRecord",
    "TurnEvent",
    "TurnOrder",
    "negotiate_match",
    "poll_for_turn",
    "run_sub_game",
    "run_sub_game_over_wire",
    "run_turn",
    "turn_receiver",
]
