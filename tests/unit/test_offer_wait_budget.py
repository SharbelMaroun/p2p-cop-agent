"""The pre-game offer wait honours the caller's connect budget (mirror of the Thief's).

At a role swap the opponent's runner may have spent its negotiate on the previous
sub-game's audit window; ``response_timeout_sec`` (30) is the in-game request timer,
not patience for an opponent who does not exist yet. Found live in the amireman
smoke, 2026-08-13 — the Thief side quit first, and this side had the same cap
waiting for sub-games 3 and 5.
"""

from p2p_cop_agent.orchestration import match as match_module

GAME = {
    "network_and_league": {"response_timeout_sec": 30, "num_games": 6,
                           "token_budget_per_series": 200000},
}


class _Sdk:
    game_config = GAME
    config_sha256 = "ab" * 32


def _negotiate_timeout(monkeypatch, **play_kwargs) -> float:
    seen = {}

    def spy(**kwargs):
        seen["timeout"] = kwargs["timeout"]
        return None  # never agreed: play_match must stop cleanly

    monkeypatch.setattr(match_module, "negotiate_match", spy)
    result = match_module.play_match(
        sdk=_Sdk(), transport=object(), take_offer=lambda: None, take_turn=lambda: None,
        decide=lambda *_a, **_k: None, identity={"group_id": "sharNamr"},
        game_id="g", game_uid="u", started_at="t", max_tokens_per_game=1,
        clock=lambda: 0.0, sleep=lambda _s: None, **play_kwargs,
    )
    assert not result.played
    return seen["timeout"]


def test_the_connect_budget_is_the_offer_floor(monkeypatch) -> None:
    assert _negotiate_timeout(monkeypatch, offer_timeout=600.0) == 600.0


def test_without_a_budget_the_shared_timer_stands(monkeypatch) -> None:
    assert _negotiate_timeout(monkeypatch) == 30.0
