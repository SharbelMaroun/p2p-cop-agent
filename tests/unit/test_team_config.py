"""M5-07c: the team identity comes from the private game.toml, not the shared JSON.

Settled from the book (Appendix B.4): identity lives in [game]/[llm], the MCP URL from
[network].public_url, and the hardware spec is part detected and part declared. These pin that loader and its
refusals.

Since `M7-22f` the spec carries the seven members `inst/:1278` names one by one. `os`,
`cpu_type` and `cpu_cores` are detected because the standard library answers them
truthfully; clock speed, RAM and the graphics card are declared because it cannot. `cpu`
and `gpu` still work as aliases — an existing private config holds the same facts under
the old names, and a rename is no reason to refuse to start.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.protocol import require_complete_identity
from p2p_cop_agent.shared.private_config import PrivateConfigError
from p2p_cop_agent.shared.team_config import load_host_spec, load_identity


def _config(**overrides: object) -> dict:
    config = {
        "game": {
            "group_id": "sharNamr", "group_name": "Sharbel-Amr",
            "members": ["Sharbel", "Amr"],
            "repos": {"cop": "https://example.com/cop", "thief": "https://example.com/thief"},
        },
        "llm": {"model": "template-zero-token"},
        "network": {"public_url": "https://self.ngrok.app/mcp"},
        "hardware": {"os": "Linux-6", "cpu": "x86_64", "cpu_freq_mhz": 3600, "ram_gb": 16,
                     "gpu": "none", "vram_gb": 1},
    }
    config.update(overrides)
    return config


def test_the_identity_carries_every_mandated_member() -> None:
    identity = load_identity(_config())
    require_complete_identity(identity)  # raises if any mandated member is missing
    assert identity["group_id"] == "sharNamr"
    assert identity["members"] == ["Sharbel", "Amr"]
    assert set(identity["repos"]) == {"cop", "thief"}
    assert identity["llm_model"] == "template-zero-token"


def test_the_mcp_url_comes_from_the_network_public_url() -> None:
    identity = load_identity(_config())
    assert identity["mcp_servers"] == {"sharNamr": "https://self.ngrok.app/mcp"}


def test_what_can_be_detected_truthfully_is_detected() -> None:
    spec = load_host_spec(_config(hardware={"cpu_freq_mhz": 2400, "ram_gb": 8,
                                            "gpu": "none", "vram_gb": 1}))
    facts = spec.as_dict()
    assert facts["os"] and facts["cpu_type"], "blank os/cpu_type fall back to detection"
    assert facts["cpu_cores"] >= 1, "cores come from os.cpu_count(), never 0"
    assert facts["ram_gb"] == 8


def test_a_declared_spec_overrides_auto_detection() -> None:
    spec = load_host_spec(_config()).as_dict()
    assert spec["os"] == "Linux-6" and spec["cpu_type"] == "x86_64"
    assert spec["gpu_model"] == "none"


def test_the_old_cpu_and_gpu_names_still_work() -> None:
    """A private config written before the rename holds the same facts. Refusing to start
    over a field name would cost a match for no gain in truthfulness."""
    spec = load_host_spec(_config(hardware={"cpu": "old-name", "gpu": "old-gpu",
                                            "cpu_freq_mhz": 3000, "ram_gb": 4,
                                            "vram_gb": 0})).as_dict()
    assert spec["cpu_type"] == "old-name" and spec["gpu_model"] == "old-gpu"


def test_a_machine_with_no_graphics_card_may_declare_zero_vram() -> None:
    """"Presence of a graphics card" (`inst/:1278`) has a legitimate no. Refusing 0 would
    push an honest operator into inventing a number for a card they do not own."""
    spec = load_host_spec(_config(hardware={"cpu_freq_mhz": 3000, "ram_gb": 4,
                                            "gpu": "none", "vram_gb": 0})).as_dict()
    assert spec["vram_gb"] == 0


def test_a_missing_clock_speed_is_refused_and_says_so() -> None:
    """The one genuinely new fact. `inst/:1278` asks for cores **and their frequency**, and
    the old single `cpu` string could not carry it, so there is nothing to alias."""
    with pytest.raises(PrivateConfigError, match="cpu_freq_mhz"):
        load_host_spec(_config(hardware={"ram_gb": 4, "gpu": "none", "vram_gb": 0}))


@pytest.mark.parametrize("overrides", [
    {"game": {"group_name": "x", "members": ["a"], "repos": {"cop": "u"}}},  # no group_id
    {"game": {"group_id": "g", "members": [], "repos": {"cop": "u"}}},        # empty members
    {"game": {"group_id": "g", "members": ["a"], "repos": {}}},               # no repos
])
def test_an_incomplete_game_section_is_refused(overrides: dict) -> None:
    with pytest.raises(PrivateConfigError):
        load_identity(_config(**overrides))


@pytest.mark.parametrize("hardware", [
    {"ram_gb": 8},                                        # gpu/vram absent
    {"ram_gb": 0, "gpu": "none", "vram_gb": 1},           # ram not positive
    {"ram_gb": 8, "gpu": "none", "vram_gb": -1},          # vram not positive
])
def test_missing_or_nonpositive_hardware_is_refused(hardware: dict) -> None:
    """Hardware cannot be fabricated: absent or nonsensical values are errors, not guesses."""
    with pytest.raises(PrivateConfigError, match="hardware"):
        load_host_spec(_config(hardware=hardware))


def test_a_missing_llm_section_is_refused() -> None:
    config = _config()
    del config["llm"]
    with pytest.raises(PrivateConfigError, match="llm"):
        load_identity(config)
