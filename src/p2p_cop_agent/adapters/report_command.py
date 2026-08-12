"""`p2p-cop report`: build the template result from a series' logs, then send it.

Rule 32 mandates automatic reporting at the end of every legal game, and the result
covers all six sub-games — but each role repository plays only three, so the
aggregation is a **team-level** act: the series driver (outside both repositories)
invokes this command with both artifact directories after the final sub-game. Reading
the other repository's *artifact files* couples nothing; they are the same public JSON
the opponent audits.

Modes, from `[email]` in the private TOML (never the shared config):
`off` (default) — build and write the artifact, send nothing;
`dry_run`      — additionally compose the MIME and print what would be sent;
`real`         — send via the Gmail REST API using `[email].token_path`.
A `draft` mode is deliberately absent: creating drafts needs `gmail.compose`, and the
token is minted with `gmail.send` alone (rule 30's least privilege).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from p2p_cop_agent.reporting.gmail_message import build_report_message, encoded_message
from p2p_cop_agent.reporting.gmail_transport import http_status_of, make_transmit
from p2p_cop_agent.reporting.result_template import build_final_result, sub_game_row
from p2p_cop_agent.reporting.send_report import ReportSender
from p2p_cop_agent.reporting.series_consensus import (
    consensus_envelope,
    consensus_sha,
    derive_game_uid,
)
from p2p_cop_agent.shared.private_config import load_private_config

REPOSITORY_LINKS_KEY = "repos"


class ReportCommandError(RuntimeError):
    """Raised when the series' artifacts cannot produce a sendable report."""


def gather_summaries(directories: list[Path]) -> list[dict]:
    """Load every `log_*.json` summary (plus identity keys) across the directories."""
    summaries: list[dict] = []
    for directory in directories:
        for log_path in sorted(Path(directory).glob("log_*.json")):
            data = json.loads(log_path.read_text(encoding="utf-8"))
            summary = dict(data["summary"])
            summary["game_id"] = data["game_id"]
            summary["game_uid"] = data["game_uid"]
            agreement = data.get("mutual_agreement") or {}
            summary["config_sha256"] = agreement.get("sha256", "")
            summary["confirmed"] = agreement.get("confirmed") is True
            summaries.append(summary)
    if not summaries:
        raise ReportCommandError(f"no log_*.json under {[str(d) for d in directories]}")
    return summaries


def run_report(
    *,
    artifact_dirs: list[Path],
    private_config_path: Path,
    match_config_path: Path | None = None,
    to_override: str | None = None,
    mode_override: str | None = None,
) -> Path:
    """Build `result_<game_id>.json` from the series' logs and dispatch per config."""
    config = load_private_config(private_config_path)
    game = config.get("game") or {}
    email = config.get("email") or {}
    mode = (mode_override or email.get("mode") or "off").lower()
    recipient = to_override or email.get("recipient")

    summaries = gather_summaries(artifact_dirs)
    game_id, game_uid = summaries[0]["game_id"], summaries[0]["game_uid"]
    our_id = str(game.get("group_id"))
    their_id = next(s["opponent_group_id"] for s in summaries)
    groups = [our_id, str(their_id)]
    repos = dict(game.get(REPOSITORY_LINKS_KEY) or {})
    opponent_repos = dict((config.get("opponent") or {}).get(REPOSITORY_LINKS_KEY) or {})
    links = [*repos.values(), *opponent_repos.values()]

    result = build_final_result(
        game_id=game_id, game_uid=game_uid, groups=groups,
        rows=[sub_game_row(s, groups) for s in summaries],
        repositories=links,
        config_sha256=str(summaries[0].get("config_sha256", "")),
        league=(config.get("league") or None),
    )
    # Rule 36 puts the mutual audit before agreement, and rule 35 scores a
    # conflicting report 0/0 -- so agreement is EARNED from the logs, not
    # asserted: every sub-game must have recorded a received, confirmed audit.
    agreed = all(s.get("confirmed") for s in summaries)
    _attach_consensus(result, config=config, groups=groups,
                      match_config_path=match_config_path, agreed=agreed)
    out = Path(artifact_dirs[0]) / f"result_{game_id}.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"result artifact: {out} | {result['final_result']['total_score']}")

    if mode == "off":
        print("email mode off: nothing composed, nothing sent")
        return out
    if not recipient:
        raise ReportCommandError("[email].recipient is required for dry_run/real modes")
    if not agreed:
        unconfirmed = [s["sub_game_number"] for s in summaries if not s.get("confirmed")]
        raise ReportCommandError(
            f"sub-games {unconfirmed} never recorded a confirmed opponent audit; "
            "rule 35 scores a conflicting report 0/0, so nothing is composed")
    message = build_report_message(
        team_code=str(game.get("group_id")), game_id=game_id, result=result,
        settlement={"state": "agreed", "audit_passed": True},
        sender=str(email.get("sender") or recipient), to=str(recipient),
    )
    if mode == "dry_run":
        print(f"DRY RUN: would send {message['Subject']!r} to {recipient}; nothing sent")
        return out
    if mode != "real":
        raise ReportCommandError(f"unknown [email].mode {mode!r} (off|dry_run|real)")
    token_path = Path(str(email.get("token_path") or "")).expanduser()
    sender = ReportSender(credential_path=token_path)
    outcome = sender.send(
        game_id=game_id,
        transmit=make_transmit(token_path, encoded_message(message)),
        sleep=time.sleep, status_of=http_status_of,
    )
    print(f"SENT to {recipient}: attempts={outcome.attempts} response={outcome.response}")
    return out


def _attach_consensus(
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
    sha = consensus_sha(series_id, uid, result["sub_games"])
    result["series_consensus"] = {"game_id": series_id, "game_uid": uid,
                                  "consensus_sha": sha}
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
