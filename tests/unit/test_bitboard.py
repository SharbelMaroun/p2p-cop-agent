"""The bitboard primitives the search evaluates with.

The two random sweeps proving what `evaluate` may assume about these primitives live in
`test_engine_eval_shortcuts.py`; those are claims about the evaluator, not about these.
"""

from __future__ import annotations

from p2p_cop_agent.strategy.bitboard import (
    bit,
    cell_of,
    components,
    cycle_rank,
    distance_between,
    edge_count,
    flood,
    masks,
    neighbours,
    popcount,
)

SIZE = 7
FULL, _, _ = masks(SIZE)


def mask_of(*cells: tuple[int, int]) -> int:
    total = 0
    for cell in cells:
        total |= bit(cell, SIZE)
    return total


def test_cell_and_bit_round_trip() -> None:
    for row in range(SIZE):
        for col in range(SIZE):
            index = bit((row, col), SIZE).bit_length() - 1
            assert cell_of(index, SIZE) == (row, col)


def test_neighbours_do_not_wrap_across_a_row_edge() -> None:
    """West from column 0 must leave the board, not reappear on the row above."""
    assert neighbours((3, 0), SIZE) == mask_of((2, 0), (4, 0), (3, 1))
    assert neighbours((3, 6), SIZE) == mask_of((2, 6), (4, 6), (3, 5))
    assert neighbours((0, 0), SIZE) == mask_of((1, 0), (0, 1))


def test_flood_fills_only_the_reachable_side_of_a_wall() -> None:
    """A full column of barriers splits the board; the flood must respect it."""
    wall = mask_of(*[(row, 3) for row in range(SIZE)])
    free = FULL & ~wall
    west = flood(bit((0, 0), SIZE), free, SIZE)
    assert popcount(west) == SIZE * 3
    assert west & bit((0, 4), SIZE) == 0


def test_components_counts_the_pieces_a_wall_leaves() -> None:
    wall = mask_of(*[(row, 3) for row in range(SIZE)])
    assert components(FULL & ~wall, SIZE) == 2
    assert components(FULL, SIZE) == 1


def test_cycle_rank_is_zero_for_a_path_and_positive_for_a_grid() -> None:
    """The quantity the barrier budget is spent on: a forest is the catchable shape."""
    corridor = mask_of(*[(0, col) for col in range(SIZE)])
    assert cycle_rank(corridor, SIZE) == 0
    square = mask_of((0, 0), (0, 1), (1, 0), (1, 1))
    assert cycle_rank(square, SIZE) == 1
    assert cycle_rank(FULL, SIZE) == edge_count(FULL, SIZE) - SIZE * SIZE + 1


def test_cycle_rank_of_the_empty_region_is_zero() -> None:
    assert cycle_rank(0, SIZE) == 0
    assert cycle_rank(0, SIZE, parts=1) == 0, "the empty region answers before reading parts"


def test_cycle_rank_takes_a_component_count_the_caller_already_has() -> None:
    """`parts` must be the count `components` would have returned, and must be used.

    The search passes `parts=1` to skip a fill it does not need. That is only sound if the
    supplied count reaches the arithmetic unchanged, so this checks both directions: the
    right count agrees with counting, and a wrong count visibly disagrees. A `parts` that
    were quietly ignored would pass the first assertion and fail the second.
    """
    square = mask_of((0, 0), (0, 1), (1, 0), (1, 1))
    assert cycle_rank(square, SIZE, parts=1) == cycle_rank(square, SIZE) == 1

    wall = mask_of(*[(row, 3) for row in range(SIZE)])
    split = FULL & ~wall
    assert components(split, SIZE) == 2
    assert cycle_rank(split, SIZE, parts=2) == cycle_rank(split, SIZE)
    assert cycle_rank(split, SIZE, parts=1) == cycle_rank(split, SIZE) - 1


def test_distance_between_counts_steps_around_a_wall() -> None:
    assert distance_between(bit((0, 0), SIZE), bit((0, 3), SIZE), FULL, SIZE) == 3
    assert distance_between(bit((0, 0), SIZE), bit((0, 0), SIZE), FULL, SIZE) == 0
    wall = mask_of((0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1))
    free = FULL & ~wall
    assert distance_between(bit((0, 0), SIZE), bit((0, 2), SIZE), free, SIZE) == 14


def test_distance_between_reports_an_unreachable_cell() -> None:
    wall = mask_of(*[(row, 3) for row in range(SIZE)])
    free = FULL & ~wall
    assert distance_between(bit((0, 0), SIZE), bit((0, 4), SIZE), free, SIZE) == -1
