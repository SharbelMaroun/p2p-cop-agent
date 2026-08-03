"""Assemble this peer's pre-game identity from private config (M5-07c serve wiring).

The book puts team identity in the **private** ``game.toml``, never the shared match
JSON: the shared object is byte-hashed for ``config_sha256``, so any team-specific data
in it would make the two peers' hashes disagree and refuse the match (Appendix B). So
the identity the negotiation offer and the declaration need -- group, members, repo
links, MCP URL, LLM model, and hardware spec -- is read here from ``[game]``, ``[llm]``,
and ``[network]``.

**Hardware is part config, part runtime, and that split is on purpose.** ``os`` and
``cpu`` are auto-detected (``platform``), because they are reliable and cost nothing.
``ram_gb``/``gpu``/``vram_gb`` are read from an operator-declared ``[hardware]`` section
because they cannot be gathered truthfully and portably from the standard library --
and the book requires *signing true specs*, with forging forfeiting the computational
bonus, so a fabricated value would be worse than an honest declared one.
"""

from __future__ import annotations

import platform
from collections.abc import Mapping

from p2p_cop_agent.protocol import HostSpec, build_identity
from p2p_cop_agent.shared.config import JsonObject
from p2p_cop_agent.shared.private_config import PrivateConfigError, public_url


def load_identity(config: Mapping[str, object]) -> JsonObject:
    """Build the book-mandated pre-game identity from the private ``game.toml``."""
    game = _section(config, "game")
    llm = _section(config, "llm")
    group_id = _require_str(game, "group_id", "game")
    group_name = game.get("group_name")
    return build_identity(
        group_id=group_id,
        members=_require_names(game, "members"),
        repos=_require_table(game, "repos"),
        mcp_servers={group_id: public_url(config)},
        llm_model=_require_str(llm, "model", "llm"),
        spec=load_host_spec(config).as_dict(),
        group_name=group_name if isinstance(group_name, str) and group_name else None,
    )


def load_host_spec(config: Mapping[str, object]) -> HostSpec:
    """Read the host spec: os/cpu auto-detected, ram/gpu/vram operator-declared."""
    section = config.get("hardware")
    hardware = section if isinstance(section, Mapping) else {}
    return HostSpec(
        os=_text(hardware.get("os"), _detect_os),
        cpu=_text(hardware.get("cpu"), _detect_cpu),
        ram_gb=_require_number(hardware, "ram_gb"),
        gpu=_require_str(hardware, "gpu", "hardware"),
        vram_gb=_require_number(hardware, "vram_gb"),
    )


def _detect_os() -> str:
    return platform.platform() or platform.system() or "unknown-os"


def _detect_cpu() -> str:
    return platform.processor() or platform.machine() or "unknown-cpu"


def _text(value: object, detect) -> str:
    """Use an operator override when given a non-empty string, else auto-detect."""
    return value if isinstance(value, str) and value.strip() else detect()


def _section(config: Mapping[str, object], name: str) -> Mapping[str, object]:
    section = config.get(name)
    if not isinstance(section, Mapping):
        raise PrivateConfigError(f"private config needs a [{name}] section")
    return section


def _require_str(section: Mapping[str, object], key: str, where: str) -> str:
    value = section.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PrivateConfigError(f"[{where}].{key} must be a non-empty string")
    return value


def _require_names(section: Mapping[str, object], key: str) -> list[str]:
    value = section.get(key)
    if (not isinstance(value, list) or not value
            or not all(isinstance(name, str) and name.strip() for name in value)):
        raise PrivateConfigError(f"[game].{key} must be a non-empty list of member names")
    return list(value)


def _require_table(section: Mapping[str, object], key: str) -> dict[str, object]:
    value = section.get(key)
    if not isinstance(value, Mapping) or not value:
        raise PrivateConfigError(f"[game].{key} must be a non-empty table of repo URLs")
    return dict(value)


def _require_number(section: Mapping[str, object], key: str) -> float:
    value = section.get(key)
    if isinstance(value, bool) or not isinstance(value, int | float) or value <= 0:
        raise PrivateConfigError(f"[hardware].{key} must be a positive number (declare it truthfully)")
    return value
