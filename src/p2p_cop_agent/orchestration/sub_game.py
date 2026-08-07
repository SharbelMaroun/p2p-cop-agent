"""One whole sub-game over the wire, then the audit that settles it (M5-10d/M5-10e).

The offline harness in ``harness.py`` is a *referee*: it holds both positions and
decides capture itself. Over the wire nothing can do that, because neither peer can
see the other. So termination here is **claimed, answered, and only later proven**:

1. The Cop moves and, if it believes it has captured, names the cell in
   ``capture_claim``.
2. The Thief answers in ``claim_response`` — ``{"claim": [r, c], "caught": bool}``.
   Only the Thief knows whether it was there.
3. The Thief declares ``win_claim`` ``{"type": "survival"}`` on outlasting the
   threshold.
4. At the end every commitment is revealed and recomputed. A peer that lied about a
   claim is exposed by its own sealed position records: the book's duty of truth on a
   capture claim, enforced by arithmetic rather than by a referee `[AE-21]` `[AE-22]`.

That ordering is the whole trust model. A claim is not self-executing, and a denial
is not final either — both are just statements, and the audit is what makes lying
strictly worse than losing, since a forgery scores zero for both sides while an
honest loss still scores.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from p2p_cop_agent.domain.scoring import Outcome
from p2p_cop_agent.orchestration.phases import PhaseMachine
from p2p_cop_agent.orchestration.turn_loop import (
    Decide,
    OnTransition,
    Receive,
    TerminalClaimReceived,
    TurnLoopError,
    TurnRecord,
    run_turn,
)
from p2p_cop_agent.protocol.commit_reveal import TurnLedger
from p2p_cop_agent.shared.config import JsonObject

# Outcome -> the `result_claim` the wire profile allows in an audit payload.
RESULT_CLAIMS: dict[Outcome, str] = {
    Outcome.CAPTURE: "capture",
    Outcome.SURVIVAL: "survival",
    Outcome.TECHNICAL_LOSS: "timeout",
}


@dataclass(frozen=True, slots=True)
class SubGameOutcome:
    """How one sub-game ended, and the audit this peer sent to prove its play."""

    outcome: Outcome
    steps: int
    reason: str
    turns: tuple[TurnRecord, ...]
    audit: JsonObject | None = None


def run_sub_game_over_wire(
    *,
    machine: PhaseMachine,
    ledger: TurnLedger,
    transport: object,
    receive: Receive,
    decide: Decide,
    survival_threshold: int,
    opens: bool = False,
    on_transition: OnTransition | None = None,
    send_audit: bool = True,
) -> SubGameOutcome:
    """Play turns until the sub-game is decided, then reveal everything.

    The loop is bounded by ``survival_threshold`` and the horizon is **inclusive**:
    completing that many steps uncaptured is a Thief win, because Appendix F sets the
    step limit and the survival threshold to the same value and the book defines
    survival as lasting "the limit of valid moves" (`U-027`).
    """
    if isinstance(survival_threshold, bool) or not isinstance(survival_threshold, int):
        raise TurnLoopError(f"survival_threshold must be an integer, got {survival_threshold!r}")
    if survival_threshold < 1:
        raise TurnLoopError(f"survival_threshold must be positive, got {survival_threshold}")

    turns: list[TurnRecord] = []
    for step in range(1, survival_threshold + 1):
        try:
            record = run_turn(
                step,
                machine=machine,
                ledger=ledger,
                transport=transport,
                receive=receive,
                decide=decide,
                opens=opens and step == 1,
                on_transition=on_transition,
                terminal=_decided_by,
            )
        except TerminalClaimReceived as claim:
            # The opponent's message decided the game before our turn existed —
            # nothing further is owed, and replying to a finished game is how the
            # first rehearsal turned one survival into two disagreeing artifacts.
            settled = claim.step if isinstance(claim.step, int) else step - 1
            return _finish(claim.outcome, settled, claim.reason, turns,
                           ledger, transport, send_audit)
        except TurnLoopError as exc:
            return _finish(Outcome.TECHNICAL_LOSS, step - 1, str(exc), turns,
                           ledger, transport, send_audit)
        turns.append(record)

    return _finish(
        Outcome.SURVIVAL,
        survival_threshold,
        f"the Thief was not captured within {survival_threshold} steps",
        turns, ledger, transport, send_audit,
    )


def _decided_by(message: Mapping[str, object] | None) -> tuple[Outcome, str] | None:
    """Read a terminal claim out of the opponent's turn, if it made one.

    Only the opponent's *answer* ends the game, never our own claim: naming a cell in
    ``capture_claim`` asserts nothing until the peer that knows the truth replies.
    """
    if message is None:
        return None
    answer = message.get("claim_response")
    if isinstance(answer, Mapping) and answer.get("caught") is True:
        return Outcome.CAPTURE, f"the opponent confirmed capture at {answer.get('claim')!r}"
    win = message.get("win_claim")
    if isinstance(win, Mapping) and win.get("type") == "survival":
        return Outcome.SURVIVAL, "the opponent claimed survival"
    return None


def _finish(
    outcome: Outcome,
    steps: int,
    reason: str,
    turns: list[TurnRecord],
    ledger: TurnLedger,
    transport: object,
    send_audit: bool,
) -> SubGameOutcome:
    """Reveal every sealed record to the opponent, then report the outcome.

    The audit is sent even when this peer is taking the technical loss: an audit that
    is withheld cannot be checked, and the point of the reveal is that the *other*
    side can recompute it `[AE-19]`.
    """
    audit = None
    if send_audit:
        audit = _reveal(outcome, ledger, transport)
    return SubGameOutcome(outcome, steps, reason, tuple(turns), audit)


def _reveal(outcome: Outcome, ledger: TurnLedger, transport: object) -> JsonObject | None:
    """Build and deliver the audit payload, tolerating an opponent already gone."""
    payload = ledger.audit_payload(RESULT_CLAIMS[outcome])
    submit: Callable[[JsonObject], object] | None = getattr(transport, "submit_audit", None)
    if submit is None:
        return payload
    try:
        submit(payload)
    except Exception:  # noqa: BLE001 - a peer that has left cannot receive its proof
        return payload
    return payload
