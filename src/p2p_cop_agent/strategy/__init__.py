"""Cop strategy boundary: deterministic, contract-independent policy only."""

from p2p_cop_agent.strategy.barrier_policy import (
    BarrierIntent,
    MoveIntent,
    TurnIntent,
    choose_turn_intent,
)
from p2p_cop_agent.strategy.belief import (
    Belief,
    BeliefError,
    scent_likelihood,
)
from p2p_cop_agent.strategy.belief_pursuit import (
    belief_target,
    belief_turn_intent,
    pursue_belief,
)
from p2p_cop_agent.strategy.hints import (
    HINT_MAX_WORDS_DEFAULT,
    Hint,
    HintError,
    encodes_coordinates,
    hint_max_words,
    template_hint,
    validate_hint,
)
from p2p_cop_agent.strategy.pursuit import choose_action, step_distances
from p2p_cop_agent.strategy.scent import (
    CENTER_INTENSITY,
    DECAY_RATE,
    DEFAULT_OUTER_RING_DELTA,
    DOCUMENTED_EMISSION,
    FIELD_SIZE,
    OUTER_RING_OFFSETS,
    ScentModelError,
    decay,
    emission_field,
    emission_offsets,
    require_outer_ring,
)
from p2p_cop_agent.strategy.scent_lock import (
    SCENT_LOCK_FIELD,
    SCENT_OUTER_RING_FIELD,
    ScentLockError,
    assert_scent_locked,
    scent_model_hash,
    scent_model_record,
    verify_peer_scent_lock,
)

__all__ = [
    "CENTER_INTENSITY",
    "DECAY_RATE",
    "DEFAULT_OUTER_RING_DELTA",
    "DOCUMENTED_EMISSION",
    "FIELD_SIZE",
    "HINT_MAX_WORDS_DEFAULT",
    "OUTER_RING_OFFSETS",
    "SCENT_LOCK_FIELD",
    "SCENT_OUTER_RING_FIELD",
    "BarrierIntent",
    "Belief",
    "BeliefError",
    "Hint",
    "HintError",
    "MoveIntent",
    "ScentLockError",
    "ScentModelError",
    "TurnIntent",
    "assert_scent_locked",
    "belief_target",
    "belief_turn_intent",
    "choose_action",
    "choose_turn_intent",
    "decay",
    "emission_field",
    "emission_offsets",
    "encodes_coordinates",
    "hint_max_words",
    "pursue_belief",
    "require_outer_ring",
    "scent_likelihood",
    "scent_model_hash",
    "scent_model_record",
    "step_distances",
    "template_hint",
    "validate_hint",
    "verify_peer_scent_lock",
]
