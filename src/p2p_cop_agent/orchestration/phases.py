"""The mandatory turn phase machine (M5-11a).

Appendix E rules 4 and 5 require the runtime to manage game state as a declared
state machine and to reject any transition that is not in the table. The point is
not bookkeeping: it turns a silent hang into a caught error, and it gives a
mid-turn disconnect one defined exit (`TECHNICAL_LOSS`) instead of a deadlock.

The table is transcribed from the specification's own listing, unchanged:

    WAITING_FOR_OPPONENT -> COMPUTING_MOVE
    COMPUTING_MOVE       -> COMMITTING | TECHNICAL_LOSS
    COMMITTING           -> AWAITING_REVEAL
    AWAITING_REVEAL      -> VERIFYING | TECHNICAL_LOSS
    VERIFYING            -> WAITING_FOR_OPPONENT
    TECHNICAL_LOSS       -> (terminal)

**What the phases mean on this wire.** The names come from the book's four-phase
commit-reveal (commit, acknowledge, reveal, audit). The simulator-v3.0.0 profile
this project speaks has **no live reveal tool**: a turn message carries the hint
and the commitment hash, while the move, the true position, the bluff verdict, and
the nonce stay private until the end-of-game audit (confirmed against the reference
2026-08-01). So `AWAITING_REVEAL` is the state of having committed and being owed
the opponent's next turn message, and `VERIFYING` is checking what arrived. The
mandated names are kept exactly as the rule writes them rather than renamed to fit
the carrier, because rule 4 is about the declared machine, not about our vocabulary.

Deliberately, `TECHNICAL_LOSS` is reachable only from the two phases the table
allows. A peer cannot declare a technical loss while it is, say, still computing a
move it has not committed -- if that ever needs to change, the table changes first.
"""

from __future__ import annotations

from enum import Enum


class Phase(Enum):
    """One declared state of a turn."""

    WAITING_FOR_OPPONENT = "WAITING_FOR_OPPONENT"
    COMPUTING_MOVE = "COMPUTING_MOVE"
    COMMITTING = "COMMITTING"
    AWAITING_REVEAL = "AWAITING_REVEAL"
    VERIFYING = "VERIFYING"
    TECHNICAL_LOSS = "TECHNICAL_LOSS"


# The specification's table, verbatim. Membership here is the whole authority.
TRANSITIONS: dict[Phase, frozenset[Phase]] = {
    Phase.WAITING_FOR_OPPONENT: frozenset({Phase.COMPUTING_MOVE}),
    Phase.COMPUTING_MOVE: frozenset({Phase.COMMITTING, Phase.TECHNICAL_LOSS}),
    Phase.COMMITTING: frozenset({Phase.AWAITING_REVEAL}),
    Phase.AWAITING_REVEAL: frozenset({Phase.VERIFYING, Phase.TECHNICAL_LOSS}),
    Phase.VERIFYING: frozenset({Phase.WAITING_FOR_OPPONENT}),
    Phase.TECHNICAL_LOSS: frozenset(),
}

# One full turn, in the order the reference performs it: wait for the opponent,
# think, commit, send, then check what comes back.
TURN_CYCLE: tuple[Phase, ...] = (
    Phase.COMPUTING_MOVE,
    Phase.COMMITTING,
    Phase.AWAITING_REVEAL,
    Phase.VERIFYING,
    Phase.WAITING_FOR_OPPONENT,
)


class PhaseError(RuntimeError):
    """Raised when a transition is not in the declared table (`[AE-5]`)."""


class PhaseMachine:
    """Track one peer's turn phase, refusing every undeclared transition.

    ``history`` keeps the phases entered in order so the log manager can record
    each transition (M5-11d) and a test can assert a whole turn, not just its end.
    """

    __slots__ = ("_history",)

    def __init__(self, start: Phase = Phase.WAITING_FOR_OPPONENT) -> None:
        if not isinstance(start, Phase):
            raise PhaseError(f"start must be a Phase, got {start!r}")
        self._history: list[Phase] = [start]

    @property
    def current(self) -> Phase:
        """Return the phase the peer is in now."""
        return self._history[-1]

    @property
    def history(self) -> tuple[Phase, ...]:
        """Return every phase entered, in order, including the starting one."""
        return tuple(self._history)

    @property
    def is_terminal(self) -> bool:
        """Return whether no transition out of the current phase exists."""
        return not TRANSITIONS[self.current]

    def to(self, phase: Phase) -> Phase:
        """Enter ``phase``, or raise naming the transition that was refused."""
        if not isinstance(phase, Phase):
            raise PhaseError(f"target must be a Phase, got {phase!r}")
        allowed = TRANSITIONS[self.current]
        if phase not in allowed:
            permitted = ", ".join(sorted(p.value for p in allowed)) or "nothing (terminal)"
            raise PhaseError(
                f"illegal transition {self.current.value} -> {phase.value}; "
                f"allowed: {permitted}"
            )
        self._history.append(phase)
        return phase

    def fail(self) -> Phase:
        """Route a mid-turn fault to the one declared terminal state (`[AE-7]`).

        Only legal where the table allows it, so a peer cannot abandon a turn it
        has not yet committed to.
        """
        return self.to(Phase.TECHNICAL_LOSS)

    def complete_turn(self) -> tuple[Phase, ...]:
        """Walk one full turn cycle, returning the phases entered."""
        return tuple(self.to(phase) for phase in TURN_CYCLE)
