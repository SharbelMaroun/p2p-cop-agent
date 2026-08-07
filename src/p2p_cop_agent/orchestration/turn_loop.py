"""One turn, driven by the declared phase machine (M5-11).

The reference's iteration order, confirmed 2026-08-01: **await the opponent, think,
apply locally, seal, send**. A peer must receive before it advances its own step,
so the loop is a strict alternation rather than two peers free-running.

Transport-neutral by construction: the loop is handed a ``PeerTransport`` and a
``receive`` callable and never imports FastMCP, so a whole sub-game can be tested
without a socket and the same code runs over one.

**Atomicity (M5-11b).** A turn is sealed exactly once. If the send then fails, the
turn is *not* re-sealed -- a commitment is a promise, and re-sealing would produce
a second hash for the same step and hand the opponent an audit mismatch, which is
an automatic zero `[AE-19]`. So the sealed record is retried as-is, and if it still
cannot be delivered the peer routes to the one declared terminal state rather than
inventing a new commitment.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from p2p_cop_agent.adapters.fastmcp_client import PeerRejectionError, TransportError
from p2p_cop_agent.orchestration.phases import Phase, PhaseMachine
from p2p_cop_agent.protocol.commit_reveal import CommitRevealError, TurnLedger
from p2p_cop_agent.shared.config import JsonObject

# Decide this peer's turn: given the opponent's last message (None on the opening
# turn), return the private payload to seal and the public fields to publish.
Decide = Callable[[JsonObject | None], tuple[JsonObject, JsonObject]]
# Take the opponent's next turn message, or None if none arrived in time.
Receive = Callable[[], JsonObject | None]
# Called with every phase entered, so the log manager sees each transition (M5-11d).
OnTransition = Callable[[Phase], None]


class TurnLoopError(RuntimeError):
    """Raised when a turn cannot be completed and no phase transition covers it."""


class TerminalClaimReceived(Exception):  # noqa: N818 - a control signal, not an error
    """The opponent's incoming message decided the game before our turn existed.

    Found by the first two-process rehearsal (2026-08-08): the Thief completes the
    inclusive horizon, says so in ``win_claim``, and legitimately hangs up — while
    this loop still owed a reply it could no longer deliver, recording a technical
    loss at step 34 against the opponent's survival at 35. Two artifacts disagreeing
    reconcile to 0/0 for both (`M9-021a`), so a terminal claim must end the game
    *before* this peer decides, seals, or sends anything further. Nothing is owed on
    a decided game: no seal happens, so no commitment is abandoned.
    """

    def __init__(self, outcome: object, reason: str, step: object = None) -> None:
        super().__init__(reason)
        self.outcome = outcome
        self.reason = reason
        self.step = step


@dataclass(frozen=True, slots=True)
class TurnRecord:
    """What one completed turn did, in enough detail to reconstruct it."""

    step: int
    received: JsonObject | None
    sent: JsonObject
    phases: tuple[Phase, ...]


def run_turn(
    step: int,
    *,
    machine: PhaseMachine,
    ledger: TurnLedger,
    transport: object,
    receive: Receive,
    decide: Decide,
    opens: bool = False,
    on_transition: OnTransition | None = None,
    terminal: Callable[[JsonObject], tuple[object, str] | None] | None = None,
) -> TurnRecord:
    """Run one turn through the phase machine and return what it did.

    ``opens`` is true only for the peer that moves first on the first step; the
    book gives that to the Thief, so a Cop always waits. Every other turn begins by
    awaiting the opponent, which is what makes the alternation strict.
    """
    entered: list[Phase] = []

    def enter(phase: Phase) -> None:
        machine.to(phase)
        entered.append(phase)
        if on_transition is not None:
            on_transition(phase)

    incoming = None if opens else _await_opponent(machine, receive, enter)
    if terminal is not None and incoming is not None:
        verdict = terminal(incoming)
        if verdict is not None:
            outcome, reason = verdict
            raise TerminalClaimReceived(outcome, reason, incoming.get("step"))

    # Deciding and sealing both happen in COMPUTING_MOVE, because that is the only
    # phase from which the table permits TECHNICAL_LOSS. Entering COMMITTING means
    # the commitment already exists and must now go out: the table gives it exactly
    # one exit, so a peer cannot abandon a promise it has already made. Corrected
    # 2026-08-01 — sealing used to happen inside COMMITTING, where a seal failure had
    # no legal exit and left the machine stranded mid-turn.
    enter(Phase.COMPUTING_MOVE)
    payload, public = decide(incoming)
    try:
        message = ledger.seal_turn(step, payload, public)
    except CommitRevealError as exc:
        machine.fail()
        raise TurnLoopError(f"step {step} could not be sealed: {exc}") from exc

    enter(Phase.COMMITTING)
    enter(Phase.AWAITING_REVEAL)
    _deliver(step, message, transport, ledger, machine)

    enter(Phase.VERIFYING)
    enter(Phase.WAITING_FOR_OPPONENT)
    return TurnRecord(step, incoming, message, tuple(entered))


def _await_opponent(
    machine: PhaseMachine, receive: Receive, enter: OnTransition
) -> JsonObject:
    """Return the opponent's turn, or take the declared exit if it never comes.

    Silence is not patience: a peer that owes us a turn and sends nothing ends the
    game rather than blocking it `[AE-7]`.

    The two-step exit is forced by the table, not chosen. There is no
    ``WAITING_FOR_OPPONENT -> TECHNICAL_LOSS`` edge, so a starved peer must enter
    ``COMPUTING_MOVE`` before it can declare the loss. Read strictly that is what
    the specification says; it may equally be a gap in the published table. The
    table is followed as written and the observation is recorded rather than
    patched around, because inventing an edge would weaken the one guarantee rule 5
    is for.
    """
    incoming = receive()
    if incoming is None:
        enter(Phase.COMPUTING_MOVE)
        machine.fail()
        raise TurnLoopError("opponent did not send a turn before the deadline")
    return incoming


def _deliver(
    step: int,
    message: JsonObject,
    transport: object,
    ledger: TurnLedger,
    machine: PhaseMachine,
) -> None:
    """Send the sealed turn, never re-sealing it, and route a failure cleanly.

    ``PeerRejectionError`` is a decided game outcome and ``TransportError`` is a
    carrier fault; both end this turn, but keeping them apart is what stops a lost
    game being retried as a network blip (M5-14a).
    """
    send = getattr(transport, "receive_turn", None)
    if send is None:
        raise TurnLoopError("transport does not expose receive_turn")
    try:
        ledger.acknowledge(send(message))
    except (TransportError, PeerRejectionError, CommitRevealError) as exc:
        machine.fail()
        raise TurnLoopError(f"step {step} was sealed but not delivered: {exc}") from exc


def sealed_steps(ledger: TurnLedger) -> tuple[int, ...]:
    """Return the steps this peer has committed to, in order."""
    return tuple(record.step for record in ledger.records)


def is_sealed_once(ledger: TurnLedger, step: int) -> bool:
    """Return whether exactly one commitment exists for ``step`` (M5-11b)."""
    return sealed_steps(ledger).count(step) == 1


def public_fields(message: Mapping[str, object]) -> JsonObject:
    """Return the turn message without the members the ledger supplies."""
    return {k: v for k, v in message.items() if k not in ("step", "sender", "commit")}
