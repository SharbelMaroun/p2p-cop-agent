"""M5-12: the append-only match log.

The log has to be enough to reconstruct a match for the end-game audit `[AE-36]`,
which puts two disciplines on it. It is **append-only** -- there is no path that
edits or deletes a past event -- and it keeps the **nonce secret until the reveal**
`[AE-18]`: a commitment's hash is written live, but the nonce that opens it cannot be
logged until the post-game reveal, or a leaked log would hand the opponent the seal.
"""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.orchestration.ports import LogManager
from p2p_cop_agent.services.log_manager import LogError, MatchLog

NONCE = "deadbeef" * 4


def test_it_satisfies_the_log_manager_port() -> None:
    assert isinstance(MatchLog(match_id="m1"), LogManager)


def test_it_records_sent_and_received_messages_in_order() -> None:
    log = MatchLog(match_id="m1")
    log.record("sent", {"step": 1, "commit": "a" * 64})
    log.record("received", {"step": 1, "sender": "thief"})
    assert [entry["event"] for entry in log.events] == ["sent", "received"]
    assert log.events[0]["commit"] == "a" * 64


def test_the_log_is_append_only() -> None:
    log = MatchLog(match_id="m1")
    log.record("sent", {"step": 1})
    snapshot = log.events
    log.record("sent", {"step": 2})
    assert len(snapshot) == 1 and len(log.events) == 2  # the earlier view is a copy
    assert not hasattr(log, "delete") and not hasattr(log, "edit")


def test_a_commitment_is_recorded_live_but_a_nonce_is_refused_before_reveal() -> None:
    log = MatchLog(match_id="m1")
    log.record("commit", {"step": 1, "commit": "a" * 64})  # the hash is fine live
    assert log.events[0]["commit"] == "a" * 64
    with pytest.raises(LogError, match="nonce"):
        log.record("sent", {"step": 1, "nonce": NONCE})


def test_after_the_reveal_a_nonce_may_be_recorded() -> None:
    log = MatchLog(match_id="m1")
    log.open_reveal()
    log.record("audit", {"step": 1, "nonce": NONCE})
    assert any("nonce" in entry for entry in log.events)


def test_it_writes_a_per_match_jsonl_file(tmp_path: Path) -> None:
    log = MatchLog.for_match("match-001", tmp_path)
    log.record("sent", {"step": 1})
    log.record("received", {"step": 1})
    lines = (tmp_path / "match-001.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["event"] == "sent"


def test_different_matches_never_share_a_file(tmp_path: Path) -> None:
    MatchLog.for_match("match-a", tmp_path).record("sent", {"step": 1})
    MatchLog.for_match("match-b", tmp_path).record("sent", {"step": 1})
    assert (tmp_path / "match-a.jsonl").exists()
    assert (tmp_path / "match-b.jsonl").exists()


@pytest.mark.parametrize("bad", ["", "   ", "a/b", "a\\b", ".."])
def test_an_unsafe_match_id_is_refused(bad: str) -> None:
    with pytest.raises(LogError):
        MatchLog(match_id=bad)
