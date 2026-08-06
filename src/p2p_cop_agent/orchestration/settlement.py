"""Audit the series, then agree the result — in that order (`M7-06`, `M7-18`).

Rule 36 (Mandatory) does not merely require an audit; it fixes its **position**: "Perform
a comprehensive mutual audit log at the end of every game. Sanction: **Mandatory condition
before agreement on the JSON result**." The audit is a precondition of agreeing, so this
module makes the ordering structural — `agree` takes a passed `SeriesAudit` and there is
no way to reach agreement without one.

**Two sanctions that punish different people, and conflating them would be expensive.**

* **Rule 19** — "Reject any game technical mismatch during the audit phase. Sanction: Iron
  rule; score of 0 for **the falsifying group**." One side, the guilty one.
* **Rule 35** — "a conflicting report causes disqualification of the game and a score of 0
  for **both teams**."

So catching an opponent's forgery is not a reason to fire off our own contradicting
report: that converts *their* rule 19 loss into a rule 35 loss we share. A failed audit
means we do not agree and do not report a disputed outcome (`M7-18c`); it does not mean we
race them to the lecturer.

**A disagreement is recorded, never smoothed over (`M7-18b`).** The temptation is to
retry, or to adopt their number to keep the peace. Both are worse than the conflict: the
first hides evidence the auditor needs and the second files a result we do not believe.
`Settlement` keeps the two outcomes side by side so the disagreement is legible afterwards.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum

from p2p_cop_agent.protocol.audit import AuditVerdict, audit_reveal


class Settled(str, Enum):
    """How a series ended. Only `AGREED` may be reported."""

    AGREED = "agreed"
    CONFLICT = "conflict"            # rule 35: 0/0 for both
    AUDIT_FAILED = "audit_failed"    # rule 19: 0 for the falsifying group
    UNANSWERED = "unanswered"        # the peer never replied


class SettlementError(RuntimeError):
    """Raised when a caller tries to agree or report out of order."""


@dataclass(frozen=True, slots=True)
class SeriesAudit:
    """The audit over every sub-game. `passed` is the only gate to agreement (`M7-06a`)."""

    passed: bool
    sub_games: tuple[int, ...]
    failed_at: int | None
    reason: str | None

    @property
    def verdict(self) -> Settled | None:
        return None if self.passed else Settled.AUDIT_FAILED


@dataclass(frozen=True, slots=True)
class Settlement:
    """The outcome of settling, with both sides' claims kept visible."""

    state: Settled
    ours: object
    theirs: object = None
    audit: SeriesAudit | None = None

    @property
    def reportable(self) -> bool:
        """`M7-18c`: only an agreed result may be reported."""
        return self.state is Settled.AGREED


def audit_series(reveals: Sequence[Mapping[str, object]]) -> SeriesAudit:
    """Audit every sub-game's reveal. `:1136`: the nonces exist only now, at the end.

    Stops at the first failure and names the sub-game. Rule 19 calls a mismatch an "iron
    rule", so there is nothing to weigh up once one is found — continuing would only
    obscure which sub-game broke.
    """
    if not reveals:
        return SeriesAudit(False, (), None, "no sub-games were audited")
    numbers: list[int] = []
    for reveal in reveals:
        number = reveal.get("sub_game")
        numbers.append(number if isinstance(number, int) else -1)
        report = audit_reveal(reveal.get("payload"), reveal.get("commits"))
        if report.verdict is not AuditVerdict.VERIFIED:
            return SeriesAudit(False, tuple(numbers), numbers[-1], report.reason)
    return SeriesAudit(True, tuple(numbers), None, None)


def agree(audit: SeriesAudit, ours: object, theirs: object) -> Settlement:
    """Compare the two computed outcomes — but only after a passed audit (`M7-18a`).

    Rule 36 makes the audit a "mandatory condition before agreement", so an unpassed audit
    is refused here rather than checked by the caller: a precondition a caller can forget
    is not a precondition.
    """
    if not audit.passed:
        return Settlement(Settled.AUDIT_FAILED, ours, theirs, audit)
    if theirs is None:
        return Settlement(Settled.UNANSWERED, ours, None, audit)
    if ours != theirs:
        return Settlement(Settled.CONFLICT, ours, theirs, audit)
    return Settlement(Settled.AGREED, ours, theirs, audit)


def require_reportable(settlement: Settlement) -> None:
    """`M7-18c`: refuse to report anything but an agreed result.

    Each state gets its own message because they call for different actions: a conflict
    needs a human and the lecturer, an audit failure needs the evidence preserved, and
    silence needs a retry of the *exchange*, not of the report.
    """
    if settlement.reportable:
        return
    reasons = {
        Settled.CONFLICT: (
            f"the two sides disagree ({settlement.ours!r} vs {settlement.theirs!r}); rule 35 "
            "scores a conflicting report 0 for BOTH teams, so this must not be sent"
        ),
        Settled.AUDIT_FAILED: (
            "the mutual audit did not pass, and rule 36 makes it a mandatory condition "
            "before agreement; reporting now would turn their rule 19 loss into a shared one"
        ),
        Settled.UNANSWERED: "the opponent never returned an outcome; there is nothing agreed to report",
    }
    raise SettlementError(reasons[settlement.state])


def settlement_record(settlement: Settlement) -> Mapping[str, object]:
    """The `mutual_agreement` block for the log artifact — both claims, kept side by side."""
    return {
        "state": settlement.state.value,
        "our_outcome": settlement.ours,
        "their_outcome": settlement.theirs,
        "audit_passed": bool(settlement.audit and settlement.audit.passed),
        "audit_failed_at": settlement.audit.failed_at if settlement.audit else None,
    }
