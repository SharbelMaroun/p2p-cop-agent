"""Public SDK boundary for all future Cop business behavior."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from p2p_cop_agent.shared import __version__
from p2p_cop_agent.shared.contracts import (
    SharedContract,
    load_shared_contract,
    require_same_match_configuration,
)


@dataclass(frozen=True, slots=True)
class CopSDK:
    """Hold validated shared configuration without implementing game behavior."""

    game_config: Mapping[str, object]
    rate_limits_config: Mapping[str, object]
    config_sha256: str
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
            config_sha256=contract.config_sha256,
            contract_version=contract.version,
        )

    def validate_match_offer(self, root: str | Path) -> None:
        """Validate and compare a proposed shared match bundle and its hash."""
        offered = load_shared_contract(root)
        expected = SharedContract(
            version=self.contract_version or "",
            game=dict(self.game_config),
            rate_limits=dict(self.rate_limits_config),
            config_sha256=self.config_sha256,
        )
        require_same_match_configuration(expected, offered)
