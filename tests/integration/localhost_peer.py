"""A standalone Cop peer process for the stage-2 localhost milestone (M5-10).

Run as a script, never imported by the runtime. It exists so a test can start a
**real second OS process** and prove a message crosses a socket between two
independent interpreters, which an in-memory loopback can never show.

Each accepted call is validated through the transport-neutral ``InboundPeer`` and
appended to a JSONL transcript, so the test has durable evidence of what the
second process actually received (M5-10f). Validation is inline here purely to
keep the demo self-contained; the production runtime keeps enqueue and drain
separate so it controls timing.

    python tests/integration/localhost_peer.py --port 8802 --transcript out.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from fastmcp import FastMCP  # noqa: E402

from p2p_cop_agent import CopSDK  # noqa: E402
from p2p_cop_agent.peer import InboundPeer  # noqa: E402
from p2p_cop_agent.protocol import (  # noqa: E402
    NegotiationError,
    ProtocolError,
    terms_from_config,
    verify_offer,
)

EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = ROOT / "config" / "rate_limits.json"


def build(peer: InboundPeer, transcript: Path, terms: dict) -> FastMCP:
    """Return a server that records every call's validation outcome."""
    mcp: FastMCP = FastMCP("p2p-cop-localhost")

    def write(entry: dict) -> dict:
        with transcript.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
        return {"ok": True}

    def record(tool: str, argument: dict) -> dict:
        try:
            peer.dispatch(tool, argument)
            entry = {"tool": tool, "accepted": True, "pid": os.getpid()}
        except ProtocolError as exc:
            entry = {"tool": tool, "accepted": False, "reason": str(exc)}
        return write(entry)

    @mcp.tool
    def negotiate(message: dict) -> dict:
        """Check the offer against *this* peer's own terms, not just its shape.

        The stage-2 negotiate round trip (M5-10b): a real second process decides
        whether it will play, and a mismatch is refused by name (`AE-11`).
        """
        try:
            peer.dispatch("negotiate", message)
            verify_offer(message, terms)
            entry = {"tool": "negotiate", "accepted": True, "pid": os.getpid()}
        except (ProtocolError, NegotiationError) as exc:
            entry = {"tool": "negotiate", "accepted": False, "reason": str(exc)}
        return write(entry)

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        return record("receive_turn", message)

    @mcp.tool
    def submit_audit(payload: dict) -> dict:
        return record("submit_audit", payload)

    @mcp.tool
    def receive_control(message: dict) -> dict:
        return record("receive_control", message)

    return mcp


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--transcript", type=Path, required=True)
    args = parser.parse_args()

    sdk = CopSDK.from_repository(ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    terms = terms_from_config(json.loads(EXAMPLE.read_text(encoding="utf-8")))
    server = build(InboundPeer(sdk), args.transcript, terms)
    server.run(transport="http", host="127.0.0.1", port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
