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
from p2p_cop_agent.strategy.consume import Perception, consume_turn
from p2p_cop_agent.strategy.hint_consumption import (
    NEUTRAL_TRUST,
    TRUST_UPDATE_RATE,
    ReceivedHint,
    TrustScore,
    hint_weight,
    receive_hint,
)
from p2p_cop_agent.strategy.hint_decode import (
    DIRECTION_WORDS,
    decode_hint,
    hint_directions,
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
from p2p_cop_agent.strategy.landmarks import (
    GENERIC_BEARINGS,
    LANDMARKS,
    map_area,
    place_for,
    vocabulary,
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
from p2p_cop_agent.strategy.scent_field import SILENCE_FLOOR, ScentField
from p2p_cop_agent.strategy.scent_lock import (
    SCENT_LOCK_FIELD,
    SCENT_OUTER_RING_FIELD,
    ScentLockError,
    assert_scent_locked,
    scent_model_hash,
    scent_model_record,
    verify_peer_scent_lock,
)
from p2p_cop_agent.strategy.squeeze import (
    MIN_ESCAPES_REMOVED,
    choose_squeeze,
    escape_routes,
    legal_barrier_cells,
    obstructs_our_own_path,
)
from p2p_cop_agent.strategy.trust import (
    NEUTRAL_SUPPORT,
    apply_support,
    corroboration,
    expected_fresh_scent,
    trust_weighted,
)
from p2p_cop_agent.strategy.verbal import (
    HintProviderError,
    generate_hint,
    is_model_turn,
    openai_provider,
    provider_from_config,
)

__all__ = [
    "GENERIC_BEARINGS", "LANDMARKS", "map_area", "place_for", "vocabulary",
    "BarrierIntent", "Belief", "BeliefError", "CENTER_INTENSITY", "DECAY_RATE", "DEFAULT_OUTER_RING_DELTA",
    "DIRECTION_WORDS", "DOCUMENTED_EMISSION", "FIELD_SIZE", "HINT_MAX_WORDS_DEFAULT",
    "Hint", "HintError", "HintProviderError", "MIN_ESCAPES_REMOVED", "MoveIntent", "NEUTRAL_SUPPORT",
    "NEUTRAL_TRUST", "OUTER_RING_OFFSETS", "Perception", "ReceivedHint", "SCENT_LOCK_FIELD",
    "SCENT_OUTER_RING_FIELD", "SILENCE_FLOOR", "ScentField", "ScentLockError", "ScentModelError",
    "TRUST_UPDATE_RATE", "TrustScore", "TurnIntent", "apply_support", "assert_scent_locked",
    "belief_target", "belief_turn_intent", "choose_action", "choose_squeeze", "choose_turn_intent",
    "consume_turn", "corroboration", "decay", "decode_hint", "emission_field", "emission_offsets",
    "encodes_coordinates", "escape_routes", "expected_fresh_scent", "generate_hint",
    "hint_directions", "hint_max_words", "hint_weight", "is_model_turn", "legal_barrier_cells",
    "obstructs_our_own_path", "openai_provider", "provider_from_config", "pursue_belief",
    "receive_hint", "require_outer_ring", "scent_likelihood", "scent_model_hash", "scent_model_record",
    "step_distances", "template_hint", "trust_weighted", "validate_hint", "verify_peer_scent_lock",
]
