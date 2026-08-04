"""Shared Cop package utilities."""

from p2p_cop_agent.shared.contracts import ContractValidationError
from p2p_cop_agent.shared.private_config import (
    PrivateConfigError,
    SharedConfigLeakError,
    assert_no_network_address,
    load_opponent_url,
    load_private_config,
    opponent_url,
    public_url,
)
from p2p_cop_agent.shared.version import __version__

# NOTE: team_config is deliberately NOT imported here. It depends on p2p_cop_agent.
# protocol, which imports p2p_cop_agent.shared.config -- re-exporting it from this
# package __init__ forms an import cycle. Import it directly:
#     from p2p_cop_agent.shared.team_config import load_identity, load_host_spec

__all__ = [
    "ContractValidationError",
    "PrivateConfigError",
    "SharedConfigLeakError",
    "__version__",
    "assert_no_network_address",
    "load_opponent_url",
    "load_private_config",
    "opponent_url",
    "public_url",
]
