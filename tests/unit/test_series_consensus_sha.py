"""C-046: the consensus digest reproduces the LECTURER's own artifact, bit for bit.

The pin that matters is `test_the_reference_sample_run_reproduces`, because its expected
value comes from outside every implementation involved:
`docs/sample-run/result_segal-police-team-vs-segal-thief-team.json` in
`rmisegal/Game-P2P-Cop-Chase` ships `mutual_agreement.sha256` and the scope below is that
file's own `game_id`, `final_result` and single sub-game row. Nothing here asserts about
itself -- the earlier golden (`C-044`, kept below) pinned an *opponent's* digest, which
proved only that two peers agreed with each other, and they were both wrong.

If the row projection, the aggregate key set, or the serialization drifts, this digest
changes and the test names the day we stop settling against the course's own tooling.
"""

from p2p_cop_agent.reporting.series_consensus import (
    consensus_envelope,
    consensus_sha,
    derive_game_uid,
    legacy_consensus_sha,
)

# Transcribed from the lecturer's artifact; the hash is the value that file ships.
REFERENCE_GAME_ID = "segal-police-team-vs-segal-thief-team"
REFERENCE_FINAL = {
    "total_score": {"segal-police-team": 20, "segal-thief-team": 5},
    "sub_games_won": {"segal-police-team": 1, "segal-thief-team": 0},
    "ties": 0,
    "winner_group": "segal-police-team",
    "series_tie": False,
}
REFERENCE_ROWS = [{
    "sub_game_number": 1,
    "roles": {"segal-thief-team": "thief", "segal-police-team": "police"},
    "result": "capture",
    "score": {"segal-thief-team": 5, "segal-police-team": 20},
}]
REFERENCE_SHA = "31d678dadbd226dcb1ad87848386416702dcf0735746d7c812350ebc69cbdc81"

TERMS = {"board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.1,
         "emit_intensity": 0.9, "min_center_intensity": 0.5, "max_steps": 35,
         "barriers_max": 14, "setting": "Haifa", "hint_max_words": 15,
         "axis_origin_corner": "top-left", "axis_start_index": 0,
         "thief_start": [3, 3], "cop_start": [0, 0], "num_games": 6}
GROUPS = ["sharNamr", "uoh-ay26"]
THEIR_SHA = "fd362f67d4c606b7ace1b560991544c922a69bde514092103f739bdc9bb20680"


def rows() -> list[dict]:
    """The verification series, as template rows (our roles use `cop`)."""
    out = []
    for n, our_role, result in [(1, "thief", "survival"), (2, "cop", "capture"),
                                (3, "thief", "survival"), (4, "cop", "capture"),
                                (5, "thief", "survival"), (6, "cop", "capture")]:
        roles = {"sharNamr": our_role, "uoh-ay26": "thief" if our_role == "cop" else "cop"}
        score = {g: ({"cop": 20, "thief": 5} if result == "capture"
                     else {"cop": 5, "thief": 10})[r] for g, r in roles.items()}
        out.append({"sub_game_number": n, "result": result, "roles": roles,
                    "score": score})
    return out


def test_the_uid_derivation_matches_their_procedure() -> None:
    assert derive_game_uid(TERMS, GROUPS) == "7b1d942e-5a9c-6e0c-312a-761dd7dec131"


def test_the_reference_sample_run_reproduces() -> None:
    """The pin that comes from outside every implementation here (`C-046`)."""
    assert consensus_sha(REFERENCE_GAME_ID, REFERENCE_FINAL, REFERENCE_ROWS) == REFERENCE_SHA


def test_the_compact_form_does_not_reproduce_it() -> None:
    """A pin that cannot fail against the wrong serialization pins nothing.

    This is the whole defect: compact JSON is what the rest of the project hashes with,
    it is a one-argument difference, and it settles against nobody. `effb75c4...` is what
    the lecturer's own scope produces under it.
    """
    import hashlib
    import json

    from p2p_cop_agent.reporting.series_consensus import AGGREGATE_KEYS, consensus_rows

    preimage = {"game_id": REFERENCE_GAME_ID,
                "aggregate": {k: REFERENCE_FINAL[k] for k in AGGREGATE_KEYS},
                "sub_games": consensus_rows(REFERENCE_ROWS)}
    compact = json.dumps(preimage, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":")).encode("utf-8")
    assert hashlib.sha256(compact).hexdigest() != REFERENCE_SHA


def test_the_legacy_form_still_reproduces_the_reported_series() -> None:
    """`C-044`'s golden, demoted but kept: those two series must stay re-derivable.

    It pins an *opponent's* digest rather than the course's, which is exactly why it was
    not enough -- both peers reproduced it and neither matched the reference.
    """
    uid = derive_game_uid(TERMS, GROUPS)
    assert legacy_consensus_sha("G003", uid, rows()) == THEIR_SHA


def test_group_order_does_not_matter() -> None:
    """The pair is sorted inside the derivation; callers need not care."""
    assert derive_game_uid(TERMS, list(reversed(GROUPS))) == derive_game_uid(TERMS, GROUPS)


def test_the_envelope_is_the_accepted_shape() -> None:
    """Empty records + 64-hex sha: exactly what our own C-040 schema accepts."""
    from p2p_cop_agent.protocol.messages import validate_message

    envelope = consensus_envelope(THEIR_SHA)
    validate_message("audit", envelope)
    assert envelope["records"] == []
