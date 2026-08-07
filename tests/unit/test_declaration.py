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
        "group_name": group_id,
        "members": ["a", "b"],
        "repos": repos or {"agent": f"https://example.com/{group_id}/agent",
                           "report": f"https://example.com/{group_id}/report"},
        "mcp_servers": {"peer": f"https://{group_id}.example.com/mcp"},
        "llm_model": "template-free",
        "spec": {"os": "Windows 11", "cpu_type": "x86_64", "cpu_freq_mhz": 3600, "cpu_cores": 8, "ram_gb": 31.8, "gpu_model": "RTX 3060", "vram_gb": 6.0},
    }


def _declaration(**overrides: object) -> dict:
    kwargs: dict = {
        "game_id": "game-1", "game_uid": "uid-1",
        "our_identity": _identity("alpha"), "opponent_identity": _identity("beta"),
        "config_sha256": CONFIG_SHA, "num_sub_games": 6,
        "max_tokens_per_game": 200000, "started_at": "2026-08-03T10:00:00Z",
        # `M7-02`: both required since 2026-08-07 — rule 53's commit and rule 37's count.
        "github_commit": "a" * 40,
        "games_played_declaration": {"opponent_group_id": "beta",
                                     "games_played_including_this": 1},
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


def test_the_declaration_carries_the_mcp_addresses_hardware_and_model() -> None:
    """`:2229` wants the MCP addresses plus hardware and model, per group since `M7-22f`:
    the bonus rule 24 sanctions compares two machines, so one root spec cannot express it."""
    decl = _declaration()
    ours = decl["groups"][0]
    assert all(group["mcp_servers"] for group in decl["groups"])
    assert ours["hardware_spec"]["ram_gb"] == 31.8 and ours["llm_model"] == "template-free"
    assert "hardware" not in decl and "llm_model" not in decl


def test_a_group_without_an_mcp_address_is_refused() -> None:
    identity = {k: v for k, v in _identity("alpha").items() if k != "mcp_servers"}
    with pytest.raises(DeclarationError, match="MCP addresses"):
        _declaration(our_identity=identity)


@pytest.mark.parametrize("url", [
    "https://user:pass@alpha.example.com/mcp",
    "https://alpha.example.com/mcp?token=abc123",
    "https://alpha.example.com/mcp?api_key=placeholder",
])
def test_an_mcp_address_carrying_a_credential_is_refused(url: str) -> None:
    """The declaration is committed to a public repository and emailed as an attachment.
    Rule 39 (Prohibited): "Do not push secrets and credentials to the repository, even if
    it is private... Sanction: Severe security failure and project failure." A URL with a
    credential in it is the easiest way to do that by accident."""
    with pytest.raises(DeclarationError, match="carries a credential"):
        _declaration(our_identity=_identity("alpha") | {"mcp_servers": {"peer": url}})


def test_a_missing_model_or_hardware_is_refused_and_the_schema_is_stamped() -> None:
    """Rule 24 is Mandatory and its sanction is losing the computational bonus, so an
    absent declaration is not a soft default. The schema version rides along because
    `M7-024` needs a schema change to be visible rather than silent."""
    assert _declaration()["schema_version"] == "1.1"
    with pytest.raises(DeclarationError, match=r"llm_model"):
        _declaration(our_identity=_identity("alpha") | {"llm_model": ""})
    with pytest.raises(DeclarationError, match=r"hardware spec"):
        _declaration(our_identity=_identity("alpha") | {"spec": {}})


@pytest.mark.parametrize("url", [
    "https://alpha.example.com/mcp",
    "http://127.0.0.1:8000/mcp",
    "https://alpha.example.com:443/mcp/v1",
    "https://alpha.example.com/mcp?game=1",
])
def test_an_ordinary_mcp_address_is_not_mistaken_for_a_credential(url: str) -> None:
    """The guard's other half, and it caught a real bug: `127.0.0.1:8000` was refused
    because the port's colon looked like `user:pass`. A guard that rejects the most
    common local address would be worse than none — it would be switched off."""
    _declaration(our_identity=_identity("alpha") | {"mcp_servers": {"peer": url}})
