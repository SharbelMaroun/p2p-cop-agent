"""M5-04: negotiation offers, and refusal on any mismatch.

The projection and the hashing rule are pinned by the controlled fixture
``negotiation_terms.projection.json``, so these tests check the implementation
against the contract rather than against themselves.
"""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.protocol.negotiation import (
    NegotiationError,
    build_offer,
    check_appendix_f,
    terms_from_config,
    verify_offer,
)
from p2p_cop_agent.shared.contracts import shared_config_sha256

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "shared_contract"
EXAMPLE = BUNDLE / "fixtures" / "match_config.example.json"
PROJECTION = BUNDLE / "fixtures" / "negotiation_terms.projection.json"

IDENTITY = {"group_id": "neutral-group-alpha", "group_name": "Alpha", "members": ["a"]}


def game() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def projection() -> dict:
    return json.loads(PROJECTION.read_text(encoding="utf-8"))


def test_projection_reproduces_the_controlled_fixture() -> None:
    """`terms_from_config` must agree with the bundle, not with our own opinion."""
    fixture = projection()
    assert terms_from_config(fixture["game_object"]) == fixture["negotiation_terms"]


def test_config_hash_covers_the_whole_object_not_the_projection() -> None:
    """The fixture states this explicitly; a peer hashing the subset would diverge."""
    fixture = projection()
    assert shared_config_sha256(fixture["game_object"]) == fixture["game_object_config_sha256"]
    assert shared_config_sha256(fixture["negotiation_terms"]) != fixture[
        "game_object_config_sha256"
    ]


def test_game_id_is_not_a_signed_term() -> None:
    """Verified 2026-07-31: the identifiers are derived, never negotiated.

    Signing them would make the terms differ from a classmate's and refuse every
    match, so this guards against a plausible-looking future 'fix'.
    """
    terms = terms_from_config(game())
    assert "game_id" not in terms and "game_uid" not in terms


def test_offer_carries_terms_challenge_signature_and_identity() -> None:
    offer = build_offer(game(), IDENTITY)
    assert set(offer) == {"terms", "nonce", "signature", "identity"}
    assert offer["identity"]["group_id"] == "neutral-group-alpha"
    assert len(offer["nonce"]) == 32 and len(offer["signature"]) == 64


def test_each_offer_uses_a_fresh_challenge() -> None:
    assert build_offer(game(), IDENTITY)["nonce"] != build_offer(game(), IDENTITY)["nonce"]


def test_an_offer_carries_no_role() -> None:
    """Roles alternate across sub-games, so the wire must not pin one."""
    blob = json.dumps(build_offer(game(), IDENTITY))
    assert "role" not in blob and "sub_game_number" not in blob


def test_an_offer_verifies_against_matching_terms_in_both_directions() -> None:
    expected = terms_from_config(game())
    assert verify_offer(build_offer(game(), IDENTITY), expected) == expected

    other = {"group_id": "neutral-group-beta"}
    assert verify_offer(build_offer(game(), other), expected) == expected


def test_a_tampered_term_breaks_the_signature() -> None:
    offer = build_offer(game(), IDENTITY)
    offer["terms"]["board_size"] = 9
    with pytest.raises(NegotiationError, match="signature"):
        verify_offer(offer, terms_from_config(game()))


def test_a_mismatch_names_the_offending_term() -> None:
    """Rule 11 refusal must be explainable, not a bare rejection."""
    mine = terms_from_config(game()) | {"hint_max_words": 20}
    with pytest.raises(NegotiationError, match="hint_max_words"):
        verify_offer(build_offer(game(), IDENTITY), mine)


@pytest.mark.parametrize("field", ["terms", "nonce", "signature"])
def test_a_structurally_incomplete_offer_is_refused(field: str) -> None:
    offer = build_offer(game(), IDENTITY)
    del offer[field]
    with pytest.raises(NegotiationError, match=field):
        verify_offer(offer, terms_from_config(game()))


@pytest.mark.parametrize(
    ("term", "value"),
    [("smell_grid_size", 3), ("decay_per_step", 0.5), ("emit_intensity", 1.0), ("num_games", 1)],
)
def test_an_altered_fixed_value_is_refused(term: str, value: object) -> None:
    """`[AE-12]`: a Fixed Appendix F parameter may not change at all."""
    with pytest.raises(NegotiationError, match=f"{term} is Fixed"):
        check_appendix_f(terms_from_config(game()) | {term: value})


@pytest.mark.parametrize(("term", "value"), [("board_size", 6), ("max_steps", 34),
                                             ("barriers_max", 13)])
def test_a_lowered_minimum_is_refused(term: str, value: int) -> None:
    """`[AE-12]`: a Minimum may be raised by agreement but never lowered."""
    with pytest.raises(NegotiationError, match=f"{term} is a Minimum"):
        check_appendix_f(terms_from_config(game()) | {term: value})


@pytest.mark.parametrize(("term", "value"), [("board_size", 9), ("max_steps", 50),
                                             ("barriers_max", 20)])
def test_a_raised_minimum_is_allowed(term: str, value: int) -> None:
    check_appendix_f(terms_from_config(game()) | {term: value})


@pytest.mark.parametrize("participants",
                         [["only-one"], ["a", "a"], ["a", ""], "not-a-list", ["a", "b", "c"]])
def test_bad_participant_lists_are_refused(participants: object) -> None:
    with pytest.raises(NegotiationError, match="agreed_between"):
        build_offer(game() | {"agreed_between": participants}, IDENTITY)


def test_an_offer_from_a_group_outside_the_agreement_is_refused() -> None:
    with pytest.raises(NegotiationError, match="not in agreed_between"):
        build_offer(game(), {"group_id": "some-stranger"})
