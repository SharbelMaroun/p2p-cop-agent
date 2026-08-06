"""`M8-02d`: which hash construction the replay verifier is allowed to use.

The row this closes was written on a wrong premise. It read: "Record why the book's
chapter-7 verifier is not used … Disclosed under the p.5 contradiction clause" — i.e. we
had found a contradiction between chapter 5 and chapter 7 and owed the lecturer a
disclosure.

Asked directly, the sources say otherwise, in the book's own voice at `:1757` (p.58/146):
"the sketch simplified the input for the sake of the illustration; in practice the
signature covers all components of the step — Intent, Move, State and Nonce — as detailed
in the protocol in Chapter 5."

So chapter 7's listing is a **teaching simplification that names chapter 5 as normative**,
not a rival specification. Filing it as a conflict would have recorded a disagreement the
sources do not have, and invited the lecturer to resolve something already resolved. What
is owed is this note, not a disclosure.

The tests below pin the difference so nobody "fixes" our verifier towards p.74 later.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from p2p_cop_agent.replay import LogNotReplayableError, Verdict, parse_log, verify_records

NONCE = "a1" * 16


def _canonical(payload: object) -> bytes:
    return json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _record(step: int, move: str = "N", nonce: str = NONCE) -> dict:
    payload = {"step": step, "move": move, "intent": True}
    return {"step": step, "sender": "police", "move": move, "hint": "north", "intent": True,
            "payload": payload, "nonce": nonce,
            "commit": hashlib.sha256(_canonical(payload) + b"|" + nonce.encode()).hexdigest()}


# --- the chapter-7 sketch and why we do not implement it --------------------------------


def test_the_chapter_seven_sketch_would_verify_none_of_our_records() -> None:
    """`:1733` computes `sha256(f"{nonce}|{move}")`: nonce first, and only the bare move.
    The point is that the difference is total rather than subtle — a viewer written to the
    sketch would red-banner an honest log at step 1 and disqualify us under `:1769`.
    """
    record = _record(1)
    sketch = hashlib.sha256(f"{record['nonce']}|{record['move']}".encode()).hexdigest()
    assert sketch != record["commit"]


def test_our_construction_is_payload_then_nonce_not_nonce_then_move() -> None:
    """Pins both differences separately, so a future "fix" that swaps only the order — or
    only the content — still fails. Either alone would look like a plausible correction."""
    payload = {"step": 1, "move": "N", "intent": True}
    ours = hashlib.sha256(_canonical(payload) + b"|" + NONCE.encode()).hexdigest()

    swapped_order = hashlib.sha256(NONCE.encode() + b"|" + _canonical(payload)).hexdigest()
    bare_move = hashlib.sha256(_canonical(payload["move"]) + b"|" + NONCE.encode()).hexdigest()
    assert ours != swapped_order
    assert ours != bare_move


def test_the_sealed_payload_covers_intent_which_the_sketch_would_leave_unbound() -> None:
    """`:1757` names Intent explicitly among the components the real signature covers.
    Under the sketch, a bluff flag could be rewritten after the fact for free — and rule 22
    turns a false capture declaration into "score of zero and technical loss"."""
    honest = _record(1)
    lied = {**honest, "payload": {**honest["payload"], "intent": False}}
    assert verify_records([lied]).verdict is Verdict.TAMPERED


# --- an in-play log is refused, not accused ---------------------------------------------


def test_a_log_whose_nonces_are_all_absent_is_refused_rather_than_called_tampered() -> None:
    """Rule 18 *requires* an in-play log to have no nonces. Stamping it `TAMPERED` would
    accuse an honest peer of the one thing `:1769` gives no appeal against."""
    in_play = {"records": [{k: v for k, v in _record(n).items() if k not in ("nonce", "payload")}
                           for n in (1, 2)]}
    with pytest.raises(LogNotReplayableError, match="in-play log"):
        parse_log(in_play)


def test_the_refusal_names_the_rule_and_points_at_settlement() -> None:
    """A peer who never reveals is a settlement matter (`Settled.UNANSWERED`), not a
    forgery. The message has to say so, or the operator reaches for the wrong sanction."""
    in_play = {"records": [{"step": 1, "commit": "0" * 64}]}
    with pytest.raises(LogNotReplayableError, match="settlement matter"):
        parse_log(in_play)


def test_but_a_log_missing_only_some_nonces_goes_through_and_fails() -> None:
    """Revealed and then interfered with — that is forgery, and it must reach a verdict."""
    log = {"records": [_record(1), _record(2), _record(3)]}
    del log["records"][1]["nonce"]
    assert verify_records(parse_log(log).records).verdict is Verdict.TAMPERED


# --- a file that is not a log at all ----------------------------------------------------


@pytest.mark.parametrize(
    ("document", "expected"),
    [
        ([{"step": 1}], "top level is not a JSON object"),
        ("just a string", "top level is not a JSON object"),
        ({"summary": {"outcome": "capture"}}, "no `records` array"),
        ({"records": []}, "no `records` array"),
        ({"records": "1,2,3"}, "no `records` array"),
    ],
)
def test_a_document_that_is_not_a_log_is_refused_with_the_reason(
    document: object, expected: str
) -> None:
    """Each of these could arrive at a real audit — a bare array, a config passed by
    mistake, an emptied log. None may reach the verifier and come back with a verdict,
    because "we could not find any records" and "the records verify" are different claims
    and only one of them belongs on a submission screenshot.
    """
    with pytest.raises(LogNotReplayableError, match=expected):
        parse_log(document)
