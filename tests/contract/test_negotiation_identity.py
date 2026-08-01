"""M5-04h: the mandated pre-game identity and `config_sha256` lock, our side only.

Split from `test_negotiation` to keep each contract file within the length limit.
Under the 2026-08-01 'populate ours, tolerate theirs' decision (`U-029`, `C-031`),
`build_offer` enforces the book's mandated content on **our** outbound offer and
attaches the lock, while `verify_offer` still accepts an opponent that omits them.
"""

import pytest

from p2p_cop_agent.protocol.identity import IdentityError
from p2p_cop_agent.protocol.negotiation import (
    NegotiationError,
    build_offer,
    terms_from_config,
)
from p2p_cop_agent.protocol.offer_review import verify_offer
from p2p_cop_agent.shared.contracts import shared_config_sha256
from tests.contract.test_negotiation import IDENTITY, game


def test_our_offer_carries_the_config_sha256_lock_over_the_whole_object() -> None:
    """The book requires both teams to lock the agreed values with a `config_sha256`.
    Ours is the digest of the *complete* object, matching the projection fixture's
    rule that the hash never covers only the terms."""
    offer = build_offer(game(), IDENTITY)
    assert offer["config_sha256"] == shared_config_sha256(game())


def test_our_own_offer_is_refused_when_our_identity_is_incomplete() -> None:
    """We must not ship a non-compliant offer: a missing mandated member is named.
    `neutral-group-alpha` is in `agreed_between`, so the participant check passes
    and the identity check is what fires."""
    with pytest.raises(IdentityError, match="mcp_servers|members|repos|llm_model|spec"):
        build_offer(game(), {"group_id": "neutral-group-alpha"})


def test_verify_tolerates_a_peer_that_omits_the_mandated_identity() -> None:
    """'Tolerate theirs': the signature covers the terms, not the identity, so an
    opponent that sends only a group_id still verifies. Refusing it is the deferred
    coordinator decision (`U-029`), not this peer's call."""
    offer = build_offer(game(), IDENTITY)
    offer["identity"] = {"group_id": "neutral-group-beta"}  # a peer that shared little
    assert verify_offer(offer, terms_from_config(game())) == terms_from_config(game())


def test_verify_accepts_a_matching_config_lock() -> None:
    """U-029, verify presence: a lock that matches ours is the healthy case."""
    offer = build_offer(game(), IDENTITY)
    verified = verify_offer(
        offer, terms_from_config(game()), expected_config_sha256=shared_config_sha256(game())
    )
    assert verified == terms_from_config(game())


def test_verify_refuses_a_present_but_wrong_config_lock() -> None:
    """U-029: a peer that locks a *different* config is a rule-11 mismatch -- refuse."""
    offer = build_offer(game(), IDENTITY)
    offer["config_sha256"] = "0" * 64  # a lock over some other config
    with pytest.raises(NegotiationError, match="config_sha256 lock mismatch"):
        verify_offer(
            offer, terms_from_config(game()), expected_config_sha256=shared_config_sha256(game())
        )


def test_verify_tolerates_an_omitted_lock_even_when_we_expect_one() -> None:
    """U-029, tolerate absence: a peer that keeps the lock in its artifacts, not on
    the wire, still negotiates -- omission is not a mismatch."""
    offer = build_offer(game(), IDENTITY)
    del offer["config_sha256"]
    assert verify_offer(
        offer, terms_from_config(game()), expected_config_sha256=shared_config_sha256(game())
    ) == terms_from_config(game())
