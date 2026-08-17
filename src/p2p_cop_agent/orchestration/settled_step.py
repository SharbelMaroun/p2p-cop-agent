"""Which turn number a sub-game ended on, in the numbering of the side that caused it.

Split from `sub_game.py` under the file-length gate, and the seam is a real one: running a
sub-game and *accounting for how it ended* are different jobs, and the second is the one two
teams have to agree on.

Agreed with `yanell11` on 2026-08-17, after our two `steps` fields disagreed on the same six
sub-games -- theirs 28 where ours said 29 -- and neither was wrong. Each side was reporting
its own move counter, and those were never the same quantity: the book only qualifies a turn
as *full* when it means both sides ("after both the cop and the thief have completed their
move"), so an unqualified step is one agent's move. The fix was not to pick a number but to
name whose counter.
"""

from __future__ import annotations

from p2p_cop_agent.orchestration.turn_loop import TerminalClaimReceived, TurnRecord


def _settled_step(claim: TerminalClaimReceived, turns: list[TurnRecord], step: int) -> int:
    """The step the sub-game ended on, in the numbering of the side that CAUSED it.

    Agreed with `yanell11` on 2026-08-17, after our two `steps` fields disagreed on the
    same six sub-games -- theirs 28 where ours said 29 -- and neither was wrong. Each side
    was reporting its own move counter, and those were never the same quantity: the book
    only qualifies a turn as *full* when it means both sides, so an unqualified step is one
    agent's move. The fix is not to pick a number but to name whose counter:

        steps = the number of the turn on which the terminal condition occurred, in the
                numbering of the side that caused it -- the Cop's turn for a capture, the
                Thief's for a survival. Operationally, the `step` field of the sealed
                record in which the terminal condition first appears.

    **A capture is caused by this peer.** This repository always plays police, so a
    CAPTURE settles on OUR capturing turn, which is our last sealed record: a confirmed
    capture ends the sub-game, so no turn follows it. We were using `claim.step` -- the
    opponent's numbering of their own concession -- which is how friendly-10 filed 26
    against 25 sealed records.

    Anything else keeps the opponent's figure, because anything else was caused by them or
    by nobody: a survival is the Thief's count, and a technical loss has no terminal record
    on either side to read a number off.
    """
    if getattr(claim.outcome, "name", "") == "CAPTURE" and turns:
        return int(turns[-1].step)
    return claim.step if isinstance(claim.step, int) else step - 1
