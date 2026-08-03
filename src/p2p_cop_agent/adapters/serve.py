"""Launch a peer and play one match over the wire: the serve command (M5-07c).

Assembles ``play_match`` from private config and a live socket -- the one part of the
runtime that needs real hardware and a tunnel, so ``serve_match`` itself is **not**
exercised in CI (there is no second machine). Its pure helpers -- URL parsing, the
per-game token split, the deterministic game id, and the M5 placeholder decision --
are unit-tested; the network assembly is the runbook (see ``M5-07c`` in docs/TODO.md).

The decision is a documented **M5 placeholder** (a legal ``STAY`` each turn);
belief-driven pursuit is M6, and this is the one seam it replaces.
"""

from __future__ import annotations

import queue
import time
from datetime import UTC, datetime
from urllib.parse import urlparse

from p2p_cop_agent.adapters.fastmcp_client import FastMCPClient
from p2p_cop_agent.adapters.fastmcp_server import PeerInboxes, take_turn
from p2p_cop_agent.adapters.serving import port_answers, serve_in_background
from p2p_cop_agent.orchestration.match import MatchResult, play_match
from p2p_cop_agent.orchestration.turn_loop import Decide
from p2p_cop_agent.peer import InboundPeer
from p2p_cop_agent.protocol import attestation_wire
from p2p_cop_agent.sdk import CopSDK
from p2p_cop_agent.services.readiness import timeouts_from_private_config, wait_for_peer
from p2p_cop_agent.shared.config import JsonObject
from p2p_cop_agent.shared.private_config import load_private_config, opponent_url
from p2p_cop_agent.shared.team_config import load_host_spec, load_identity

_DEFAULT_PORTS = {"https": 443, "http": 80}


def split_host_port(url: str) -> tuple[str, int]:
    """Return the (host, port) a readiness probe should connect to."""
    parsed = urlparse(url)
    if not parsed.hostname:
        raise ValueError(f"cannot read a host from {url!r}")
    return parsed.hostname, parsed.port or _DEFAULT_PORTS.get(parsed.scheme, 80)


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


def serve_decide() -> Decide:
    """The M5 placeholder policy: a legal STAY each turn. M6 replaces this seam."""
    count = 0

    def decide(_incoming: JsonObject | None) -> tuple[JsonObject, JsonObject]:
        nonlocal count
        count += 1
        return (
            {"move": "MOVE:STAY", "intent": "truth"},
            {"hint": "holding position", "smell_grid": {}, "timestamp": f"t{count}"},
        )

    return decide


def _drain(box: queue.Queue) -> JsonObject | None:
    try:
        return box.get_nowait()
    except queue.Empty:
        return None


def serve_match(
    *,
    root: str,
    match_config_path: str,
    rate_limits_path: str,
    private_config_path: str,
) -> MatchResult:
    """Assemble a peer from config, wait for the opponent, and play one match.

    Runbook-only: it binds a real server (``0.0.0.0``) and dials a real socket, so it is
    not run in CI. A ``MatchResult`` with everything ``None`` means the opponent never
    came up within the connect budget.
    """
    config = load_private_config(private_config_path)
    sdk = CopSDK.from_repository(root, match_config_path, rate_limits_path=rate_limits_path)
    identity = load_identity(config)
    host_spec = load_host_spec(config)
    inboxes = PeerInboxes()
    peer = InboundPeer(sdk)
    serve_in_background(inboxes, port=int(config["network"]["my_port"]))  # type: ignore[index]
    host, port = split_host_port(opponent_url(config))
    connect_timeout, retry_interval = timeouts_from_private_config(config)
    if not wait_for_peer(
        lambda: port_answers(host, port), clock=time.monotonic, sleep=time.sleep,
        timeout=connect_timeout, interval=retry_interval,
    ):
        return MatchResult(None, None, None, None)
    game_id = derive_game_id(sdk.config_sha256)
    sealed = sdk.seal_step_zero_attestation(
        host=host_spec, model=identity["llm_model"], group_id=identity["group_id"], game_id=game_id,
    )
    return play_match(
        sdk=sdk, transport=FastMCPClient(opponent_url(config)),
        take_offer=lambda: _drain(inboxes.agreements),
        take_turn=lambda: take_turn(inboxes, peer),
        decide=serve_decide(), identity=identity, step_zero=attestation_wire(sealed),
        game_id=game_id, game_uid=sdk.config_sha256[:32],
        started_at=datetime.now(UTC).isoformat(),
        max_tokens_per_game=per_game_token_budget(dict(sdk.game_config)),
        clock=time.monotonic, sleep=time.sleep,
    )
