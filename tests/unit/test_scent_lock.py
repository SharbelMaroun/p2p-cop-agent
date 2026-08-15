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
#
# Changed 2026-08-15 by `C-048`, from `e6aef097...`. That is the point of the lock working:
# the `update` string in the record now carries the upper clamp, so the physics really did
# change and the published hash had to move with it. A lock that survived a change to the
# formula it locks would be the more serious failure -- rule 23's sanction is for deviating
# from the AGREED formula, so the hash has to be what tells a peer the formula moved.
# Any peer we previously exchanged locks with must be re-agreed before play.
AGREED_DEFAULT_LOCK = "c77a12609b9f1c3df90067ce166b6b0455c8343dba9d463b0e8e402f8469b34f"


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
