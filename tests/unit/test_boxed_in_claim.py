"""C-037: a Thief that concedes ``boxed_in`` must end the sub-game, not break it.

Group `uoh-ay26`'s Thief sends ``win_claim`` ``{"type": "boxed_in"}`` when every
cardinal neighbour is barriered or off-board. Our schema pinned the value to
``survival`` with ``additionalProperties: false``, so the whole turn message failed
validation and was dropped -- the Cop then waited for a turn that would never arrive
and the match died into the 0/0 that rule 35 gives both sides.

The value is a peer extension: the reference simulator emits only
``{"type": "survival"}`` or ``None``, and the book settles the same condition through
the Cop's ``capture_claim`` and the Thief's truthful ``claim_response``. So these
tests pin *tolerate, never adopt* -- and pin the sender gate, because a Cop making
this claim would be asserting our capture without proof (rule 22).
"""

import pytest

from p2p_cop_agent.domain.scoring import Outcome
from p2p_cop_agent.orchestration.terminal_claims import decided_by
from p2p_cop_agent.protocol.messages import ProtocolError, validate_message


def turn(**extra: object) -> dict:
    """A schema-complete turn message, overridable per test."""
    return {"step": 7, "sender": "thief", "hint": "cornered", "smell_grid": {},
            "commit": "a" * 64, "timestamp": "2026-08-12T00:00:00+00:00",
            "barrier_placed": None, "capture_claim": None, "claim_response": None,
            **extra}


# --- the schema gate: the message must survive validation at all -------------------


@pytest.mark.parametrize("claim_type", ["survival", "boxed_in"])
def test_schema_accepts_both_terminal_claims(claim_type: str) -> None:
    """Neither value may cost us the turn message that carries it."""
    validate_message("turn", turn(win_claim={"type": claim_type}))


def test_schema_still_refuses_an_unknown_claim_type() -> None:
    """Widening to two values is not the same as accepting anything."""
    with pytest.raises(ProtocolError):
        validate_message("turn", turn(win_claim={"type": "vibes"}))


def test_schema_still_refuses_extra_members_in_the_claim() -> None:
    """``additionalProperties: false`` inside the claim is deliberate and stays."""
    with pytest.raises(ProtocolError):
        validate_message("turn", turn(win_claim={"type": "boxed_in", "cell": [0, 0]}))


# --- the decision: who is believed, and about what --------------------------------


def test_a_thief_conceding_boxed_in_ends_the_sub_game_as_a_capture() -> None:
    """Only the Thief can see its own neighbours, so its concession is decisive."""
    decided = decided_by(turn(sender="thief", win_claim={"type": "boxed_in"}))
    assert decided is not None
    outcome, reason = decided
    assert outcome is Outcome.CAPTURE
    assert "boxed in" in reason


def test_a_cop_claiming_boxed_in_is_ignored() -> None:
    """Rule 22: a peer asserting our capture without proof is not believed.

    This is the direction that matters for safety. Accepting it would let any
    opponent end a game it was losing by asserting a fact it cannot observe.
    """
    assert decided_by(turn(sender="police", win_claim={"type": "boxed_in"})) is None


def test_survival_is_unaffected_by_the_widening() -> None:
    """The value we actually emit keeps its existing meaning."""
    decided = decided_by(turn(sender="thief", win_claim={"type": "survival"}))
    assert decided is not None
    assert decided[0] is Outcome.SURVIVAL


def test_a_confirmed_capture_still_outranks_a_win_claim() -> None:
    """An answered ``capture_claim`` is proof; a ``win_claim`` is only a statement."""
    decided = decided_by(turn(
        sender="thief",
        claim_response={"claim": [2, 2], "caught": True},
        win_claim={"type": "survival"},
    ))
    assert decided is not None
    assert decided[0] is Outcome.CAPTURE


def test_a_turn_with_no_claim_decides_nothing() -> None:
    """The ordinary case: the game continues."""
    assert decided_by(turn()) is None


def test_a_malformed_win_claim_decides_nothing() -> None:
    """A non-mapping claim must not raise on the live path."""
    assert decided_by(turn(win_claim="boxed_in")) is None
