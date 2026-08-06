"""`M8-08d` / `M8-08c`: detecting a reordered log — and deliberately not bannering it.

Written after a direct probe showed the shipped verifier stamping `Verified OK` on all
three structural forgeries: a shuffle, a deletion, and a duplicate. Every commitment covers
one record, so none of them touches a digest.

**Why the finding does not flip the banner.** Both sources say sequence checking is neither
mandated nor implemented — the book's rule 19 is "any mismatch **in the digest**"
(p.129/271), with a missing step answering instead to rule 35's contradictory reports and
rule 5's illegal state jump; the reference verifies each record "with no reference to its
place in the sequence", never sorts, and rejects no duplicate.

So a differently-ordered log is not evidence of forgery. Red-bannering one would be a false
accusation carrying no appeal (`:1769`), and rule 35 scores zero for *both* teams on a
contradicting report. Detect and report; let settlement compare the two logs.
"""

from __future__ import annotations

import hashlib
import json

from p2p_cop_agent.replay import Verdict, inspect_sequence, verify_records

NONCE = "c3" * 16


def _record(step: int) -> dict:
    payload = {"step": step, "move": "NSEW"[step % 4]}
    canonical = json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return {"step": step, "move": payload["move"], "payload": payload, "nonce": NONCE,
            "commit": hashlib.sha256(canonical + b"|" + NONCE.encode()).hexdigest()}


def _records(count: int = 5) -> list[dict]:
    return [_record(n) for n in range(1, count + 1)]


def test_a_clean_log_reports_an_intact_sequence() -> None:
    report = inspect_sequence(_records(5))
    assert report.contiguous
    assert report.summary == "sequence intact — 5 steps, 1..5"


def test_a_reordered_log_is_detected() -> None:
    """`M8-08d`. Every digest is still valid — the shuffle is the whole forgery."""
    records = _records(5)
    shuffled = [records[i] for i in (0, 3, 1, 4, 2)]

    assert verify_records(shuffled).verdict is Verdict.VERIFIED_OK, "hashes cannot see it"
    report = inspect_sequence(shuffled)
    assert not report.contiguous
    assert any(f.kind == "out-of-order" for f in report.findings)


def test_a_deleted_step_is_detected_as_a_gap() -> None:
    """This replaces a test that asserted only that its *fixture* had a gap and never that
    the code noticed — a test which would have passed against no implementation at all."""
    records = _records(5)
    del records[2]

    assert verify_records(records).verdict is Verdict.VERIFIED_OK
    finding = next(f for f in inspect_sequence(records).findings if f.kind == "gap")
    assert "[3]" in finding.detail and finding.rule == "AE-35"


def test_a_duplicated_step_is_detected() -> None:
    records = _records(4)
    records.insert(2, records[1])

    assert verify_records(records).verdict is Verdict.VERIFIED_OK
    finding = next(f for f in inspect_sequence(records).findings if f.kind == "duplicate")
    assert "[2]" in finding.detail


def test_records_without_an_integer_step_are_reported_not_crashed_on() -> None:
    records = _records(3)
    records[1] = {**records[1], "step": "two"}
    assert any(f.kind == "unnumbered" for f in inspect_sequence(records).findings)


def test_a_boolean_step_is_not_mistaken_for_an_integer() -> None:
    """`True == 1` in Python, so a bool passes `isinstance(int)` and reads as step 1 — a
    forgery that survives precisely because it type-checks."""
    records = _records(2)
    records[0] = {**records[0], "step": True}
    assert any(f.kind == "unnumbered" for f in inspect_sequence(records).findings)


def test_an_empty_log_reports_nothing_rather_than_raising() -> None:
    assert inspect_sequence([]).contiguous


def test_a_structural_anomaly_never_changes_the_cryptographic_verdict() -> None:
    """**The assertion this module exists for.** Neither source requires ordering, so an
    honest log ordered differently must not be red-bannered."""
    records = _records(6)
    mangled = [records[i] for i in (5, 0, 1, 3, 4)]  # shuffled and one deleted

    assert verify_records(mangled).verdict is Verdict.VERIFIED_OK
    assert not inspect_sequence(mangled).contiguous


def test_every_finding_names_the_rule_it_answers_to() -> None:
    """The sanctions differ — rule 19 is 0 for the falsifying group, rule 35 is 0 for both
    — so a finding that does not name its rule invites the wrong one being applied."""
    records = _records(5)
    del records[1]
    records.append(records[0])
    for finding in inspect_sequence(records).findings:
        assert finding.rule.startswith("AE-") and finding.detail


def test_the_summary_of_a_damaged_log_lists_every_finding_with_its_rule() -> None:
    """What an operator actually reads. A summary saying only "sequence problem" would
    leave them guessing which sanction applies, which is the whole reason for the split."""
    records = _records(5)
    del records[2]
    records.append(records[0])

    summary = inspect_sequence(records).summary
    assert "gap" in summary and "duplicate" in summary
    assert "[AE-35]" in summary and "intact" not in summary
