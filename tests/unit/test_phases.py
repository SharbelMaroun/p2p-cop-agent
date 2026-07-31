"""M5-11a: the declared turn phase machine, and every transition it refuses.

Appendix E rules 4 and 5 make the table itself the authority, so the tests are
mostly about what is *not* allowed -- a machine that accepts everything would pass
a happy-path test and still deadlock the first time a peer went out of order.
"""

import pytest

from p2p_cop_agent.orchestration.phases import (
    TRANSITIONS,
    TURN_CYCLE,
    Phase,
    PhaseError,
    PhaseMachine,
)

# Every ordered pair the specification's table permits.
LEGAL = {(source, target) for source, targets in TRANSITIONS.items() for target in targets}
ALL_PAIRS = {(source, target) for source in Phase for target in Phase}


def test_the_table_matches_the_specification_listing() -> None:
    """Transcribed from the spec; a silent edit here changes a mandatory rule."""
    assert {
        Phase.WAITING_FOR_OPPONENT: frozenset({Phase.COMPUTING_MOVE}),
        Phase.COMPUTING_MOVE: frozenset({Phase.COMMITTING, Phase.TECHNICAL_LOSS}),
        Phase.COMMITTING: frozenset({Phase.AWAITING_REVEAL}),
        Phase.AWAITING_REVEAL: frozenset({Phase.VERIFYING, Phase.TECHNICAL_LOSS}),
        Phase.VERIFYING: frozenset({Phase.WAITING_FOR_OPPONENT}),
        Phase.TECHNICAL_LOSS: frozenset(),
    } == TRANSITIONS


def test_every_phase_has_a_declared_row() -> None:
    """A phase missing from the table would raise KeyError instead of PhaseError."""
    assert set(TRANSITIONS) == set(Phase)


def test_a_peer_starts_waiting_for_the_opponent() -> None:
    """The reference waits first: a turn begins when the opponent's message lands."""
    assert PhaseMachine().current is Phase.WAITING_FOR_OPPONENT


@pytest.mark.parametrize(("source", "target"), sorted(LEGAL, key=lambda p: (p[0].value, p[1].value)))
def test_every_declared_transition_is_accepted(source: Phase, target: Phase) -> None:
    assert PhaseMachine(source).to(target) is target


@pytest.mark.parametrize(
    ("source", "target"), sorted(ALL_PAIRS - LEGAL, key=lambda p: (p[0].value, p[1].value))
)
def test_every_undeclared_transition_is_refused(source: Phase, target: Phase) -> None:
    """`[AE-5]`: the refusal is the feature, and it names what it refused."""
    with pytest.raises(PhaseError, match="illegal transition"):
        PhaseMachine(source).to(target)


def test_one_full_turn_walks_the_cycle_and_returns_to_waiting() -> None:
    machine = PhaseMachine()
    assert machine.complete_turn() == TURN_CYCLE
    assert machine.current is Phase.WAITING_FOR_OPPONENT


def test_turns_can_run_back_to_back() -> None:
    """Thirty-five of these happen per sub-game; the cycle must be re-enterable."""
    machine = PhaseMachine()
    for _ in range(3):
        machine.complete_turn()
    assert machine.current is Phase.WAITING_FOR_OPPONENT
    assert machine.history.count(Phase.COMMITTING) == 3


def test_history_records_every_phase_in_order() -> None:
    """The log manager needs one line per transition (M5-11d)."""
    machine = PhaseMachine()
    machine.complete_turn()
    assert machine.history == (Phase.WAITING_FOR_OPPONENT, *TURN_CYCLE)


def test_technical_loss_is_terminal() -> None:
    machine = PhaseMachine(Phase.AWAITING_REVEAL)
    assert machine.fail() is Phase.TECHNICAL_LOSS
    assert machine.is_terminal
    with pytest.raises(PhaseError, match="terminal"):
        machine.to(Phase.WAITING_FOR_OPPONENT)


@pytest.mark.parametrize("source", [Phase.COMPUTING_MOVE, Phase.AWAITING_REVEAL])
def test_a_mid_turn_fault_has_a_defined_exit(source: Phase) -> None:
    """`[AE-7]`: a disconnect must reach a terminal state, never deadlock."""
    assert PhaseMachine(source).fail() is Phase.TECHNICAL_LOSS


@pytest.mark.parametrize(
    "source", [Phase.WAITING_FOR_OPPONENT, Phase.COMMITTING, Phase.VERIFYING]
)
def test_a_technical_loss_cannot_be_declared_from_an_undeclared_phase(source: Phase) -> None:
    """Abandoning an uncommitted turn is not in the table, so it is refused.

    Not an oversight: if this ever needs to be legal, the table changes first.
    """
    with pytest.raises(PhaseError, match="illegal transition"):
        PhaseMachine(source).fail()


@pytest.mark.parametrize("bad", ["COMMITTING", None, 3])
def test_a_non_phase_target_is_refused(bad: object) -> None:
    with pytest.raises(PhaseError, match="must be a Phase"):
        PhaseMachine().to(bad)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", ["WAITING_FOR_OPPONENT", None])
def test_a_non_phase_start_is_refused(bad: object) -> None:
    with pytest.raises(PhaseError, match="start must be a Phase"):
        PhaseMachine(bad)  # type: ignore[arg-type]
