"""The post-series consensus exchange, agreed with `uoh-ay26` (`C-044`).

After game 6 each team emits one `series_consensus` audit envelope: empty records and
a `consensus_sha` -- SHA-256 over the canonical `{game_id, game_uid, sub_games}`
preimage, where each row carries only cross-peer facts (number, result, roles with
`cop` normalised to `police`, sorted per-team scores, winner). Local timestamps,
tokens and filenames are deliberately excluded so both sides can agree without
byte-identical local observations.

Identifier convention (their 2026-08-12 message, adopted): `game_id` is the mutually
agreed `G00N` string, and `game_uid` is `derive_game_uid(terms, group_ids)` -- a UUID
formed from the first 16 bytes of SHA-256 over `canonical(terms) + "|" + the sorted
group ids joined by "|"`. Reproduced against their verification series bit-for-bit:
`fd362f67…` from our own six logs under `("G003", 7b1d942e-…)`.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Mapping, Sequence

WIRE_ROLE = {"cop": "police", "police": "police", "thief": "thief"}


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


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


def consensus_sha(game_id: str, game_uid: str,
                  template_rows: Sequence[Mapping[str, object]]) -> str:
    """The canonical series adjudication digest both teams must reproduce."""
    preimage = {"game_id": game_id, "game_uid": game_uid,
                "sub_games": consensus_rows(template_rows)}
    return hashlib.sha256(_canonical(preimage)).hexdigest()


def consensus_envelope(sha: str, *, sender: str = "police") -> dict:
    """The reciprocal `submit_audit` envelope the opponent's exchange awaits."""
    return {"sender": sender, "records": [], "result_claim": "series_consensus",
            "consensus_sha": sha}
