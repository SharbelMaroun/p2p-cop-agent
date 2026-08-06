"""`M7-24`: the log a stranger re-verifies, and the nonce that must not appear yet.

`:1690` says exactly what an auditor does with this file: the replay viewer "takes the
Nonce and the move appearing in the log, re-encodes them, and compares the result to the
original Commitment value using the SHA-256 algorithm". So the binding test here is not
that the fields exist — it is that a **recomputation using only the file** reproduces
every commitment.

The other half is timing. Rule 18 is Mandatory — "Keep the Nonce secret until the end of
the game. Sanction: Disqualification due to risk of dictionary attack" — and that is a
rule about *when a byte exists*, which no inspection of the finished artifact can detect.
The finished log is identical whether the nonces were written at the end or leaked at
step one. Only refusing to build the intermediate state can enforce it.
"""

from __future__ import annotations

import hashlib

import pytest

from p2p_cop_agent.protocol.commit import canonical_payload_bytes
from p2p_cop_agent.reporting import MatchIdentity
from p2p_cop_agent.reporting.log_artifact import (
    LogArtifactError,
    build_log,
    is_revealed,
    reveal_log,
)

IDENT = MatchIdentity("demo-series", "b" * 32)


def _commit(payload: dict, nonce: str) -> str:
    return hashlib.sha256(canonical_payload_bytes(payload) + b"|" + nonce.encode()).hexdigest()


PAYLOADS = [{"step": n, "move": m} for n, m in ((1, "N"), (2, "E"))]
NONCES = ["a" * 32, "c" * 32]
STEPS = [
    {"step": n + 1, "sender": "cop", "commit": _commit(p, x), "move": p["move"],
     "hint": "near the north edge", "intent": bool(n)}
    for n, (p, x) in enumerate(zip(PAYLOADS, NONCES, strict=True))
]
REVEALS = [{"step": n + 1, "nonce": x, "payload": p}
           for n, (p, x) in enumerate(zip(PAYLOADS, NONCES, strict=True))]
SUMMARY = {"outcome": "capture", "turns": 2, "cop_score": 20, "tokens_total": 0}


def _log():
    return build_log(identity=IDENT, sub_game=1, steps=STEPS, summary=SUMMARY)


# --- M7-24 / M7-24a: independently re-verifiable ---------------------------------------


def test_a_stranger_can_recompute_every_commitment_from_the_file_alone() -> None:
    """`M7-24`'s condition — "a third party can re-verify **without our code**" — and
    `:1690`'s procedure. This is the test that matters; the rest are its preconditions."""
    revealed = reveal_log(_log(), REVEALS)
    for record in revealed["audit"]["records"]:
        recomputed = hashlib.sha256(
            canonical_payload_bytes(record["payload"]) + b"|" + record["nonce"].encode()
        ).hexdigest()
        assert recomputed == record["commit"]


def test_a_tampered_payload_fails_that_recomputation() -> None:
    """The `TAMPERED` path. If altering a move still verified, the log would be evidence
    of nothing — `:1693` invalidates the replay on "even the slightest change"."""
    revealed = reveal_log(_log(), REVEALS)
    record = revealed["audit"]["records"][0]
    forged = {**record["payload"], "move": "S"}
    recomputed = hashlib.sha256(
        canonical_payload_bytes(forged) + b"|" + record["nonce"].encode()
    ).hexdigest()
    assert recomputed != record["commit"]


def test_every_step_records_its_hint_and_intent() -> None:
    """`M7-24c`: the verbal layer is auditable too, and a hint without its intent flag
    cannot be judged — there would be no way to tell a bluff from a mistake."""
    for step in _log()["steps"]:
        assert "hint" in step and "intent" in step


# --- M7-24b: the nonce may not exist yet ----------------------------------------------


def test_the_in_play_log_carries_no_nonce_anywhere() -> None:
    """Rule 18 (Mandatory), sanction "disqualification due to risk of dictionary attack"."""
    assert "nonce" not in repr(_log()["steps"])
    assert _log()["audit"] is None


def test_a_step_carrying_a_nonce_is_refused_at_build_time() -> None:
    """The constraint made unrepresentable. A log written with inline nonces is
    byte-identical to a correct one once the game ends, so no inspection of the finished
    artifact could ever catch it — only refusing to build the intermediate state can."""
    leaky = [{**STEPS[0], "nonce": NONCES[0]}, STEPS[1]]
    with pytest.raises(LogArtifactError, match="nonce stays secret"):
        build_log(identity=IDENT, sub_game=1, steps=leaky, summary=SUMMARY)


def test_a_step_carrying_the_revealed_payload_is_refused_too() -> None:
    """The payload is the other half of the reveal; a nonce guard alone would be theatre."""
    leaky = [{**STEPS[0], "payload": PAYLOADS[0]}, STEPS[1]]
    with pytest.raises(LogArtifactError, match="payload"):
        build_log(identity=IDENT, sub_game=1, steps=leaky, summary=SUMMARY)


def test_the_reveal_is_the_only_way_nonces_enter_and_it_is_visible() -> None:
    assert not is_revealed(_log())
    assert is_revealed(reveal_log(_log(), REVEALS))


# --- reveals must line up with what was played ----------------------------------------


def test_a_reveal_count_that_disagrees_with_the_steps_is_refused() -> None:
    """A missing reveal is an unverifiable step; a spare one is a step never played."""
    with pytest.raises(LogArtifactError, match="every step is revealed exactly once"):
        reveal_log(_log(), REVEALS[:1])


def test_a_reveal_for_the_wrong_step_is_refused() -> None:
    swapped = [REVEALS[1], REVEALS[0]]
    with pytest.raises(LogArtifactError, match="reveal 0 is for step"):
        reveal_log(_log(), swapped)


def test_a_reveal_missing_its_nonce_or_payload_is_refused() -> None:
    thin = [{"step": 1, "nonce": NONCES[0]}, REVEALS[1]]
    with pytest.raises(LogArtifactError, match="missing payload"):
        reveal_log(_log(), thin)


def test_a_log_with_no_steps_is_refused_rather_than_emitted_empty() -> None:
    with pytest.raises(LogArtifactError, match="cannot be audited"):
        build_log(identity=IDENT, sub_game=1, steps=[], summary=SUMMARY)


def test_the_summary_and_identity_ride_along() -> None:
    log = _log()
    assert log["summary"]["outcome"] == "capture"
    assert log["game_uid"] == IDENT.game_uid
    assert log["links"]["log"] == "log_demo-series_g01.json"
