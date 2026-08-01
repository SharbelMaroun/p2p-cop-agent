"""M5-07a/M5-07b: the provider-neutral public tunnel boundary.

Two guarantees. Our *own* public address -- the tunnel URL we advertise so a peer
can reach us -- is read only from private config (`[network].public_url`), never
from the shared signed object; and the provider that produces it (ngrok, cloudflare,
a self-hosted domain) is a purely local choice, so only the resulting https URL is
ever exchanged and the token that authorises the tunnel stays private `[AE-10]`
`[G§7.4]`. This is the source of the `mcp_servers` value the negotiation identity
carries (M5-04h); the shared-config-leak half is proven in `test_private_config`.
"""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.protocol.identity import build_identity
from p2p_cop_agent.shared.private_config import (
    PrivateConfigError,
    SharedConfigLeakError,
    assert_no_network_address,
    public_url,
)

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_TOML = ROOT / "config" / "game.toml.example"


def test_our_public_url_is_read_from_the_network_section() -> None:
    config = {"network": {"public_url": "https://abc123.ngrok.app/mcp"}}
    assert public_url(config) == "https://abc123.ngrok.app/mcp"


@pytest.mark.parametrize("url", [
    "https://abc123.ngrok.app/mcp",
    "https://tunnel.trycloudflare.com/mcp",
    "https://mcp.my-own-domain.example/mcp",
])
def test_any_providers_public_url_reads_identically(url: str) -> None:
    """Provider-neutral: nothing in the code privileges a provider; each is a URL."""
    assert public_url({"network": {"public_url": url}}) == url


def test_a_missing_network_section_is_refused() -> None:
    with pytest.raises(PrivateConfigError, match=r"no \[network\] section"):
        public_url({"game": {"group_id": "sharNamr"}})


@pytest.mark.parametrize("value", ["", "   ", 8801, None])
def test_a_non_string_or_empty_public_url_is_refused(value: object) -> None:
    with pytest.raises(PrivateConfigError, match="non-empty string"):
        public_url({"network": {"public_url": value}})


@pytest.mark.parametrize("value", ["mcp.host:9000", "ws://host/mcp", "file:///x"])
def test_a_non_http_public_url_is_refused(value: str) -> None:
    with pytest.raises(PrivateConfigError, match="must be http"):
        public_url({"network": {"public_url": value}})


def test_the_shipped_example_advertises_a_public_url() -> None:
    """The committed example must teach the shape, so a new peer knows where its own
    advertised address goes."""
    import tomllib

    with EXAMPLE_TOML.open("rb") as handle:
        config = tomllib.load(handle)
    assert public_url(config).startswith("https://")


def test_only_the_url_is_exchanged_never_the_tunnel_secret() -> None:
    """M5-07a/b: the token authorising the tunnel lives beside the URL in private
    config, but only the URL reaches the identity a peer receives."""
    # A stand-in tunnel token; a real one lives only in an ignored .env.
    private = {"network": {
        "public_url": "https://abc123.ngrok.app/mcp",
        "tunnel_authtoken": "dummy-tunnel-token-value",
        "opponent_url": "https://opponent.invalid/mcp",
    }}
    identity = build_identity(
        group_id="sharNamr", members=["Amr safadi"],
        repos={"cop": "https://example.test/cop"},
        mcp_servers={"cop": public_url(private)},
        llm_model="cli-default", spec={"os": "Example OS"},
    )
    assert identity["mcp_servers"]["cop"] == "https://abc123.ngrok.app/mcp"
    assert "dummy-tunnel-token-value" not in json.dumps(identity)


def test_our_advertised_tunnel_url_cannot_ride_in_the_shared_object() -> None:
    """M5-07a: the signed match object stays free of our own tunnel address too."""
    with pytest.raises(SharedConfigLeakError):
        assert_no_network_address({"network_and_league": {"public_url": "https://t/mcp"}})
