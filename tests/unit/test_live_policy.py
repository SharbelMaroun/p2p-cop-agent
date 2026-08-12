"""The live Cop turn plays the measured pursuit stack over the wire (M6-21).

Until 2026-08-07 the served move was a documented placeholder — a legal STAY every
turn, incapable of ever capturing. Each test pins one property of the replacement.
"""

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.orchestration.live_policy import live_decide
from p2p_cop_agent.protocol.commit_reveal import TurnLedger

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")
GAME = {"world": {"map_area": "New York", "hint_max_words": 15},
        "movement_and_barriers": {"max_barriers": 14}}


def thief_message(step: int, cells: dict[str, float]) -> dict:
    return {"step": step, "sender": "thief", "hint": "somewhere", "smell_grid": cells,
            "commit": "0" * 64, "timestamp": f"t{step}"}


def fresh(start: Coordinate | None = None):
    return live_decide(BOARD, start if start is not None else Coordinate(0, 0), GAME)


def test_the_cop_closes_on_the_observed_trail() -> None:
    decide = fresh(Coordinate(0, 0))
    payload, _ = decide(thief_message(1, {"6,6": 0.9, "6,5": 0.62, "5,6": 0.62}))
    assert payload["position"] in ([0, 1], [1, 0]), "one step toward the strongest scent"


def test_an_empty_observation_keeps_the_carried_belief() -> None:
    decide = fresh(Coordinate(0, 0))
    decide(thief_message(1, {"6,6": 0.9}))
    payload, _ = decide(thief_message(2, {}))
    assert payload["position"] in ([0, 2], [1, 1], [2, 0]), "still closing on (6,6)"


def test_landing_on_the_believed_cell_sends_a_capture_claim() -> None:
    decide = fresh(Coordinate(1, 2))
    _, public = decide(thief_message(1, {"1,3": 2.0}))
    assert public.get("capture_claim") == [1, 3]


def test_a_placed_barrier_is_disclosed_and_spends_the_turn() -> None:
    """Adjacent to the believed cell, walling its last exits beats moving beside it."""
    decide = fresh(Coordinate(0, 1))
    payload, public = decide(thief_message(1, {"0,0": 3.0}))
    if public.get("barrier_placed") is not None:  # the stack may prefer the capture move
        assert payload["move"].startswith("BARRIER:")
        assert payload["position"] == [0, 1], "a barrier turn gives up movement"
    else:
        assert payload["move"] != "MOVE:STAY"


def test_public_fields_carry_no_sealed_truth_and_seal_cleanly() -> None:
    decide = fresh(Coordinate(3, 3))
    ledger = TurnLedger("police")
    for step in (1, 2, 3):
        payload, public = decide(thief_message(step, {"6,6": 0.9}))
        message = ledger.seal_turn(step, payload, public)  # validates against the schema
        assert {"position", "move", "intent"}.isdisjoint(public)
        assert message["smell_grid"], "the trail is emitted every turn, involuntarily"


def test_the_trail_window_follows_the_moving_cop() -> None:
    decide = fresh(Coordinate(0, 0))
    _, first = decide(thief_message(1, {"6,6": 0.9}))
    _, second = decide(thief_message(2, {"6,6": 0.9}))
    assert first["smell_grid"] != second["smell_grid"], "the window moves with the Cop"


def test_identical_message_sequences_reproduce_identical_turns() -> None:
    turns = []
    for _ in range(2):
        decide = fresh(Coordinate(0, 0))
        seen = [decide(thief_message(1, {"5,5": 0.9})), decide(thief_message(2, {"4,5": 0.9}))]
        turns.append([(payload["move"], payload["position"], public["smell_grid"])
                      for payload, public in seen])
    assert turns[0] == turns[1]


def test_the_barrier_quota_is_never_exceeded() -> None:
    decide = fresh(Coordinate(3, 3))
    placed = 0
    for step in range(1, 30):
        payload, public = decide(thief_message(step, {"3,4": 5.0, "3,2": 4.9}))
        if public.get("barrier_placed") is not None:
            placed += 1
    assert placed <= GAME["movement_and_barriers"]["max_barriers"]
    assert len(payload["barriers"]) == placed


def test_a_blind_cop_sweeps_instead_of_standing_on_its_start_cell() -> None:
    """M6-27, the defect that lost the amireman friendly: with no observation the
    uniform prior's row-major argmax is (0,0) — the Cop's own start — so the stack
    answered STAY every turn. It stood there 26 turns, spent no barrier, and lost."""
    decide = fresh(Coordinate(0, 0))
    positions = [decide(None)[0]["position"] for _ in range(8)]
    assert positions[-1] != [0, 0], "a blind Cop must leave its start cell"
    assert len({tuple(p) for p in positions}) > 1, "it must cover ground, not stand still"


def test_an_unparseable_grid_does_not_freeze_the_cop() -> None:
    """A grid we cannot read is no evidence, and no evidence must still sweep."""
    decide = fresh(Coordinate(0, 0))
    moves = [decide(thief_message(step, {"nope": 1.0}))[0]["move"] for step in range(1, 7)]
    assert any(move != "MOVE:STAY" for move in moves)


def test_the_amireman_profile_claims_the_post_move_cell_every_turn() -> None:
    """Their guide: an ungated claim of the Cop's own cell each turn; gated claims
    miss captures under their thief-evaluated semantics. Off by default -- an
    every-turn claim broadcasts our true position, a gift no other profile demands."""
    from p2p_cop_agent.orchestration.live_policy import live_decide

    decide = live_decide(BOARD, Coordinate(0, 0), GAME, claim_every_turn=True)
    payload, public = decide(thief_message(1, {"6,6": 0.9}))
    assert public["capture_claim"] == payload["position"]

    ungated = live_decide(BOARD, Coordinate(0, 0), GAME)
    _payload2, public2 = ungated(thief_message(1, {"6,6": 0.9}))
    assert "capture_claim" not in public2 or public2["capture_claim"] != [0, 1]
