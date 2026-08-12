"""Launch a peer and play one match over the wire: the serve command (M5-07c).

Assembles ``play_match`` from private config and a live socket -- the one part of the
runtime that needs real hardware and a tunnel, so ``serve_match`` itself is **not**
exercised in CI (there is no second machine). Its pure helpers -- URL parsing, the
per-game token split, the deterministic game id -- are unit-tested; the network
assembly is the runbook (see ``M5-07c`` in docs/TODO.md).

The decision seam is now ``adapters/live_policy.live_decide`` -- the measured
belief-pursuit stack with barriers, claims, and the involuntary trail. The M5
placeholder (a legal ``STAY`` each turn) that previously lived here is deleted, not
kept as an option: a Cop that never moves can never capture, so every served match
was a guaranteed survival payout to the opponent (M6-19).
"""

from __future__ import annotations

import queue
import time
from datetime import UTC, datetime
from pathlib import Path

from p2p_cop_agent.adapters.fastmcp_client import FastMCPClient
from p2p_cop_agent.adapters.fastmcp_server import PeerInboxes, take_turn
from p2p_cop_agent.adapters.serving import peer_answers, serve_in_background
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.orchestration.live_policy import live_decide
from p2p_cop_agent.orchestration.match import MatchResult, play_match
from p2p_cop_agent.orchestration.turn_loop import Decide
from p2p_cop_agent.peer import InboundPeer
from p2p_cop_agent.protocol import attestation_wire
from p2p_cop_agent.sdk import CopSDK
from p2p_cop_agent.services import wire_log
from p2p_cop_agent.services.deadlines import RetryPolicy
from p2p_cop_agent.services.readiness import (
    split_host_port,  # noqa: F401 - re-exported; the runbook and tests import it here
    timeouts_from_private_config,
    wait_for_peer,
)
from p2p_cop_agent.shared.config import JsonObject
from p2p_cop_agent.shared.private_config import load_private_config, opponent_url
from p2p_cop_agent.shared.team_config import load_host_spec, load_identity


def per_game_token_budget(game: JsonObject) -> int:
    """Split the series token budget across the negotiated number of sub-games."""
    league = game["network_and_league"]
    num_games = int(league["num_games"])  # type: ignore[index,call-overload]
    if num_games <= 0:
        raise ValueError("num_games must be positive")
    return int(league["token_budget_per_series"]) // num_games  # type: ignore[index,call-overload]


def derive_game_id(config_sha256: str) -> str:
    """A game id both peers derive identically from the shared config lock."""
    return f"game-{config_sha256[:12]}"


def cop_start(game: JsonObject) -> Coordinate:
    """Return the negotiated Cop opening cell from the shared match object."""
    section = game["board_and_agents"]
    row, col = section["cop_start"]  # type: ignore[index,misc]
    return Coordinate(int(row), int(col))


_STRATEGY: dict = {}


def serve_decide(board: Board, start: Coordinate, game: JsonObject) -> Decide:
    """Return the live decision policy for one served match (M6-19).

    A thin, name-stable seam: the CLI and the runbook call ``serve_decide``, and the
    behaviour behind it is `adapters/live_policy.live_decide` -- belief-recursive
    pursuit, one legal move-or-barrier intent per turn, truthful barrier disclosure,
    capture claims on the believed cell, the involuntary 5×5 trail window, and the
    alternating truth/bluff hint, all deterministic. The sealed payload carries the
    real move and position, because the audit is what makes a claim provable.
    """
    return live_decide(
        board, start, game, claim_every_turn=bool(_STRATEGY.get("claim_every_turn")))


def _drain(box: queue.Queue) -> JsonObject | None:
    try:
        return box.get_nowait()
    except queue.Empty:  # an empty inbox is a normal state, not an error
        return None


def serve_match(
    *,
    root: str,
    match_config_path: str,
    rate_limits_path: str,
    private_config_path: str,
    artifacts_dir: Path | None = None,
    sub_game: int = 1,
) -> MatchResult:
    """Assemble a peer from config, wait for the opponent, and play one match.

    Runbook-only: it binds a real server (``0.0.0.0``) and dials a real socket, so it is
    not run in CI. A ``MatchResult`` with everything ``None`` means the opponent never
    came up within the connect budget.
    """
    config = load_private_config(private_config_path)
    _STRATEGY.update(config.get("strategy") or {})  # amireman profile flags
    sdk = CopSDK.from_repository(root, match_config_path, rate_limits_path=rate_limits_path)
    identity = load_identity(config)
    host_spec = load_host_spec(config)
    inboxes = PeerInboxes()
    peer = InboundPeer(sdk)
    # Arm the wire recorder BEFORE the mailbox opens (C-039): `fastmcp_server` has fed
    # `wire_log.received(...)` since M9, but nothing ever called `enable`, so the Cop
    # kept no inbound record at all. The Thief armed its mirror in `play_command.py`.
    if artifacts_dir is not None and wire_log.enable(Path(artifacts_dir) / "logs"):
        print(f"wire log: {wire_log.target()}")
    serve_in_background(inboxes, port=int(config["network"]["my_port"]))  # type: ignore[index]
    # `peer_answers`, not `port_answers`: a tunnelled peer's host is a CDN edge that
    # accepts TCP whether or not the opponent exists (found live, 2026-08-09).
    connect_timeout, retry_interval = timeouts_from_private_config(config)
    if not wait_for_peer(
        lambda: peer_answers(opponent_url(config)), clock=time.monotonic, sleep=time.sleep,
        timeout=connect_timeout, interval=retry_interval,
    ):
        return MatchResult(None, None, None, None)
    game_id = derive_game_id(sdk.config_sha256)
    sealed = sdk.seal_step_zero_attestation(
        host=host_spec, model=identity["llm_model"], group_id=identity["group_id"], game_id=game_id,
    )
    started_at = datetime.now(UTC).isoformat()
    result = play_match(
        # Bound every outbound call (`M9-27`). Left unset the client waits forever, and two
        # tries plus a backoff quietly outlive the deadline we signed -- see
        # `RetryPolicy.call_timeout_sec` for why the cap is the deadline over `attempts`.
        sdk=sdk, transport=FastMCPClient(
            opponent_url(config),
            timeout=RetryPolicy.from_match(dict(sdk.game_config)).call_timeout_sec,
        ),
        take_offer=lambda: _drain(inboxes.agreements),
        take_turn=lambda: take_turn(inboxes, peer),
        decide=serve_decide(sdk.board(), cop_start(dict(sdk.game_config)), dict(sdk.game_config)),
        identity=identity,
        step_zero=attestation_wire(sealed),
        game_id=game_id, game_uid=sdk.config_sha256[:32],
        started_at=started_at,
        max_tokens_per_game=per_game_token_budget(dict(sdk.game_config)),
        clock=time.monotonic, sleep=time.sleep,
        artifacts_dir=artifacts_dir, sub_game=sub_game,
    )
    # Rule 36: the mutual audit is a condition of agreement, and an agreement needs two
    # peers present. Exiting here is what cost the companion Thief a won game against
    # `uoh-ay26` on 2026-08-11 -- their `submit_audit` met a 502 and the opponent recorded a
    # technical loss, scoring the game 0/0 for both under rule 35. This side plays Police in
    # sub-games 2/4/6, so the same window is needed here. See `post_match`.
    if result.played:
        from p2p_cop_agent.adapters.fastmcp_server import drain  # noqa: PLC0415
        from p2p_cop_agent.adapters.post_match import (  # noqa: PLC0415
            audit_window_seconds,
            await_opponent_audit,
        )

        audited = await_opponent_audit(
            drain=lambda: drain(inboxes, peer), clock=time.monotonic, sleep=time.sleep,
            timeout=audit_window_seconds(config),
        )
        print(f"opponent audit {'received' if audited else 'did not arrive in the window'}")
    if artifacts_dir is not None and result.played and result.outcome.audit:
        from p2p_cop_agent.adapters.match_artifacts import write_match_log  # noqa: PLC0415

        opponent = result.agreement.opponent_identity or {}
        write_match_log(
            artifacts_dir, game_id=game_id, game_uid=sdk.config_sha256[:32],
            sub_game=sub_game, group_id=str(identity.get("group_id", "unknown")),
            opponent_group_id=str(opponent.get("group_id", "unknown")),
            config_sha256=sdk.config_sha256, outcome=result.outcome.outcome,
            steps=result.outcome.steps, started_at=started_at,
            audit=result.outcome.audit,
            # Rule 53 per game, per team (inst/:1295): ours from the running tree,
            # theirs from the negotiation identity (C-038's member, when sent).
            github_commit={
                str(side.get("group_id", "unknown")): str(side.get("git_commit_hash", "unknown"))
                for side in (identity, opponent)
            },
        )
    return result
