"""The containment ratchet: measured lock-breaking, with its refusals intact (M6-23).

Design history the module docstring carries is pinned here as behaviour: the ratchet
fires only in a locked endgame pocket that still carries a cycle, only on the
just-vacated cell, only when the wall touches the pocket, and never sealing the
believed cell beyond our reach.
"""

from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.strategy.containment import REGION_TRIGGER, choose_containment, pocket

BOARD = Board(grid_size=7, axis_start_index=0, axis_origin_corner="top-left")
QUOTA = BarrierField(14)

# A ladder-shaped pocket with real cycles: one interior wall bends the Thief's
# sooner-region around itself into two long columns joined by rungs.
LADDER = BarrierField(14, (Coordinate(1, 1),))

# A room with one entrance: rows 0-2, cols 0-2, walled except through (0, 2).
ROOM = BarrierField(
    14,
    (Coordinate(1, 2), Coordinate(2, 2), Coordinate(3, 0), Coordinate(3, 1), Coordinate(3, 2)),
)


def test_pocket_counts_the_soonest_region_and_its_cycles() -> None:
    area, cycles = pocket(BOARD, Coordinate(0, 0), Coordinate(3, 3), frozenset())
    assert area == 6, "the corner triangle the Thief reaches strictly first"
    assert cycles == 1, "its inner 2x2 block is one independent cycle"


def test_a_tie_belongs_to_the_cop() -> None:
    """Cop at (0,2), Thief believed at (0,0): the midpoint (0,1) ties and is not the
    Thief's — arriving together is a capture, not an escape."""
    area, _ = pocket(BOARD, Coordinate(0, 0), Coordinate(0, 2), frozenset())
    assert area == 7, "the western column, without the tied midpoint"


def test_the_ratchet_fires_in_a_locked_cyclic_pocket() -> None:
    chosen = choose_containment(
        BOARD, Coordinate(0, 3), Coordinate(0, 0), LADDER, Coordinate(0, 2))
    assert chosen == Coordinate(0, 2)


def test_the_ratchet_waits_while_the_pocket_is_open() -> None:
    """Mid-board, the region is over the trigger: chase, do not spend."""
    chosen = choose_containment(
        BOARD, Coordinate(6, 6), Coordinate(1, 1), QUOTA, Coordinate(6, 5))
    assert chosen is None


def test_the_ratchet_needs_the_wall_to_touch_the_pocket() -> None:
    """A vacated cell off the pocket is quota wasted — measured at trigger 25, where
    fourteen trail walls left the terminal orbit intact, then refused."""
    area, cycles = pocket(BOARD, Coordinate(0, 0), Coordinate(3, 3), frozenset())
    assert (area, cycles) == (6, 1), "the lock is armed; only the touch is missing"
    chosen = choose_containment(
        BOARD, Coordinate(3, 3), Coordinate(0, 0), QUOTA, Coordinate(4, 3))
    assert chosen is None


def test_the_ratchet_refuses_to_seal_the_believed_cell() -> None:
    """Walling the room's only entrance hands the Thief a fortress to the horizon."""
    area, cycles = pocket(BOARD, Coordinate(0, 0), Coordinate(0, 3), ROOM.cells)
    assert area <= REGION_TRIGGER and cycles >= 1, "otherwise the seal check never runs"
    chosen = choose_containment(
        BOARD, Coordinate(0, 3), Coordinate(0, 0), ROOM, Coordinate(0, 2))
    assert chosen is None, "(0,2) is the only way we can ever follow the Thief in"


def test_a_forest_pocket_needs_no_wall() -> None:
    """Cycles zero: the chase already wins; a wall would only slow it down."""
    barriers = BarrierField(14, (Coordinate(1, 0), Coordinate(1, 1), Coordinate(0, 2)))
    _, cycles = pocket(BOARD, Coordinate(0, 0), Coordinate(2, 1), barriers.cells)
    assert cycles == 0
    chosen = choose_containment(
        BOARD, Coordinate(2, 1), Coordinate(0, 0), barriers, Coordinate(2, 0))
    assert chosen is None


def test_no_quota_no_ratchet() -> None:
    spent = BarrierField(0)
    chosen = choose_containment(
        BOARD, Coordinate(0, 3), Coordinate(0, 0), spent, Coordinate(0, 2))
    assert chosen is None


def test_the_trigger_is_documented_and_wide_enough_to_cover_a_re_lock() -> None:
    """The first cut used 15 and disarmed when the Thief re-locked at 16 — pinned so
    a future tightening has to face the measurement."""
    assert REGION_TRIGGER >= 16
