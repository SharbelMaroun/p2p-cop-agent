"""How a turn message announces that the sub-game is over.

Split out of ``sub_game.py`` when `C-037` added the second terminal claim shape. The
seam is real rather than a line-count concession: running the turn loop and *deciding
what the opponent's turn asserts* are different jobs, and only this one is about
believing a peer we cannot see.

The whole trust model lives in one rule -- **a claim is checked or conceded, never
believed**:

* ``claim_response`` with ``caught: true`` is the Thief answering our
  ``capture_claim``. It is proof, because only the Thief knows where it stood, and
  the audit later re-derives it from that peer's own sealed records.
* ``win_claim`` ``{"type": "survival"}`` is the Thief reporting it outlasted the
  agreed horizon -- the value this repository emits, and the only one the reference
  simulator knows (``peer/turn_sender.py::take_turn`` builds it or ``None``).
* ``win_claim`` ``{"type": "boxed_in"}`` is a **peer extension** we accept and never
  send. Group `uoh-ay26`'s Thief emits it for the book's third capture condition --
  every cardinal neighbour barriered or off-board
  (`police_thief_p2p_Summary.md:810`, Appendix E rule 47). The book settles that
  condition through ``capture_claim`` + ``claim_response`` instead, which this loop
  already does, so we do not adopt it; but refusing the value failed schema
  validation on the *entire* turn message, and a dropped turn hangs the match into
  the 0/0 that rule 35 gives both sides `[C-037]`.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_cop_agent.domain.scoring import Outcome


def decided_by(message: Mapping[str, object] | None) -> tuple[Outcome, str] | None:
    """Read a terminal claim out of the opponent's turn, if it made one.

    Only the opponent's *answer* ends the game, never our own claim: naming a cell in
    ``capture_claim`` asserts nothing until the peer that knows the truth replies.

    ``boxed_in`` is honoured **only from a Thief sender**, and that gate is the point.
    Being walled in is a fact only the Thief can observe, exactly like
    ``claim_response``, and a Thief declaring it concedes against its own interest --
    so believing it costs us nothing. The same words from a *Cop* would assert our
    capture with no proof at all, which rule 22 makes a disqualifying false
    declaration, so that direction is ignored rather than trusted.
    """
    if message is None:
        return None
    answer = message.get("claim_response")
    if isinstance(answer, Mapping) and answer.get("caught") is True:
        return Outcome.CAPTURE, f"the opponent confirmed capture at {answer.get('claim')!r}"
    win = message.get("win_claim")
    kind = win.get("type") if isinstance(win, Mapping) else None
    if kind == "survival":
        return Outcome.SURVIVAL, "the opponent claimed survival"
    if kind == "boxed_in" and message.get("sender") == "thief":
        return Outcome.CAPTURE, "the opponent declared itself boxed in"
    return None
