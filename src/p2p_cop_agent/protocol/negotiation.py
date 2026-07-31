"""Pre-play negotiation: build an offer, and refuse a mismatched one (M5-04).

An offer carries the **terms projection** (a strict subset of the match config),
a public challenge nonce, a signature over those terms, and this peer's identity.
``config_sha256`` is always computed over the **complete** game object, never over
the projection -- the projection is what gets signed, the whole object is what
gets hashed. Both facts are pinned by
``shared_contract/fixtures/negotiation_terms.projection.json``.

Verified against the reference implementation on 2026-07-31: the signature covers
the terms with the nonce concatenated outside behind ``|`` (the same construction
as a per-turn commitment, a different domain), the message carries **no role**
because roles alternate across sub-games, and ``game_id``/``game_uid`` are *not*
members of the signed terms -- they are derived from shared inputs and appear only
in emitted artifacts. Adding them here would break every cross-peer signature.

Appendix E rule 11 requires refusing to play on any mismatch, and rule 12 forbids
lowering a `Minimum` parameter, so both are enforced before a match may start.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_cop_agent.protocol.commit import generate_commitment_nonce, move_commit, verify_commit
from p2p_cop_agent.shared.config import JsonObject

# Signed-terms projection: term name -> (section, key) in the match config.
TERM_SOURCES: tuple[tuple[str, tuple[str, str]], ...] = (
    ("board_size", ("board_and_agents", "grid_size")),
    ("smell_grid_size", ("pheromones", "pheromone_grid_size")),
    ("decay_per_step", ("pheromones", "pheromone_decay")),
    ("emit_intensity", ("pheromones", "pheromone_center_intensity")),
    ("max_steps", ("movement_and_barriers", "max_moves")),
    ("barriers_max", ("movement_and_barriers", "max_barriers")),
    ("setting", ("world", "map_area")),
    ("hint_max_words", ("world", "hint_max_words")),
    ("axis_origin_corner", ("board_and_agents", "axis_origin_corner")),
    ("axis_start_index", ("board_and_agents", "axis_start_index")),
    ("thief_start", ("board_and_agents", "thief_start")),
    ("cop_start", ("board_and_agents", "cop_start")),
    ("num_games", ("network_and_league", "num_games")),
)
# Tolerated simulator-profile extra; absent from Appendix F, so never required.
OPTIONAL_TERM = ("min_center_intensity", ("pheromones", "pheromone_min_center_intensity"))

# Appendix F `Fixed`: deviation is disqualification (rule 12).
FIXED_TERMS: JsonObject = {
    "smell_grid_size": 5,
    "decay_per_step": 0.10,
    "emit_intensity": 0.9,
    "num_games": 6,
}
# Appendix F `Minimum`: may be raised by agreement, never lowered (rule 12).
MINIMUM_TERMS: JsonObject = {"board_size": 7, "max_steps": 35, "barriers_max": 14}


class NegotiationError(ValueError):
    """Raised when an offer is malformed, unsigned, or not mutually acceptable."""


def terms_from_config(game: Mapping[str, object]) -> JsonObject:
    """Project a complete match object into the exact signed-terms subset."""
    terms: JsonObject = {}
    for name, (section, key) in TERM_SOURCES:
        block = game.get(section)
        if not isinstance(block, Mapping) or key not in block:
            raise NegotiationError(f"match config is missing {section}.{key}")
        terms[name] = block[key]
    name, (section, key) = OPTIONAL_TERM
    block = game.get(section)
    if isinstance(block, Mapping) and key in block:
        terms[name] = block[key]
    return terms


def check_appendix_f(terms: Mapping[str, object]) -> None:
    """Reject altered `Fixed` values and lowered `Minimum` values (rule 12)."""
    for name, required in FIXED_TERMS.items():
        if terms.get(name) != required:
            raise NegotiationError(
                f"{name} is Fixed at {required}; offer carries {terms.get(name)!r}"
            )
    for name, floor in MINIMUM_TERMS.items():
        value = terms.get(name)
        if not isinstance(value, int) or isinstance(value, bool):
            raise NegotiationError(f"{name} must be an integer, got {value!r}")
        if value < floor:  # type: ignore[operator]
            raise NegotiationError(f"{name} is a Minimum of {floor}; offer lowers it to {value}")


def validate_participants(game: Mapping[str, object], group_id: object) -> None:
    """Require exactly two distinct named participants, including the offerer.

    ``agreed_between`` lives inside the hashed game object, so both peers already
    hold the same ordering; what still needs checking is that it names two real
    and distinct groups and that the offering peer is one of them.
    """
    participants = game.get("agreed_between")
    if not isinstance(participants, list) or len(participants) != 2:
        raise NegotiationError("agreed_between must name exactly two participants")
    if not all(isinstance(name, str) and name.strip() for name in participants):
        raise NegotiationError("agreed_between entries must be non-empty strings")
    if participants[0] == participants[1]:
        raise NegotiationError("agreed_between must name two distinct participants")
    if group_id is not None and group_id not in participants:
        raise NegotiationError(f"offering group {group_id!r} is not in agreed_between")


def build_offer(
    game: Mapping[str, object],
    identity: Mapping[str, object],
    *,
    nonce: str | None = None,
) -> JsonObject:
    """Return a signed negotiation offer for this match (M5-04a).

    The nonce is the **public** negotiation challenge. It is generated with the
    same entropy source as a commitment nonce but is a distinct domain value and
    is never reused as one (`C-020`).
    """
    terms = terms_from_config(game)
    check_appendix_f(terms)
    validate_participants(game, identity.get("group_id"))
    challenge = nonce or generate_commitment_nonce()
    return {
        "terms": terms,
        "nonce": challenge,
        "signature": move_commit(terms, challenge),
        "identity": dict(identity),
    }


def verify_offer(offer: Mapping[str, object], expected_terms: Mapping[str, object]) -> JsonObject:
    """Accept an opponent's offer, or raise naming exactly what disagrees.

    Order matters: structure, then signature, then Appendix F, then equality with
    our own terms. A peer learns *why* it was refused, which rule 11 requires.
    """
    for field in ("terms", "nonce", "signature"):
        if field not in offer:
            raise NegotiationError(f"offer is missing {field!r}")
    terms = offer["terms"]
    if not isinstance(terms, Mapping):
        raise NegotiationError("offer terms must be an object")
    if not verify_commit(dict(terms), offer["nonce"], offer["signature"]):  # type: ignore[arg-type]
        raise NegotiationError("offer signature does not cover the offered terms")
    check_appendix_f(terms)
    differing = sorted(
        key
        for key in set(terms) | set(expected_terms)
        if terms.get(key) != expected_terms.get(key)
    )
    if differing:
        raise NegotiationError(f"negotiated terms differ on: {', '.join(differing)}")
    return dict(terms)
