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
    terms_from_config,
)
from p2p_cop_agent.protocol.offer_review import verify_offer
from p2p_cop_agent.shared.contracts import shared_config_sha256

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "shared_contract"
EXAMPLE = BUNDLE / "fixtures" / "match_config.example.json"
PROJECTION = BUNDLE / "fixtures" / "negotiation_terms.projection.json"

# A complete identity: the book mandates members, repo URLs, MCP URLs, hardware
# spec, and LLM model, and `build_offer` now enforces that on our own outbound offer
# (M5-04h). Values are neutral test data, not the real team's.
IDENTITY = {
    "group_id": "neutral-group-alpha", "group_name": "Alpha", "members": ["a", "b"],
    "repos": {"cop": "https://example.test/cop", "thief": "https://example.test/thief"},
    "mcp_servers": {"cop": "https://cop.example.test/mcp"}, "llm_model": "cli-default",
    "spec": {"os": "Example OS", "cpu_type": "Example CPU", "cpu_freq_mhz": 3600, "cpu_cores": 8, "ram_gb": 32, "gpu_model": "none", "vram_gb": 0},
}


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


def test_the_scent_block_matches_the_lecturers_agreed_config_template() -> None:
    """`U-028`, settled 2026-08-01 against the book PDF and the artifact template.

    Table 16 has three rows, all `Fixed`, and **no** minimum-centre row; the
    lecturer's own `agreed-config` template carries the same three keys. The
    optional treatment of `min_center_intensity` is therefore right, and the
    fixture must not acquire a fourth key to please the simulator.
    """
    assert game()["pheromones"] == {
        "pheromone_center_intensity": 0.9,
        "pheromone_decay": 0.1,
        "pheromone_grid_size": 5,
    }
    assert "min_center_intensity" not in terms_from_config(game())


def test_game_id_is_not_a_signed_term() -> None:
    """Verified 2026-07-31: the identifiers are derived, never negotiated.

    Signing them would make the terms differ from a classmate's and refuse every
    match, so this guards against a plausible-looking future 'fix'.
    """
    terms = terms_from_config(game())
    assert "game_id" not in terms and "game_uid" not in terms


def test_offer_carries_terms_challenge_signature_identity_and_lock() -> None:
    offer = build_offer(game(), IDENTITY)
    assert set(offer) == {"terms", "nonce", "signature", "identity", "config_sha256"}
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

    other = {**IDENTITY, "group_id": "neutral-group-beta"}
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



@pytest.mark.parametrize("participants",
                         [["only-one"], ["a", "a"], ["a", ""], "not-a-list", ["a", "b", "c"]])
def test_bad_participant_lists_are_refused(participants: object) -> None:
    with pytest.raises(NegotiationError, match="agreed_between"):
        build_offer(game() | {"agreed_between": participants}, IDENTITY)


def test_an_offer_from_a_group_outside_the_agreement_is_refused() -> None:
    with pytest.raises(NegotiationError, match="not in agreed_between"):
        build_offer(game(), {"group_id": "some-stranger"})
