"""M5-04h: the book-mandated pre-game identity content, populated on our side.

The book requires the pre-game exchange to carry team identity: members, the two
repository URLs, the MCP server URL(s), the hardware spec, and the LLM model. Under
the 2026-08-01 'populate ours, tolerate theirs' decision (`U-029`), we always send
the full set but never refuse a peer that omits it -- so these tests cover the
assembler and the *outbound* self-check only. Tolerance of an incoming offer is
proven in `test_negotiation`.
"""

import pytest

from p2p_cop_agent.protocol.identity import (
    MANDATORY_IDENTITY,
    IdentityError,
    build_identity,
    require_complete_identity,
)

FULL = {
    "group_id": "sharNamr",
    "members": ["Amr safadi", "Sharbel Maroun"],
    "repos": {"cop": "https://example.test/cop", "thief": "https://example.test/thief"},
    "mcp_servers": {"cop": "https://cop.example.test/mcp"},
    "llm_model": "cli-default",
    "spec": {"os": "Example OS", "cpu": "Example CPU"},
}


def test_build_identity_assembles_every_mandated_member() -> None:
    identity = build_identity(
        group_id="sharNamr",
        group_name="sharNamr",
        members=["Amr safadi", "Sharbel Maroun"],
        repos=FULL["repos"],
        mcp_servers=FULL["mcp_servers"],
        llm_model="cli-default",
        spec=FULL["spec"],
    )
    assert all(identity.get(member) for member in MANDATORY_IDENTITY)
    assert identity["group_name"] == "sharNamr"


def test_build_identity_omits_group_name_when_not_supplied() -> None:
    identity = build_identity(
        group_id="sharNamr", members=["a"], repos={"cop": "x"},
        mcp_servers={"cop": "y"}, llm_model="m", spec={"os": "o"},
    )
    assert "group_name" not in identity


def test_require_complete_identity_accepts_a_full_identity() -> None:
    require_complete_identity(FULL)  # must not raise


@pytest.mark.parametrize("dropped", MANDATORY_IDENTITY)
def test_require_complete_identity_names_each_missing_member(dropped: str) -> None:
    partial = {k: v for k, v in FULL.items() if k != dropped}
    with pytest.raises(IdentityError, match=dropped):
        require_complete_identity(partial)


def test_an_empty_collection_counts_as_missing() -> None:
    """An empty members list is not 'members shared'; a present-but-empty field
    must fail the check as surely as an absent one."""
    with pytest.raises(IdentityError, match="members"):
        require_complete_identity({**FULL, "members": []})
