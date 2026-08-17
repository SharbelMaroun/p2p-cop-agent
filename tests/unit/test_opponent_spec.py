"""Reading the opponent's commit out of their own Step-0 attestation.

Rule 53 wants a commit per game per team. Ours filed theirs as `"unknown"` in every report
ever sent, while the value sat in the first record of every audit they disclosed. The point
of reading it rather than transcribing it: `yanell11` gave us `27060c13…` by email, run 8
actually played on `33119340…`, and our own interop sheet was equally stale within the hour.
A pasted number describes when it was written; the attestation describes the code that ran.
"""

from p2p_cop_agent.reporting.opponent_spec import opponent_commit, opponent_step_zero

COMMIT = "33119340729f77b14635d72dcf9851b0dc6e2258"


def audit(*payloads: dict) -> list[dict]:
    return [{"records": [{"payload": p} for p in payloads]}]


STEP_ZERO = {"type": "system_spec", "github_commit": COMMIT,
             "group_name": "YANELL11", "token_budget": 200000, "step": 0}
A_MOVE = {"type": "turn", "step": 1, "move": "move:N", "position": [0, 1]}


def test_it_finds_the_commit_in_the_step_zero_record() -> None:
    assert opponent_commit(audit(STEP_ZERO, A_MOVE)) == COMMIT


def test_it_finds_step_zero_wherever_it_sits() -> None:
    assert opponent_commit(audit(A_MOVE, STEP_ZERO)) == COMMIT


def test_a_record_numbered_zero_counts_even_without_the_type() -> None:
    untyped = {"step": 0, "github_commit": COMMIT}
    assert opponent_commit(audit(untyped)) == COMMIT


def test_no_attestation_returns_none_rather_than_a_placeholder() -> None:
    """None keeps "they did not disclose it" distinct from "we did not look"."""
    assert opponent_commit(audit(A_MOVE)) is None
    assert opponent_commit([]) is None
    assert opponent_commit(None) is None


def test_a_blank_or_missing_commit_is_not_a_commit() -> None:
    for value in ("", "   ", None, 12345, []):
        assert opponent_commit(audit({"type": "system_spec", "github_commit": value})) is None


def test_malformed_records_do_not_raise() -> None:
    """An opponent's disclosure is hostile input; it must not crash artifact writing."""
    assert opponent_commit([{"records": [None, 7, "x", {"payload": "not a mapping"}]}]) is None
    assert opponent_commit([{}, {"records": None}]) is None


def test_the_whole_attestation_is_available_not_just_the_commit() -> None:
    spec = opponent_step_zero(audit(STEP_ZERO))
    assert spec["group_name"] == "YANELL11"
    assert spec["token_budget"] == 200000
