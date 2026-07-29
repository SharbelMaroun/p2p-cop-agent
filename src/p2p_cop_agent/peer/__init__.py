"""Transport-neutral peer boundary (M5-01); FastMCP adapters arrive in M5-02/03."""

from p2p_cop_agent.peer.inbound import TOOL_ARGUMENTS, InboundPeer
from p2p_cop_agent.peer.transport import PeerTransport

__all__ = ["TOOL_ARGUMENTS", "InboundPeer", "PeerTransport"]
