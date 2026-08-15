"""C-047: a negotiate without an `identity` object is accepted.

Group `yanell11` carry their group id at the TOP LEVEL and send no `identity` object at
all. Our schema made `identity` required, so `InboundPeer.negotiate` -- which validates
before `verify_offer` ever runs -- refused the whole message with
`'identity' is a required property`, and the live friendly on 2026-08-15 died there.

That contradicted our own recorded decision. `C-031`/`U-029` settled this as "populate
ours, tolerate theirs", and `verify_offer` implements it faithfully (it requires only
`terms`, `nonce`, `signature`). Schema validation ran first, so the tolerance was
unreachable -- documented but never true.

The key set below is the one our own wire recorder captured from their live message,
not a reconstruction.
"""

from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.peer.inbound import InboundPeer
from p2p_cop_agent.protocol.messages import ProtocolError, validate_message

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = ROOT / "config" / "rate_limits.json"


def _sdk() -> CopSDK:
    return CopSDK.from_repository(ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)

TERMS = {"board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.1,
         "emit_intensity": 0.9, "min_center_intensity": 0.5, "max_steps": 35,
         "barriers_max": 14, "setting": "Haifa", "hint_max_words": 15,
         "axis_origin_corner": "top-left", "axis_start_index": 0,
         "thief_start": [3, 3], "cop_start": [0, 0], "num_games": 6}

# Verbatim from `games/friendly-yanell11-0815/logs/wire.jsonl`, 2026-08-15T18:04:08Z.
THEIR_KEYS = ("counted_games_played", "group_id", "info_mode_sha256", "interop_profile",
              "nonce", "role", "scent_model_sha256", "signature", "step0_commit",
              "sub_game_number", "terms", "tie_award", "turn_order", "wire_shape_sha256")


def their_offer(**overrides: object) -> dict:
    """A negotiate with exactly the members their peer sent."""
    offer = {"counted_games_played": 0, "group_id": "yanell11",
             "info_mode_sha256": "aa" * 32, "interop_profile": "reference-v3",
             "nonce": "cc" * 16, "role": "thief", "scent_model_sha256": "bb" * 32,
             "signature": "dd" * 32, "step0_commit": "ee" * 32, "sub_game_number": 1,
             "terms": dict(TERMS), "tie_award": 2, "turn_order": "thief_first",
             "wire_shape_sha256": "ff" * 32}
    offer.update(overrides)
    return offer


def test_the_captured_message_shape_is_what_we_think_it_is() -> None:
    """Guards the fixture itself: if it drifts from the wire log it proves nothing."""
    assert tuple(sorted(their_offer())) == tuple(sorted(THEIR_KEYS))


def test_a_negotiate_without_identity_validates() -> None:
    validate_message("negotiate", their_offer())


def test_the_group_id_is_read_from_the_top_level() -> None:
    """`identity` absent: fall back to the top-level spelling rather than raising."""
    peer = InboundPeer(_sdk())
    peer.negotiate(their_offer())
    assert peer.opponent_group == "yanell11"


def test_the_group_id_is_still_read_from_identity_when_present() -> None:
    """The reference-shaped peer keeps working; this is a widening, not a swap."""
    peer = InboundPeer(_sdk())
    peer.negotiate(their_offer(identity={"group_id": "uoh-ay26"}))
    assert peer.opponent_group == "uoh-ay26"


def test_an_absent_group_id_is_not_fatal() -> None:
    """It labels our logs; it authorizes nothing, so `None` is a legitimate outcome."""
    offer = their_offer()
    del offer["group_id"]
    peer = InboundPeer(_sdk())
    peer.negotiate(offer)
    assert peer.opponent_group is None


def test_the_required_members_are_still_required() -> None:
    """Widening `identity` must not have loosened what actually carries the agreement."""
    for member in ("terms", "nonce", "signature"):
        offer = their_offer()
        del offer[member]
        with pytest.raises(ProtocolError):
            validate_message("negotiate", offer)
