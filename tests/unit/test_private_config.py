"""M5-03f: the opponent's address comes from private TOML, and only from there.

Two halves. The loader must read `[network].opponent_url` from an explicit private
path, and the shared match object must be provably free of any network address --
the second half is what keeps a private setting from leaking into a signed
agreement `[ADR-004]`.
"""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.shared.private_config import (
    PrivateConfigError,
    SharedConfigLeakError,
    assert_no_network_address,
    load_opponent_url,
    load_private_config,
    opponent_url,
)

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_TOML = ROOT / "config" / "game.toml.example"
MATCH_CONFIG = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"

PRIVATE = """
[network]
my_port = 8802
opponent_url = "http://127.0.0.1:8801/mcp"
turn_timeout_seconds = 180
"""


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "game.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_the_opponent_url_is_read_from_the_network_section(tmp_path: Path) -> None:
    assert load_opponent_url(write(tmp_path, PRIVATE)) == "http://127.0.0.1:8801/mcp"


def test_the_shipped_example_parses_and_names_an_opponent(tmp_path: Path) -> None:
    """The committed example must stay loadable, or it teaches the wrong shape."""
    config = load_private_config(EXAMPLE_TOML)
    assert opponent_url(config).startswith("https://")
    assert set(config["network"]) >= {"my_port", "opponent_url", "turn_timeout_seconds"}


def test_a_missing_file_is_a_private_config_error(tmp_path: Path) -> None:
    with pytest.raises(PrivateConfigError, match="cannot read"):
        load_opponent_url(tmp_path / "absent.toml")


def test_malformed_toml_is_a_private_config_error(tmp_path: Path) -> None:
    with pytest.raises(PrivateConfigError, match="not valid TOML"):
        load_opponent_url(write(tmp_path, "[network\nopponent_url = "))


def test_a_missing_network_section_is_refused() -> None:
    with pytest.raises(PrivateConfigError, match=r"no \[network\] section"):
        opponent_url({"game": {"group_id": "alpha"}})


@pytest.mark.parametrize("value", ["", "   ", 8801, None, ["http://x/mcp"]])
def test_a_non_string_or_empty_url_is_refused(value: object) -> None:
    with pytest.raises(PrivateConfigError, match="non-empty string"):
        opponent_url({"network": {"opponent_url": value}})


@pytest.mark.parametrize("value", ["127.0.0.1:8801", "ftp://host/mcp", "file:///etc/passwd"])
def test_a_non_http_url_is_refused(value: str) -> None:
    """A scheme we cannot dial is a configuration error, not a runtime surprise."""
    with pytest.raises(PrivateConfigError, match="must be http"):
        opponent_url({"network": {"opponent_url": value}})


# --- the other half: nothing addressable may ride in the shared object ---------


def test_the_real_shared_match_object_carries_no_network_address() -> None:
    """The controlled fixture is the one both peers sign; it must be clean."""
    assert_no_network_address(json.loads(MATCH_CONFIG.read_text(encoding="utf-8")))


def test_shared_timeouts_and_league_counts_are_not_addresses() -> None:
    """`network_and_league` is legitimate; only addresses are contraband."""
    assert_no_network_address(
        {"network_and_league": {"response_timeout_sec": 30, "num_games": 6}}
    )


@pytest.mark.parametrize(
    "shared",
    [
        {"network": {"opponent_url": "http://127.0.0.1:8801/mcp"}},
        {"board_and_agents": {"port": 8801}},
        {"identity": {"mcp_servers": ["http://a/mcp"]}},
        {"world": {"host": "127.0.0.1"}},
        {"nested": {"deep": {"bind_port": 0}}},
    ],
)
def test_an_address_named_member_in_shared_config_is_refused(shared: dict) -> None:
    with pytest.raises(SharedConfigLeakError, match="private network member"):
        assert_no_network_address(shared)


@pytest.mark.parametrize(
    "shared",
    [
        {"world": {"map_area": "https://example.invalid/mcp"}},
        {"extensions": {"notes": ["fine", "http://127.0.0.1:8801/mcp"]}},
        {"agreed_between": ["alpha", "http://beta.invalid/mcp"]},
    ],
)
def test_an_address_valued_member_in_shared_config_is_refused(shared: dict) -> None:
    """Renaming the key does not launder the value; both checks are needed."""
    with pytest.raises(SharedConfigLeakError, match="network address"):
        assert_no_network_address(shared)
