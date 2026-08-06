"""`M8-12b`: the detection path is not self-only.

Verifying our own honest log proves the reader agrees with the writer. Catching a forgery
in a log **we did not write** is the thing rule 36's mutual audit is actually for, and it
is what stands between an opponent rewriting a losing move and a clean `Verified OK`.

Each test here is a different shape of lie, chosen because each one defeats a cheaper
check than the last: a rewritten payload defeats eyeballing, a swapped nonce defeats
field-shape validation, and a rewritten *visible* field defeats the digest check itself.
That last one found a real hole in our verifier — see `_visible_fields_contradicting_the_seal`.
"""

from __future__ import annotations

from pathlib import Path

from p2p_cop_agent.replay import Replay, Verdict, load_log
from tests.integration.foreign_log_writer import foreign_writer, write_foreign_log


def _replay(tmp_path: Path, document: dict) -> Replay:
    return Replay(load_log(write_foreign_log(tmp_path, document)))


def test_a_forged_foreign_log_is_detected(tmp_path: Path) -> None:
    """An opponent rewriting their own move after the fact — the attack the whole
    commit-reveal scheme exists to stop."""
    document = foreign_writer(5)
    document["records"][3]["payload"]["move"] = "W"  # sealed as "N"; rewritten afterwards
    document["records"][3]["move"] = "W"

    replay = _replay(tmp_path, document)
    assert replay.stamp is Verdict.TAMPERED
    assert replay.go_to_first_divergence() == 3
    assert replay.record["step"] == 4


def test_a_foreign_log_with_a_swapped_nonce_is_detected(tmp_path: Path) -> None:
    """Swapping two valid nonces keeps every field well-formed and every value real — a
    shape check, or an "is this 32 hex characters" check, would pass it."""
    document = foreign_writer(4)
    records = document["records"]
    records[0]["nonce"], records[1]["nonce"] = records[1]["nonce"], records[0]["nonce"]
    assert _replay(tmp_path, document).stamp is Verdict.TAMPERED


def test_a_foreign_log_with_an_appended_step_is_detected(tmp_path: Path) -> None:
    """Inventing a step nobody played, with a plausible commit copied from a real one.

    **This test found a real hole.** A digest check alone passed it: the copied payload,
    nonce and commit are internally consistent, so only the record's visible `step` was a
    lie — and nothing was comparing the visible fields to the sealed ones.
    """
    document = foreign_writer(3)
    document["records"].append({**document["records"][0], "step": 4})
    assert _replay(tmp_path, document).stamp is Verdict.TAMPERED


def test_rewriting_only_the_displayed_move_is_detected(tmp_path: Path) -> None:
    """The sharper form of the same hole, and the one that matters at an audit: leave the
    sealed payload alone so every digest matches, and change only what the board shows.
    Without the visible-field check this replays a fictional game under a green stamp.

    `:1691` is the sentence that closes it — the viewer re-encodes "the Nonce and the move
    **appearing in the log**", so the move appearing in the log must be the move sealed.
    """
    document = foreign_writer(4)
    record = document["records"][2]
    assert record["move"] == record["payload"]["move"], "honest before we touch it"
    record["move"] = "X"

    replay = _replay(tmp_path, document)
    assert replay.stamp is Verdict.TAMPERED
    assert "contradicts the sealed payload" in replay.banner


def test_a_deleted_step_is_reported_though_the_digests_still_pass(tmp_path: Path) -> None:
    """Removing a step you would rather nobody replayed.

    **This test used to assert only that its own fixture had a gap** — `steps == [1,2,4,5]`
    — which would have passed against no implementation at all. It now asserts what the
    product does: every surviving digest verifies, so the banner stays green, and the gap
    is surfaced by `sequence` under rule 35 rather than misreported as a rule 19 forgery.
    """
    document = foreign_writer(5)
    del document["records"][2]

    replay = _replay(tmp_path, document)
    assert replay.stamp is Verdict.VERIFIED_OK, "no digest was touched"
    finding = next(f for f in replay.sequence.findings if f.kind == "gap")
    assert finding.rule == "AE-35" and "[3]" in finding.detail


def test_a_reordered_foreign_log_verifies_but_is_reported(tmp_path: Path) -> None:
    """The deliberate asymmetry. Neither the book nor the reference requires ordering, so
    red-bannering an honest opponent over it would be a false accusation with no appeal
    (`:1769`) — and rule 35 scores zero for *both* teams on a contradicting report."""
    document = foreign_writer(5)
    document["records"] = [document["records"][i] for i in (0, 3, 1, 4, 2)]

    replay = _replay(tmp_path, document)
    assert replay.stamp is Verdict.VERIFIED_OK
    assert any(f.kind == "out-of-order" for f in replay.sequence.findings)


def test_stripping_a_single_nonce_is_detected_rather_than_read_as_in_play(
    tmp_path: Path,
) -> None:
    """All nonces absent is an honest in-play log. One absent is a log that was revealed
    and then interfered with, and it must reach a verdict rather than a refusal."""
    document = foreign_writer(4)
    del document["records"][1]["nonce"]

    replay = _replay(tmp_path, document)
    assert replay.stamp is Verdict.TAMPERED
    assert "nonce" in replay.verdict.checks[1].reason


def test_every_forgery_above_leaves_the_other_steps_verifiable(tmp_path: Path) -> None:
    """The match is void either way, but an auditor's next question is *which step* — and
    a verifier that gave up at the first failure could not answer it."""
    document = foreign_writer(6)
    document["records"][2]["commit"] = "0" * 64

    checks = _replay(tmp_path, document).verdict.checks
    assert [check.ok for check in checks] == [True, True, False, True, True, True]
