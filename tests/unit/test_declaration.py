"""M5-17f-iii: the pre-game declaration, written after negotiation and locked before play.

M5 owns the timing-and-lock obligation, not the M7 artifact: a declaration exists,
carries the fields both peers can compute before the first move, and is
cryptographically locked. These pin the builder and that the lock is public,
reproducible, and tamper-evident.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.protocol.declaration import (
    DeclarationError,
    build_declaration,
    lock_declaration,
)

CONFIG_SHA = "a" * 64


def _identity(group_id: str, repos: dict[str, str] | None = None) -> dict:
    return {
        "group_id": group_id,
        "members": ["a", "b"],
        "repos": repos or {"agent": f"https://example.com/{group_id}/agent",
                           "report": f"https://example.com/{group_id}/report"},
    }


def _declaration(**overrides: object) -> dict:
    kwargs: dict = {
        "game_id": "game-1", "game_uid": "uid-1",
        "our_identity": _identity("alpha"), "opponent_identity": _identity("beta"),
        "config_sha256": CONFIG_SHA, "num_sub_games": 6,
        "max_tokens_per_game": 200000, "started_at": "2026-08-03T10:00:00Z",
    }
    kwargs.update(overrides)
    return build_declaration(**kwargs)


def test_the_declaration_carries_every_pre_game_member() -> None:
    decl = _declaration()
    assert decl["declaration_type"] == "pre_game"
    assert decl["game_id"] == "game-1" and decl["game_uid"] == "uid-1"
    assert decl["config_sha256"] == CONFIG_SHA
    assert [g["group_id"] for g in decl["groups"]] == ["alpha", "beta"]
    assert decl["num_sub_games"] == 6 and decl["max_tokens_per_game"] == 200000
    assert decl["game_ended_at"] is None  # filled and re-locked post-game by M7


def test_the_links_are_all_four_repos_two_per_group() -> None:
    """Rule 49: four repository links total, two per group."""
    assert len(_declaration()["links"]) == 4


def test_the_lock_is_reproducible_and_sixty_four_hex() -> None:
    decl = _declaration()
    lock = lock_declaration(decl)
    assert lock == lock_declaration(dict(decl))
    assert len(lock) == 64 and all(c in "0123456789abcdef" for c in lock)


def test_the_lock_changes_when_any_field_changes() -> None:
    """Tamper-evidence: a different declaration must not share a lock."""
    assert lock_declaration(_declaration()) != lock_declaration(_declaration(game_uid="uid-2"))


@pytest.mark.parametrize("overrides", [
    {"game_id": ""},
    {"game_uid": ""},
    {"config_sha256": "tooshort"},
    {"num_sub_games": 0},
    {"max_tokens_per_game": -1},
])
def test_an_incomplete_declaration_is_refused(overrides: dict) -> None:
    with pytest.raises(DeclarationError):
        _declaration(**overrides)


def test_a_group_without_a_repo_link_is_refused() -> None:
    with pytest.raises(DeclarationError, match="repo"):
        _declaration(opponent_identity={"group_id": "beta", "members": [], "repos": {}})


def test_a_group_without_a_group_id_is_refused() -> None:
    with pytest.raises(DeclarationError, match="group_id"):
        _declaration(opponent_identity={"members": [], "repos": {"a": "https://x/a"}})
