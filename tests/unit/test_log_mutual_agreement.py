"""`M7-24` follow-up: the `mutual_agreement` block the log was missing.

Found by asking the reference-code notebook what its log actually carries — a step-3
question that was skipped when `log_artifact` was written and asked afterwards when the
method gap was closed. `mutual_agreement` is a top-level key there, and our
`settlement_record` described itself as producing "the `mutual_agreement` block for the
log artifact" while nothing consumed it: producer built, consumer never wired.

Seven of the eight method steps ran on that batch. The eighth would have caught a dangling
producer within minutes of writing it.
"""

from __future__ import annotations

from p2p_cop_agent.reporting.log_artifact import reveal_log
from tests.unit.test_log_artifact import REVEALS, _log


def test_the_revealed_log_can_carry_the_mutual_agreement_block() -> None:
    """Found by asking the reference-code notebook what its log actually carries — a
    question skipped when this module was written. `mutual_agreement` is a top-level key
    there, and `settlement_record`'s docstring claimed to produce "the `mutual_agreement`
    block for the log artifact" while nothing consumed it: producer built, consumer never
    wired. This is that wiring."""
    from p2p_cop_agent.orchestration.settlement import Settled, Settlement, settlement_record

    agreed = settlement_record(Settlement(Settled.AGREED, "capture", "capture"))
    revealed = reveal_log(_log(), REVEALS, mutual_agreement=agreed)
    assert revealed["mutual_agreement"]["state"] == "agreed"
    assert revealed["mutual_agreement"]["our_outcome"] == "capture"


def test_the_block_is_optional_so_an_unsettled_log_still_reveals() -> None:
    """A game that ended without agreement still needs its reveal written — that log is
    the evidence of what happened, and withholding it would destroy the record."""
    assert "mutual_agreement" not in reveal_log(_log(), REVEALS)
