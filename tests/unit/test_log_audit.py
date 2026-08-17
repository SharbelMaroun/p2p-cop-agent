"""The report's `audit` block, earned rather than asserted.

`sub_game_row` emitted `{"log_verified": True, "tampered": False}` as hardcoded literals
until 2026-08-17, so every result report claimed a verification that had never run. These
tests pin the two properties that make the replacement worth having: a genuine log passes,
and an edited one FAILS. Without the second, the check is decoration.
"""

from p2p_cop_agent.protocol.commit import move_commit
from p2p_cop_agent.reporting.log_audit import verify_own_commitments

NONCE = "6916c9758252c34b7f456785b9f926d8"
OTHER = "0f1e2d3c4b5a69788796a5b4c3d2e1f0"


def sealed(payload: dict, nonce: str = NONCE, commit: str | None = None) -> dict:
    return {"payload": payload, "nonce": nonce,
            "commit": commit if commit is not None else move_commit(payload, nonce)}


def test_a_genuine_log_verifies() -> None:
    records = [sealed({"step": n, "move": "MOVE:NORTH", "position": [n, 0]})
               for n in range(1, 6)]
    assert verify_own_commitments(records) == {
        "log_verified": True, "tampered": False, "steps_checked": 5}


def test_an_edited_payload_cannot_reproduce_its_own_commitment() -> None:
    """The property the whole check exists for: rewriting history is detectable."""
    honest = {"step": 1, "move": "MOVE:NORTH", "position": [1, 0]}
    record = sealed(honest)
    record["payload"] = {**honest, "move": "MOVE:SOUTH"}      # changed after committing
    result = verify_own_commitments([record])
    assert result["log_verified"] is False
    assert result["tampered"] is True


def test_a_swapped_nonce_is_caught() -> None:
    payload = {"step": 1, "move": "MOVE:EAST", "position": [0, 1]}
    record = sealed(payload)
    record["nonce"] = OTHER
    assert verify_own_commitments([record])["tampered"] is True


def test_an_empty_log_is_not_verified_rather_than_vacuously_true() -> None:
    """A log with nothing in it has not been verified; it has not been contradicted.

    Returning True here is how the old literal was defensible-looking and wrong: the
    honest answer to "did the audit pass" when nothing was checked is no.
    """
    assert verify_own_commitments([]) == {
        "log_verified": False, "tampered": False, "steps_checked": 0}


def test_a_malformed_nonce_fails_the_check_instead_of_raising() -> None:
    """`move_commit` rejects a non-32-hex nonce; an uncomputable commit is a failed check.

    It must not propagate: the report is Mandatory, and an exception here would replace a
    finding with a traceback -- which is exactly how the last diagnosis lost its evidence.
    """
    record = {"payload": {"step": 1, "move": "MOVE:STAY"}, "nonce": "abc", "commit": "x"}
    assert verify_own_commitments([record]) == {
        "log_verified": False, "tampered": True, "steps_checked": 1}


def test_one_bad_step_among_many_fails_the_whole_log() -> None:
    records = [sealed({"step": n, "move": "MOVE:NORTH"}) for n in range(1, 5)]
    records[2]["commit"] = move_commit({"step": 99, "move": "MOVE:WEST"}, NONCE)
    result = verify_own_commitments(records)
    assert result["log_verified"] is False
    assert result["steps_checked"] == 4


def test_missing_fields_are_failures_not_crashes() -> None:
    for record in ({}, {"payload": {}}, {"nonce": NONCE}, {"commit": "x"}):
        assert verify_own_commitments([record])["log_verified"] is False
