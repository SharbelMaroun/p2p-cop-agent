"""Transport adapters (M5-02+).

Importing from this package pulls in transport dependencies (``fastmcp``). The
transport-neutral core (``p2p_cop_agent.peer`` / ``.sdk``) never imports it.
"""

from p2p_cop_agent.adapters.fastmcp_server import (
    Delivery,
    PeerInboxes,
    build_server,
    drain,
)

__all__ = ["Delivery", "PeerInboxes", "build_server", "drain"]
