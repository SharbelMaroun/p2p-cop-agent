"""Public SDK boundary for all future Cop business behavior."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from p2p_cop_agent.shared import __version__
from p2p_cop_agent.shared.contracts import load_shared_contract


@dataclass(frozen=True, slots=True)
class CopSDK:
    """Hold validated shared configuration without implementing game behavior."""

    game_config: Mapping[str, object]
    rate_limits_config: Mapping[str, object]
    role: str = field(default="cop", init=False)
    version: str = field(default=__version__, init=False)
    contract_version: str | None = None

    @classmethod
    def from_repository(cls, root: str | Path) -> "CopSDK":
        """Load the proposed shared bundle and always enforce its source-backed schemas."""
        contract = load_shared_contract(root)
        return cls(
            game_config=contract.game,
            rate_limits_config=contract.rate_limits,
            contract_version=contract.version,
        )
