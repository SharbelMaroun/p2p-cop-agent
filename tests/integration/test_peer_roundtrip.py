"""M5-01: a message round-trips over an in-memory transport with zero FastMCP."""

from collections.abc import Mapping
from pathlib import Path

from p2p_cop_agent import CopSDK
from p2p_cop_agent.peer import InboundPeer, PeerTransport
from p2p_cop_agent.shared.config import JsonObject

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = ROOT / "config" / "rate_limits.json"
SRC = ROOT / "src" / "p2p_cop_agent"


class LoopbackTransport:
    """A PeerTransport that delivers straight to a local InboundPeer (test double)."""

    def __init__(self, remote: InboundPeer) -> None:
        self._remote = remote

    def negotiate(self, message: Mapping[str, object]) -> JsonObject:
        return self._remote.negotiate(message)

    def receive_turn(self, message: Mapping[str, object]) -> JsonObject:
        return self._remote.receive_turn(message)

    def submit_audit(self, payload: Mapping[str, object]) -> JsonObject:
        return self._remote.submit_audit(payload)

    def receive_control(self, message: Mapping[str, object]) -> JsonObject:
        return self._remote.receive_control(message)


def _sdk() -> CopSDK:
    return CopSDK.from_repository(ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)


def test_loopback_transport_satisfies_the_protocol_and_round_trips() -> None:
    remote = InboundPeer(_sdk())
    transport: PeerTransport = LoopbackTransport(remote)
    assert isinstance(transport, PeerTransport)  # structural match, runtime_checkable

    turn = {"step": 1, "sender": "thief", "hint": "east", "smell_grid": {"3,3": 0.9},
            "commit": "a" * 64, "timestamp": "t"}
    assert transport.receive_turn(turn) == {"ok": True}


def test_transport_neutral_core_imports_no_fastmcp() -> None:
    # The DoD is about imports, not prose: docstrings may name FastMCP, but no
    # transport-neutral module may actually import it.
    files = list((SRC / "peer").glob("*.py")) + list((SRC / "sdk").glob("*.py"))
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip().lower()
            assert not stripped.startswith(("import fastmcp", "from fastmcp"))
