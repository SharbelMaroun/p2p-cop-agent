"""Public SDK boundary for all future Cop business behavior."""

from collections.abc import Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass, field
from pathlib import Path

from p2p_cop_agent.domain import Action, BarrierField, Board, Coordinate
from p2p_cop_agent.sdk.session import ProtocolSessionMixin
from p2p_cop_agent.shared import __version__
from p2p_cop_agent.shared.contracts import (
    SharedContract,
    load_match_contract,
    require_same_match_configuration,
)
from p2p_cop_agent.strategy import TurnIntent, choose_action, choose_turn_intent

_NO_BARRIERS: frozenset[Coordinate] = frozenset()


@dataclass(frozen=True, slots=True)
class CopSDK(ProtocolSessionMixin):
    """Hold a validated per-match configuration without implementing game behavior.

    Commit-reveal and Step-0 session helpers are provided by
    :class:`~p2p_cop_agent.sdk.session.ProtocolSessionMixin`.
    """

    game_config: Mapping[str, object]
    rate_limits_config: Mapping[str, object]
    config_sha256: str
    config_file_sha256: str
    role: str = field(default="cop", init=False)
    version: str = field(default=__version__, init=False)
    contract_version: str | None = None

    @classmethod
    def from_repository(
        cls,
        root: str | Path,
        match_config_path: str | Path,
        *,
        rate_limits_path: str | Path,
    ) -> "CopSDK":
        """Load the stable bundle and explicit per-run configuration files."""
        contract = load_match_contract(
            root,
            match_config_path,
            rate_limits_path=rate_limits_path,
        )
        return cls(
            game_config=contract.game,
            rate_limits_config=contract.rate_limits,
            config_sha256=contract.config_sha256,
            config_file_sha256=contract.config_file_sha256,
            contract_version=contract.version,
        )

    def validate_match_offer(
        self,
        root: str | Path,
        match_config_path: str | Path,
        *,
        rate_limits_path: str | Path,
    ) -> None:
        """Validate and compare a proposed per-match configuration and its hashes."""
        offered = load_match_contract(
            root,
            match_config_path,
            rate_limits_path=rate_limits_path,
        )
        expected = SharedContract(
            version=self.contract_version or "",
            game=dict(self.game_config),
            rate_limits=dict(self.rate_limits_config),
            config_sha256=self.config_sha256,
            config_file_sha256=self.config_file_sha256,
        )
        require_same_match_configuration(expected, offered)

    def board(self) -> Board:
        """Return the board geometry negotiated for this match."""
        return Board.from_config(self.game_config)

    def choose_pursuit_action(
        self,
        cop: Coordinate,
        target: Coordinate,
        blocked: AbstractSet[Coordinate] = _NO_BARRIERS,
    ) -> Action:
        """Return the deterministic pursuit action for this match's board.

        Delegates to the strategy layer so adapters never re-implement policy.
        ``target`` is the presumed Thief cell supplied by the caller; the SDK
        does not infer it.
        """
        return choose_action(self.board(), cop, target, blocked)

    def choose_turn_intent(
        self,
        cop: Coordinate,
        target: Coordinate,
        barriers: BarrierField,
    ) -> TurnIntent:
        """Return one deterministic move-or-barrier intent for this match.

        The target remains caller-supplied local belief; the SDK never reads or
        stores objective opponent truth.
        """
        return choose_turn_intent(self.board(), cop, target, barriers)
