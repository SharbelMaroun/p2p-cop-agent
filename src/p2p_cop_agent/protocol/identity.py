"""The book-mandated pre-game identity content (M5-04h).

The book requires the pre-game exchange to carry team identity: the members, the
two repository URLs, the MCP server URL(s), the hardware spec, the LLM model, and a
signature. This module assembles that content from **injected** sources -- nothing
is hard-coded, so the real team values live in configuration, not here -- and checks
that *our own* offer is complete before it goes out.

Per the 2026-08-01 'populate ours, tolerate theirs' decision (`U-029`, `C-031`) this
is deliberately **one-directional**: we always send the full identity, but we do not
refuse a peer that omits it. Requiring it of the opponent would refuse a
simulator-built peer that keeps these values in emitted artifacts rather than on the
wire, and that is a contract change reserved for the coordinator. So the completeness
check here is only ever applied to what *we* send, never to what a peer sent us.

The URLs the identity carries (`repos`, `mcp_servers`) belong on the negotiation wire
precisely because the book mandates sharing them; that is a different object from the
shared, signed match config, which still forbids any network address `[AE-10]`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from p2p_cop_agent.shared.config import JsonObject

# The identity members the book mandates in the pre-game exchange. ``group_id`` names
# the team; the message's own ``signature`` field is the mandated signature and is
# checked where the offer is verified, not here.
MANDATORY_IDENTITY: tuple[str, ...] = (
    "group_id", "members", "repos", "mcp_servers", "llm_model", "spec",
)


class IdentityError(ValueError):
    """Raised when *our own* pre-game identity is missing a mandated member."""


def build_identity(
    *,
    group_id: str,
    members: Iterable[str],
    repos: Mapping[str, str],
    mcp_servers: Mapping[str, str],
    llm_model: str,
    spec: Mapping[str, object],
    group_name: str | None = None,
) -> JsonObject:
    """Assemble the mandated identity from injected sources (no hard-coded values)."""
    identity: JsonObject = {
        "group_id": group_id,
        "members": list(members),
        "repos": dict(repos),
        "mcp_servers": dict(mcp_servers),
        "llm_model": llm_model,
        "spec": dict(spec),
    }
    if group_name is not None:
        identity["group_name"] = group_name
    return identity


def require_complete_identity(identity: Mapping[str, object]) -> None:
    """Refuse to send *our* offer if it omits a mandated member.

    A present-but-empty member (an empty ``members`` list, a blank model) counts as
    missing: an empty field is not a shared value. Never applied to an opponent.
    """
    missing = [member for member in MANDATORY_IDENTITY if not identity.get(member)]
    if missing:
        raise IdentityError(
            f"our pre-game identity is missing mandated member(s): {', '.join(missing)}; "
            "the book requires members, repo URLs, MCP server URLs, hardware spec, and LLM model"
        )
