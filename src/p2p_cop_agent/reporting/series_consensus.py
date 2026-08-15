"""The post-series consensus exchange (`C-044`/`C-045`, corrected `C-046`).

After game 6 each team emits one `series_consensus` audit envelope: empty records and
a `consensus_sha` over `{game_id, aggregate, sub_games}`, where each row carries only
cross-peer facts (number, result, roles with `cop` normalised to `police`, sorted
per-team scores, winner). Local timestamps, tokens and filenames are deliberately
excluded so both sides can agree without byte-identical local observations.

**The serialization is SPACED, not the compact canonical form the rest of this project
uses**, and that is the reference's construction rather than a preference -- see
:func:`consensus_sha`, which records how it was settled against the lecturer's own
sample-run artifact on 2026-08-15 and what the previous form cost.

Identifier convention (`uoh-ay26`'s 2026-08-12 message, adopted): `game_id` is the
mutually agreed series label and `game_uid` is `derive_game_uid(terms, group_ids)` -- a
UUID from the first 16 bytes of SHA-256 over `canonical(terms) + "|" + the sorted group
ids joined by "|"`. The uid is published in the envelope but is **not** part of the
consensus preimage; hashing it was our own addition, kept only in
:func:`legacy_consensus_sha` so `G008` and `G009` remain reproducible.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Mapping, Sequence

WIRE_ROLE = {"cop": "police", "police": "police", "thief": "thief"}

# The aggregate block of the consensus preimage, in the reference's own key set. Fixed
# rather than "whatever `final_result` happens to carry": our template also emits
# `tokens_total_series`, `first_meeting_between_groups`, `games_played_including_this`
# and `diversity_reward_applied`, none of which the reference hashes -- including one of
# them would produce a digest no other implementation reproduces.
AGGREGATE_KEYS = ("total_score", "sub_games_won", "ties", "winner_group", "series_tie")


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def _spaced(value: object) -> bytes:
    """The reference's serialization for the consensus digest: DEFAULT separators.

    `json.dumps` with no `separators=` argument emits `", "` and `": "`. Passing the
    compact pair here is the single-character mistake that makes a correct implementation
    settle against nobody, so the two forms are separate functions rather than a flag.
    """
    return json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")


def derive_game_uid(terms: Mapping[str, object], group_ids: Sequence[str]) -> str:
    """Their shared derivation: a UUID from the terms and the sorted group pair."""
    seed = _canonical(dict(terms)) + b"|" + "|".join(sorted(group_ids)).encode("utf-8")
    return str(uuid.UUID(bytes=hashlib.sha256(seed).digest()[:16]))


def consensus_rows(template_rows: Sequence[Mapping[str, object]]) -> list[dict]:
    """Project the template's per-sub-game rows onto the consensus preimage rows."""
    rows = []
    for row in sorted(template_rows, key=lambda r: int(r["sub_game_number"])):  # type: ignore[call-overload]
        roles = {gid: WIRE_ROLE[str(role)] for gid, role in dict(row["roles"]).items()}  # type: ignore[call-overload]
        score = dict(sorted(dict(row["score"]).items()))  # type: ignore[call-overload]
        winner = None if len(set(score.values())) == 1 else max(score, key=score.get)  # type: ignore[arg-type]
        rows.append({
            "sub_game_number": int(row["sub_game_number"]),  # type: ignore[call-overload]
            "result": row["result"],
            "roles": dict(sorted(roles.items())),
            "score": score,
            "winner_group": winner,
        })
    return rows


def consensus_sha(game_id: str, final_result: Mapping[str, object],
                  template_rows: Sequence[Mapping[str, object]]) -> str:
    """The reference's series adjudication digest -- the value the lecturer recomputes.

    Preimage ``{game_id, aggregate, sub_games}``, serialized with **spaced** separators:
    ``json.dumps(sort_keys=True, ensure_ascii=False)`` and no ``separators=`` argument.
    This is the one hash in the project that is *not* the compact canonical form used
    everywhere else, and the exception is load-bearing rather than an oversight.

    **Settled 2026-08-15 against the lecturer's own artifact, not against a restatement.**
    `yanell11` argued for this form; the claim rested on a scope dict transcribed by hand
    into their probe, so it was checked at the source instead --
    ``docs/sample-run/result_segal-police-team-vs-segal-thief-team.json``, fetched from
    ``rmisegal/Game-P2P-Cop-Chase@master``. That file ships
    ``mutual_agreement.sha256 = 31d678dadbd2...``, and recomputing from its own rows gives::

        spaced   31d678dadbd226dcb1ad87848386416702dcf0735746d7c812350ebc69cbdc81  == shipped
        compact  effb75c40fcdae1b299a3936bed0b34d13fc4cfd3ffcda5232fba5cb5bce29b7  no match

    The book mandates the field -- "mutual agreement confirmations using SHA-256"
    (`inst/police_thief_p2p_Summary.md:2220`) -- and specifies **no** construction for it,
    deferring to the ``[Result File]`` example it ships. The lecturer's artifact is that
    example, so following it contradicts nothing higher.

    **What this replaced, and why the old one is kept.** Until now this computed
    ``{game_id, game_uid, sub_games}`` compact (:func:`legacy_consensus_sha`). That form
    was agreed bilaterally with `uoh-ay26` and reproduced bit-for-bit by both peers, so
    `G008` and `G009` settled correctly *between the peers* -- but neither side matched
    the reference, which is precisely the failure mode a cross-team kit exists to catch.
    Two implementations agreeing with each other is not the same as either being right.
    """
    preimage = {"game_id": game_id,
                "aggregate": {key: final_result[key] for key in AGGREGATE_KEYS},
                "sub_games": consensus_rows(template_rows)}
    return hashlib.sha256(_spaced(preimage)).hexdigest()


def legacy_consensus_sha(game_id: str, game_uid: str,
                         template_rows: Sequence[Mapping[str, object]]) -> str:
    """The pre-2026-08-15 construction, retained so past series stay reproducible.

    `G008` and `G009` were reported under this digest and both opponents accepted it, so
    it has to remain computable to re-derive what those reports actually said. It is not
    used for any new series; see :func:`consensus_sha` for what replaced it and why.
    """
    preimage = {"game_id": game_id, "game_uid": game_uid,
                "sub_games": consensus_rows(template_rows)}
    return hashlib.sha256(_canonical(preimage)).hexdigest()


def consensus_envelope(sha: str, *, sender: str = "police") -> dict:
    """The reciprocal `submit_audit` envelope the opponent's exchange awaits."""
    return {"sender": sender, "records": [], "result_claim": "series_consensus",
            "consensus_sha": sha}
