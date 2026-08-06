"""M6-06: predictive barrier squeezing, and the trade it refuses to make.

`inst/police_thief_p2p_Summary.md:812` is the whole specification: "the Cop must manage
these resources strategically to **block the Thief's escape routes without inadvertently
obstructing their own path**." Two clauses, two halves of the tactic — and the second is
the one a naive implementation gets wrong, because walling a cell you are standing next
to is a cell you may have to walk around.

The reference offers nothing to copy: its brain "only occasionally walls a cell", is
"deliberately simple", and is documented as "a basic default you should improve".
"""

from __future__ import annotations

from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.squeeze import (
    choose_squeeze,
    escape_routes,
    legal_barrier_cells,
    obstructs_our_own_path,
)

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")


def _field(*cells: Coordinate, quota: int = 14) -> BarrierField:
    field = BarrierField(max_barriers=quota)
    for cell in cells:
        field = field.place(BOARD, cell)
    return field


def test_an_open_cell_has_four_escapes_and_a_corner_has_two() -> None:
    empty = frozenset()
    assert escape_routes(BOARD, Coordinate(3, 3), empty) == 4
    assert escape_routes(BOARD, Coordinate(0, 0), empty) == 2


def test_a_barrier_removes_an_escape_route() -> None:
    walled = frozenset({Coordinate(2, 3)})
    assert escape_routes(BOARD, Coordinate(3, 3), walled) == 3


def test_only_adjacent_cells_are_legal_to_wall() -> None:
    """A barrier goes on our own cell or one step away — never at range."""
    cells = legal_barrier_cells(BOARD, Coordinate(3, 3), _field())
    for cell in cells:
        assert abs(cell.row - 3) + abs(cell.col - 3) <= 1


def test_a_squeeze_is_chosen_when_our_route_has_a_redundant_path() -> None:
    """The barrier lands where it costs an escape and costs us nothing.

    A diagonal prediction is the case that works: two equal-length routes reach it, so
    walling one leaves the other and our distance is unchanged.
    """
    cop, predicted = Coordinate(3, 3), Coordinate(2, 4)
    chosen = choose_squeeze(BOARD, cop, predicted, _field())
    assert chosen is not None
    before = escape_routes(BOARD, predicted, frozenset())
    assert escape_routes(BOARD, predicted, frozenset({chosen})) < before


def test_the_squeeze_is_selective_because_the_book_makes_it_selective() -> None:
    """Straight-line predictions yield no squeeze, and that is the rule working.

    At range 1 the only cell adjacent to the prediction is our own, and walling it traps
    us as well. At range 2 in a straight line, the one squeezing cell IS our route. Both
    are refused by `:812`'s second clause -- "without inadvertently obstructing their own
    path" -- which is why the tactic fires occasionally rather than every turn. A
    squeeze that fired constantly would be ignoring the sentence that defines it.
    """
    cop = Coordinate(3, 3)
    for straight in (Coordinate(3, 4), Coordinate(3, 5), Coordinate(1, 4)):
        assert choose_squeeze(BOARD, cop, straight, _field()) is None


def test_a_squeeze_never_lengthens_our_own_route() -> None:
    """`:812`: 'without inadvertently obstructing their own path'."""
    cop, predicted = Coordinate(3, 3), Coordinate(3, 5)
    chosen = choose_squeeze(BOARD, cop, predicted, _field())
    if chosen is not None:
        assert not obstructs_our_own_path(BOARD, cop, predicted, chosen, frozenset())


def test_the_cell_that_would_block_our_own_route_is_refused() -> None:
    """A corridor where the only squeeze is also our only way through."""
    walls = (Coordinate(2, 4), Coordinate(4, 4))  # a gap at (3,4) is the sole passage
    cop, predicted = Coordinate(3, 3), Coordinate(3, 5)
    field = _field(*walls)
    assert obstructs_our_own_path(BOARD, cop, predicted, Coordinate(3, 4), field.cells)
    assert choose_squeeze(BOARD, cop, predicted, field) != Coordinate(3, 4)


def test_an_already_trapped_prediction_buys_no_barrier() -> None:
    """Spending quota on a cell with no escapes is pure waste."""
    boxed = (Coordinate(0, 1), Coordinate(1, 0))
    assert choose_squeeze(BOARD, Coordinate(1, 1), Coordinate(0, 0), _field(*boxed)) is None


def test_an_exhausted_quota_places_nothing() -> None:
    """`[AF-t15]`: the quota is a hard resource, not a soft preference."""
    spent = _field(Coordinate(0, 1), quota=1)
    assert spent.remaining == 0
    assert choose_squeeze(BOARD, Coordinate(3, 3), Coordinate(3, 4), spent) is None


def test_the_predicted_cell_itself_is_never_walled_as_a_squeeze() -> None:
    """A barrier on the Thief's cell is a capture claim, a different decision entirely."""
    cop, predicted = Coordinate(3, 3), Coordinate(3, 4)
    assert choose_squeeze(BOARD, cop, predicted, _field()) != predicted


def test_the_choice_is_deterministic() -> None:
    """Two identical states must produce the same barrier, for a replayable log."""
    args = (BOARD, Coordinate(3, 3), Coordinate(3, 4), _field())
    assert choose_squeeze(*args) == choose_squeeze(*args)


def test_the_squeeze_never_receives_the_thiefs_true_position() -> None:
    """It takes a *prediction*. Truth cannot enter, so a squeeze cannot leak it."""
    from inspect import signature

    names = set(signature(choose_squeeze).parameters)
    assert "predicted" in names
    assert not names & {"thief", "thief_cell", "truth", "actual", "position"}


def test_a_cell_already_walled_is_not_offered_twice() -> None:
    """The quota is spent once per cell; re-walling would burn it for nothing."""
    field = _field(Coordinate(2, 3))
    assert Coordinate(2, 3) not in legal_barrier_cells(BOARD, Coordinate(3, 3), field)
