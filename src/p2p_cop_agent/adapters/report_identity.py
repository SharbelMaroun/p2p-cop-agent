"""Agreed series identity and the consensus exchange, for the report (`C-044`/`C-045`).

Split from `report_command.py` at a real seam: composing/sending the email is one job;
speaking the mutually agreed series identity -- the `G00N` id, the derived uid, the
consensus digest, and the reciprocal envelope -- is the cross-team protocol half.
"""

from __future__ import annotations

import json
from pathlib import Path

from p2p_cop_agent.reporting.series_consensus import (
    consensus_envelope,
    consensus_sha,
    derive_game_uid,
)


def attach_consensus(
    result: dict,
    *,
    config: dict,
    groups: list[str],
    match_config_path: Path | None,
    agreed: bool,
) -> None:
    """Compute the agreed-identifier consensus and emit the reciprocal envelope (C-044).

    Skipped, loudly, when the operator has not agreed a `G00N` series id or the shared
    match file is not supplied -- a consensus over identifiers only one side uses can
    never match, which is exactly what the verification series proved.
    """
    from p2p_cop_agent.protocol.negotiation import terms_from_config  # noqa: PLC0415

    series_id = str((config.get("game") or {}).get("series_game_id") or "")
    if not series_id or match_config_path is None:
        print("consensus: skipped (agree [game].series_game_id and pass --match)")
        return
    terms = terms_from_config(json.loads(Path(match_config_path).read_text("utf-8")))
    uid = derive_game_uid(terms, groups)
    # `final_result` supplies the aggregate half of the reference preimage; `uid` is no
    # longer hashed (the reference scope has no `game_uid`) but stays in the published
    # `series_consensus` block, where the opponent's exchange reads it as the series
    # identity. Hashing it was our own addition and is what `legacy_consensus_sha` keeps.
    sha = consensus_sha(series_id, result["final_result"], result["sub_games"])
    result["series_consensus"] = {"game_id": series_id, "game_uid": uid,
                                  "consensus_sha": sha}
    # Their convention (2026-08-13 review): the aggregate's mutual_agreement.sha256
    # IS the shared consensus digest -- the one value both teams provably computed
    # from the same six rows -- not the pre-game config lock, which lives in the
    # per-game artifacts. :2220's "mutual agreement confirmations using SHA-256"
    # is better satisfied by the digest the agreement is actually about.
    result["mutual_agreement"] = {"sha256": sha, "confirmed": bool(agreed)}
    print(f"consensus: {series_id} {uid} sha={sha}")
    if not agreed:
        print("consensus: NOT emitted (unconfirmed sub-games)")
        return
    opponent = str((config.get("network") or {}).get("opponent_url") or "")
    if not opponent:
        print("consensus: NOT emitted (no [network].opponent_url)")
        return
    from p2p_cop_agent.adapters.fastmcp_client import FastMCPClient  # noqa: PLC0415

    try:
        response = FastMCPClient(opponent, timeout=30).submit_audit(
            consensus_envelope(sha))
        print(f"consensus: emitted to opponent -> {response}")
    except Exception as exc:  # noqa: BLE001 - the report already succeeded locally
        print(f"consensus: opponent unreachable ({exc}); sha stands in the artifact")


def agreed_identifiers(
    config: dict, groups: list[str], match_config_path: Path | None,
) -> tuple[str, str] | None:
    """Return the mutually agreed (game_id, game_uid), or None when unagreed."""
    from p2p_cop_agent.protocol.negotiation import terms_from_config  # noqa: PLC0415

    series_id = str((config.get("game") or {}).get("series_game_id") or "")
    if not series_id or match_config_path is None:
        return None
    terms = terms_from_config(json.loads(Path(match_config_path).read_text("utf-8")))
    return series_id, derive_game_uid(terms, groups)
