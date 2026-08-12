"""A strategy exception costs one imperfect turn, never the match (M6-26).

An uncaught raise inside the live `decide` propagates to the watchdog as a freeze and
scores the technical 0/0 — strictly worse than any legal move (Appendix F table 17:
even a lost game pays 5). The fail-safe converts a strategy bug into a truthful STAY:
the sealed record still matches the cell we actually hold, the trail still advances,
and the wire message still carries every mandatory field, so the game and its audit
continue as if the Cop had merely played a weak turn.
"""

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.orchestration import live_policy

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")
GAME = {"world": {"map_area": "New York", "hint_max_words": 15},
        "movement_and_barriers": {"max_barriers": 14}}


def thief_message(step: int, cells: dict[str, float]) -> dict:
    return {"step": step, "sender": "thief", "hint": "somewhere", "smell_grid": cells,
            "commit": "0" * 64, "timestamp": f"t{step}"}


def test_a_raising_strategy_yields_a_truthful_stay(monkeypatch) -> None:
    def poisoned(*_args, **_kwargs):
        raise RuntimeError("injected strategy failure")

    monkeypatch.setattr(live_policy, "denial_turn_intent", poisoned)
    decide = live_policy.live_decide(BOARD, Coordinate(2, 2), GAME)
    payload, public = decide(thief_message(1, {"6,6": 0.9}))
    assert payload["move"] == "MOVE:STAY"
    assert payload["position"] == [2, 2], "the sealed record matches the held cell"
    assert payload["barriers"] == [], "a failed turn spends no quota"
    assert public["smell_grid"], "the involuntary emission still reaches the wire"


def test_the_game_continues_after_the_failed_turn(monkeypatch) -> None:
    """One poisoned turn, then the stack recovers: the next turn plays normally."""
    real = live_policy.denial_turn_intent
    calls = {"count": 0}

    def flaky(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise ValueError("first turn only")
        return real(*args, **kwargs)

    monkeypatch.setattr(live_policy, "denial_turn_intent", flaky)
    decide = live_policy.live_decide(BOARD, Coordinate(0, 0), GAME)
    first, _ = decide(thief_message(1, {"6,6": 0.9}))
    second, _ = decide(thief_message(2, {"6,6": 0.9, "6,5": 0.62}))
    assert first["move"] == "MOVE:STAY"
    assert second["move"] != "MOVE:STAY", "recovery, not a permanent forfeit"
