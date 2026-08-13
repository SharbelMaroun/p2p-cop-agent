"""The Cop's moves must depend on the opponent (`M11-01`).

This is the test the counted `G008` series needed and did not have. The Cop played a
near-identical move sequence in all three of its Police sub-games -- same opening, same
barrier cells -- against a Thief behaving differently each time, and every unit test and
every tournament arm still passed, because the arenas built the Thief's window with our
own emitter and the decoder inverts exactly that model.

So this asserts the one property that failure violates and no existing test covered:
**two different opponents must produce two different games.** It deliberately does not
check any particular move, because the point is not what the Cop plays; it is that what
the Cop plays is a function of what it was told.
"""

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.orchestration.live_policy import live_decide

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")
GAME = {"world": {"map_area": "New York", "hint_max_words": 15},
        "movement_and_barriers": {"max_barriers": 14, "survival_threshold": 35}}
HALF = 2


def window(centre: tuple[int, int], intensity: float = 0.5) -> dict[str, float]:
    """A full board-clipped 5x5 window centred on `centre`, zero cells kept.

    The intensities are deliberately *flat*. A likelihood decoder can read nothing from
    them, which is the state the live Cop was actually in; the shape still names the
    emitter, so a Cop that reads shape stays responsive and one that reads only values
    does not.
    """
    row, col = centre
    return {f"{r},{c}": intensity
            for r in range(max(0, row - HALF), min(6, row + HALF) + 1)
            for c in range(max(0, col - HALF), min(6, col + HALF) + 1)}


def walk(cells: list[tuple[int, int]], strategy: str = "") -> list[str]:
    """Return the Cop's move labels against an opponent that visits `cells`."""
    decide = live_decide(BOARD, Coordinate(0, 0), GAME, strategy=strategy)
    moves = []
    for step, cell in enumerate(cells, start=1):
        payload, _ = decide({"step": step, "sender": "thief", "hint": "somewhere",
                             "commit": "0" * 64, "timestamp": f"t{step}",
                             "smell_grid": window(cell)})
        moves.append(payload["move"])
    return moves


SOUTH_THEN_WEST = [(3, 3), (4, 3), (5, 3), (6, 3), (6, 4), (6, 5), (6, 6), (5, 6),
                   (4, 6), (3, 6), (2, 6), (1, 6)]
EAST_THEN_NORTH = [(3, 3), (3, 4), (3, 5), (3, 6), (2, 6), (1, 6), (0, 6), (0, 5),
                   (0, 4), (0, 3), (0, 2), (0, 1)]


def first_difference(left: list[str], right: list[str]) -> int | None:
    """Return the 1-based turn where two games first diverge, or None if identical."""
    pairs = enumerate(zip(left, right, strict=True), start=1)
    return next((turn for turn, (a, b) in pairs if a != b), None)


def test_two_different_opponents_produce_two_different_games() -> None:
    """The failure this repository actually shipped: one sequence for every opponent.

    The default stack opens with seven turns of deliberate geometry -- `denial` denies
    the clearance core before it aims at anything -- so the assertion is over a realistic
    horizon rather than the opening. In `G008` the sequences stayed identical for all 34
    turns, which is what a belief that never localises looks like from outside.
    """
    assert first_difference(walk(SOUTH_THEN_WEST), walk(EAST_THEN_NORTH)) is not None


def test_the_search_engine_answers_the_opponent_too() -> None:
    """Both shipped choosers must have the property, not just the default one.

    No claim is made about *which* answers sooner. An earlier version of this test
    asserted the search diverged by turn 7 and it did -- until the weight search removed
    the distance term, after which the search contains rather than rushes and diverges on
    turn 8 like the incumbent. The property worth pinning is that the opponent changes the
    game at all; the turn it happens on is a tuning artifact and pinning it would make
    every future retune look like a regression.
    """
    assert first_difference(walk(SOUTH_THEN_WEST, "engine"),
                            walk(EAST_THEN_NORTH, "engine")) is not None


def test_the_cop_closes_on_a_stationary_opponent() -> None:
    """A Thief that never moves must be approached, not toured around."""
    moves = walk([(6, 6)] * 8)
    assert moves.count("MOVE:STAY") == 0
