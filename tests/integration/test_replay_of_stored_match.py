"""`M9-12c` / `X-17`: the replay app re-verifies a match read back off disk.

Every other replay test in this repository builds records in memory and hands them to the
verifier. This closes the loop the **grader** closes: a sub-game is played, its log is written
as JSON, the file is loaded from disk **by path**, and the verifier reaches `Verified OK`
without ever seeing the objects that produced it.

The distance matters more than it looks. `json.dumps`/`loads` is not identity — an int key
becomes a string, a tuple becomes a list — and the commitment is taken over canonical bytes.
A verifier that only ever sees in-memory dicts can pass forever while every stored log fails,
and the first person to find out would be whoever opened the submission.

Rule 20 makes a verifying replay a threshold condition, and p.81/189 makes the screenshot of
this state "absolute mandatory". So this is the row that decides whether the submission has
evidence at all, not merely whether the code is correct.
"""

from __future__ import annotations

from pathlib import Path

from p2p_cop_agent.replay.load import load_log
from p2p_cop_agent.replay.verify import Verdict, verify_records
from p2p_cop_agent.reporting import log_filename
from tests.integration.test_series_rehearsal import IDENT, _play_sub_game


def stored_log(tmp_path: Path, *, tamper: bool = False) -> Path:
    """Play one sub-game and return the path its log was written to."""
    _play_sub_game(tmp_path, 1, outcome="capture", tamper=tamper)
    return tmp_path / log_filename(IDENT, 1)


def test_a_stored_log_exists_on_disk_after_a_sub_game(tmp_path: Path) -> None:
    assert stored_log(tmp_path).is_file()


def test_a_stored_log_loads_from_its_path_alone(tmp_path: Path) -> None:
    """`load_log` takes a path and nothing else — rule 36's mutual-audit posture. An
    opponent hands over a file, not a Python object."""
    assert load_log(stored_log(tmp_path)).records


def test_a_stored_log_re_verifies_to_verified_ok(tmp_path: Path) -> None:
    """**The row.** Read off disk, re-hashed, compared against the stored commitments."""
    verdict = verify_records(load_log(stored_log(tmp_path)).records)
    assert verdict.verdict is Verdict.VERIFIED_OK, verdict.banner


def test_the_banner_is_the_text_the_mandatory_screenshot_shows(tmp_path: Path) -> None:
    """The banner is evidence rather than a debug aid — p.81/189 requires a screenshot of
    it, so its wording is part of the submission."""
    banner = verify_records(load_log(stored_log(tmp_path)).records).banner
    assert banner.startswith(Verdict.VERIFIED_OK.value)
    assert "re-verified" in banner


def test_a_forged_reveal_survives_the_round_trip_as_tampered(tmp_path: Path) -> None:
    """Proves the round trip *verifies* rather than merely parses. The forgery is written
    into the file, so nothing in memory carries the original past the check."""
    verdict = verify_records(load_log(stored_log(tmp_path, tamper=True)).records)
    assert verdict.verdict is Verdict.TAMPERED
