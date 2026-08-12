"""C-044: the consensus preimage reproduces the opponent's live SHA, bit for bit.

`uoh-ay26` published their verification-series consensus digest; on 2026-08-12 we
reconstructed it exactly from our own six logs under their identifiers. That
reconstruction is pinned here as a golden test: if either the row projection, the
canonicalisation, or the uid derivation drifts, this digest changes and the test
names the day the teams stop agreeing.
"""

from p2p_cop_agent.reporting.series_consensus import (
    consensus_envelope,
    consensus_sha,
    derive_game_uid,
)

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


def test_the_verification_series_sha_reproduces_bit_for_bit() -> None:
    uid = derive_game_uid(TERMS, GROUPS)
    assert consensus_sha("G003", uid, rows()) == THEIR_SHA


def test_group_order_does_not_matter() -> None:
    """The pair is sorted inside the derivation; callers need not care."""
    assert derive_game_uid(TERMS, list(reversed(GROUPS))) == derive_game_uid(TERMS, GROUPS)


def test_the_envelope_is_the_accepted_shape() -> None:
    """Empty records + 64-hex sha: exactly what our own C-040 schema accepts."""
    from p2p_cop_agent.protocol.messages import validate_message

    envelope = consensus_envelope(THEIR_SHA)
    validate_message("audit", envelope)
    assert envelope["records"] == []
