"""M6-07 / `AE-23`: the scent model is locked, and a deviation refuses the match.

Rule 23 verbatim: "Lock the cryptographic hash of the scent model before the start of
the game. Sanction: Deviation from the formula cancels the game." The book's method
(PDF p. 31) is to agree the emission and decay model, confirm both sides read it the
same way, and hash the agreement.

The digest pinned here is a **cross-implementation** constant: the companion Thief
peer, written independently, produces the same value from its own record. Pinning it
means an edit to the record shape fails here rather than silently in a match, where
the two peers would refuse each other and neither would know why.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.strategy.scent import DEFAULT_OUTER_RING_DELTA, ScentModelError
from p2p_cop_agent.strategy.scent_lock import (
    ScentLockError,
    assert_scent_locked,
    scent_model_hash,
    scent_model_record,
    verify_peer_scent_lock,
)

# The lock over the default model, reproduced independently by the Thief peer.
AGREED_DEFAULT_LOCK = "e6aef0978ff91fe8aaf7d0a49d8bb839f03cd259a554e4251c182a20b02c6ea1"


def test_the_record_describes_the_whole_model_not_just_the_constants() -> None:
    """The three Appendix F values alone cannot distinguish two emission profiles."""
    record = scent_model_record()
    assert record["center_intensity"] == 0.9
    assert record["decay_per_step"] == 0.10
    assert record["field_size"] == 5
    assert "max(0" in record["update"]  # the formula itself is inside the lock
    assert set(record["emission_profile_by_squared_distance"]) == {"0", "1", "2", "4", "5", "8"}


def test_the_lock_is_deterministic_and_matches_the_independent_peer() -> None:
    assert scent_model_hash() == scent_model_hash()
    assert scent_model_hash() == AGREED_DEFAULT_LOCK


def test_a_different_agreed_ring_produces_a_different_lock() -> None:
    """The negotiated cell is inside the hash, so disagreeing on it is visible."""
    assert scent_model_hash(0.07) != scent_model_hash(DEFAULT_OUTER_RING_DELTA)


def test_a_peer_that_publishes_no_lock_is_still_playable() -> None:
    """The reference publishes none; requiring one would refuse every such classmate."""
    verify_peer_scent_lock(None)


def test_a_peer_whose_lock_differs_is_refused_before_the_first_move() -> None:
    with pytest.raises(ScentLockError, match="rule 23"):
        verify_peer_scent_lock("f" * 64)


def test_a_peer_running_our_model_is_accepted() -> None:
    verify_peer_scent_lock(AGREED_DEFAULT_LOCK)


def test_a_peer_agreeing_a_non_default_ring_is_accepted_at_that_ring() -> None:
    verify_peer_scent_lock(scent_model_hash(0.07), outer_ring=0.07)
    with pytest.raises(ScentLockError):
        verify_peer_scent_lock(scent_model_hash(0.07), outer_ring=DEFAULT_OUTER_RING_DELTA)


def test_the_running_model_is_checked_against_what_was_locked() -> None:
    assert_scent_locked(AGREED_DEFAULT_LOCK, outer_ring=DEFAULT_OUTER_RING_DELTA)
    with pytest.raises(ScentLockError, match="does not match"):
        assert_scent_locked(AGREED_DEFAULT_LOCK, outer_ring=0.07)


def test_an_out_of_range_ring_cannot_be_locked_at_all() -> None:
    """A nonsense value fails when the record is built, never reaching the wire."""
    with pytest.raises(ScentModelError):
        scent_model_hash(1.5)
