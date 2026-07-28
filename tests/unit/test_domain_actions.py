"""Tests for the immutable movement-action vocabulary."""

import pytest

from p2p_cop_agent.domain import Action, ActionError


def test_action_tokens_are_the_five_fixed_moves() -> None:
    assert Action.tokens() == ("N", "S", "E", "W", "STAY")


def test_action_from_token_round_trips_every_member() -> None:
    for member in Action:
        assert Action.from_token(member.value) is member


def test_action_compares_equal_to_its_wire_token() -> None:
    assert Action.NORTH == "N"
    assert Action.STAY == "STAY"


@pytest.mark.parametrize("token", ["", "n", "north", "NE", "X", "STAY "])
def test_action_from_token_rejects_unknown_text(token: str) -> None:
    with pytest.raises(ActionError, match="unknown movement token"):
        Action.from_token(token)


@pytest.mark.parametrize("token", [None, 1, ["N"], b"N"])
def test_action_from_token_rejects_non_text(token: object) -> None:
    with pytest.raises(ActionError, match="must be text"):
        Action.from_token(token)


def test_action_member_value_is_read_only() -> None:
    with pytest.raises(AttributeError):
        Action.NORTH.value = "X"  # type: ignore[misc]


def test_action_members_cannot_be_reassigned() -> None:
    with pytest.raises(AttributeError, match="reassign"):
        Action.NORTH = Action.SOUTH  # type: ignore[misc]
