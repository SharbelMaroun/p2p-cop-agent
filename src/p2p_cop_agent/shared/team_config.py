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

import contextlib
import platform
from collections.abc import Mapping

from p2p_cop_agent.protocol import HostSpec, build_identity
from p2p_cop_agent.protocol.attestation import AttestationError, running_git_commit
from p2p_cop_agent.shared.config import JsonObject
from p2p_cop_agent.shared.private_config import PrivateConfigError, public_url


def load_identity(config: Mapping[str, object]) -> JsonObject:
    """Build the book-mandated pre-game identity from the private ``game.toml``.

    ``git_commit_hash`` is attached when resolvable, as a **peer accommodation**, not
    a book member (`C-038`). The book homes the commit hash in the sealed Step-0
    declaration and the emailed `github_commit` (rules 24/53, `inst/:1295`), and the
    reference's wire identity carries no code version at all -- but group `uoh-ay26`'s
    `mutual_sign_off` reads `identity.git_commit_hash` and quietly voids the mutual
    result when it is absent, which would fail the reference itself. Identity is
    unsigned and role-free, so the extra member costs nothing. Best-effort on purpose:
    the mandated home for this value keeps its fail-closed resolver, while an optional
    duplicate must not refuse a match that Step-0 would attest correctly.
    """
    game = _section(config, "game")
    llm = _section(config, "llm")
    group_id = _require_str(game, "group_id", "game")
    group_name = game.get("group_name")
    identity = build_identity(
        group_id=group_id,
        members=_require_names(game, "members"),
        repos=_require_table(game, "repos"),
        mcp_servers={group_id: public_url(config)},
        llm_model=_require_str(llm, "model", "llm"),
        spec=load_host_spec(config).as_dict(),
        group_name=group_name if isinstance(group_name, str) and group_name else None,
    )
    # Optional duplicate; Step-0 remains the mandated, fail-closed home.
    with contextlib.suppress(AttestationError):
        identity["git_commit_hash"] = running_git_commit()
    return identity


def load_host_spec(config: Mapping[str, object]) -> HostSpec:
    """Read the host spec: what can be detected truthfully is, the rest is declared.

    The split follows what the standard library can actually answer. `os`, `cpu_type` and
    `cpu_cores` come from `platform`/`os` and cost nothing. Clock speed, RAM and the
    graphics card cannot be read portably, so they are operator-declared — and the book
    requires signing *true* specs, with forging forfeiting the computational bonus, so a
    fabricated number would be worse than an honest declared one.

    `cpu` and `gpu` are accepted as aliases for `cpu_type` and `gpu_model`: an existing
    private config carries the same facts under the old names, and renaming a field is no
    reason to refuse to start. `cpu_freq_mhz` has no alias because it is genuinely new —
    `inst/:1278` asks for cores **and their frequency**, and the old single `cpu` string
    could not carry it.
    """
    section = config.get("hardware")
    hardware = section if isinstance(section, Mapping) else {}
    return HostSpec(
        os=_text(hardware.get("os"), _detect_os),
        cpu_type=_text(hardware.get("cpu_type") or hardware.get("cpu"), _detect_cpu),
        cpu_freq_mhz=_require_number(hardware, "cpu_freq_mhz"),
        cpu_cores=int(_number(hardware.get("cpu_cores")) or os_cpu_count()),
        ram_gb=_require_number(hardware, "ram_gb"),
        gpu_model=_text(hardware.get("gpu_model") or hardware.get("gpu"), lambda: "")
                  or _require_str(hardware, "gpu_model", "hardware"),
        vram_gb=_require_number(hardware, "vram_gb", allow_zero=True),
    )


def os_cpu_count() -> int:
    """Cores this machine reports, never 0 — a spec claiming zero cores is not true."""
    import os as _os  # noqa: PLC0415

    return _os.cpu_count() or 1


def _number(value: object) -> float | None:
    """Return a usable number, or `None` so the caller can fall back to detection."""
    if isinstance(value, bool) or not isinstance(value, int | float) or value <= 0:
        return None
    return float(value)


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


def _require_number(section: Mapping[str, object], key: str, *, allow_zero: bool = False) -> float:
    """Require a declared number. `allow_zero` exists for `vram_gb` alone.

    "Presence of a graphics card" (`inst/:1278`) has a legitimate *no*, and refusing `0`
    would push an honest operator into inventing a number for a card they do not own.
    """
    value = section.get(key)
    numeric = not isinstance(value, bool) and isinstance(value, int | float)
    if not numeric or not (value >= 0 if allow_zero else value > 0):
        limit = "a number ≥ 0" if allow_zero else "a positive number"
        raise PrivateConfigError(
            f"[hardware].{key} must be {limit} (declare it truthfully; rule 24 forfeits "
            "the computational bonus for an incomplete or forged spec)")
    return value
