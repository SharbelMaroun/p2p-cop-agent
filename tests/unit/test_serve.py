"""M5-07c: the pure helpers behind the serve launcher.

``serve_match`` itself binds a real socket and needs a second machine, so it is
runbook-only and not exercised here. Its decision-free helpers -- URL parsing, the
per-game token split, the deterministic game id, and the placeholder policy -- are
pure and pinned below.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.adapters.serve import (
    derive_game_id,
    per_game_token_budget,
    serve_decide,
    split_host_port,
)


@pytest.mark.parametrize("url, expected", [
    ("http://127.0.0.1:8802/mcp", ("127.0.0.1", 8802)),
    ("https://team.ngrok.app/mcp", ("team.ngrok.app", 443)),
    ("http://host.example/mcp", ("host.example", 80)),
])
def test_split_host_port(url: str, expected: tuple[str, int]) -> None:
    assert split_host_port(url) == expected


def test_split_host_port_rejects_a_url_without_a_host() -> None:
    with pytest.raises(ValueError, match="host"):
        split_host_port("not-a-url")


def test_per_game_token_budget_divides_the_series_budget() -> None:
    game = {"network_and_league": {"num_games": 6, "token_budget_per_series": 200000}}
    assert per_game_token_budget(game) == 200000 // 6


def test_per_game_token_budget_refuses_zero_games() -> None:
    with pytest.raises(ValueError, match="num_games"):
        per_game_token_budget({"network_and_league": {"num_games": 0, "token_budget_per_series": 1}})


def test_derive_game_id_is_deterministic_from_the_config_lock() -> None:
    """Both peers derive the same id from the shared config sha, so ids agree."""
    sha = "abcdef0123456789" * 4
    assert derive_game_id(sha) == "game-abcdef012345"
    assert derive_game_id(sha) == derive_game_id(sha)


def test_serve_decide_emits_a_legal_placeholder_turn() -> None:
    """The M5 placeholder: a legal STAY with public fields, advancing each call."""
    decide = serve_decide()
    payload_1, public_1 = decide(None)
    _, public_2 = decide(None)
    assert payload_1 == {"move": "MOVE:STAY", "intent": "truth"}
    assert set(public_1) == {"hint", "smell_grid", "timestamp"}
    assert public_1["timestamp"] != public_2["timestamp"]
