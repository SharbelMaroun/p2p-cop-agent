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
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate


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


def test_serve_decide_is_the_live_policy_not_the_placeholder() -> None:
    """The M5 STAY placeholder is gone: the served turn moves, seals truth, emits.

    This test used to pin ``payload == {"move": "MOVE:STAY", ...}`` — pinning the
    defect. A Cop that never leaves its start cell can never capture (M6-21).
    """
    decide = serve_decide(
        Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left"),
        Coordinate(0, 0),
        {"world": {"map_area": "New York", "hint_max_words": 15},
         "movement_and_barriers": {"max_barriers": 14}},
    )
    payload_1, public_1 = decide(
        {"step": 1, "sender": "thief", "hint": "far away",
         "smell_grid": {"6,6": 0.9, "5,6": 0.62}, "commit": "0" * 64, "timestamp": "t1"})
    _, public_2 = decide(None)
    assert payload_1["move"] != "MOVE:STAY", "the placeholder would forfeit every game"
    assert payload_1["position"] != [0, 0], "the served Cop actually pursues"
    assert public_1["smell_grid"], "the locked emission model must be honoured"
    assert public_1["timestamp"] != public_2["timestamp"]
