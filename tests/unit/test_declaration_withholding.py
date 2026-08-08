"""`M9-27`: a classmate who withholds identity fields must not end an agreed match.

Split from `test_declaration.py` when it crossed the 150-line cap. Found live on 2026-08-09:
negotiation with group `amireman` succeeded, terms were agreed, and the match then died
building the declaration because their identity carried no `mcp_servers`.

The same module already refuses to invent an opponent's hardware or model -- null plus an
`undeclared` list, never a value -- and says of `group_name` that refusing to play over a
missing one "would assert more across the wire than any source supports". `repos` and
`mcp_servers` had never been given that treatment.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.protocol.declaration import DeclarationError
from tests.unit.test_declaration import _declaration


def test_an_opponent_withholding_its_repos_is_recorded_not_refused() -> None:
    """**Corrected 2026-08-09 by a live match.** Negotiation with a classmate succeeded and
    the match then died here because their identity carried no `mcp_servers`. Nothing lets
    us compel a peer's disclosure and rule 38 forbids supplying it for them, so the omission
    is named in `undeclared_identity` and the game proceeds. Rule 49's four links are then
    unmeetable, which `build_result` refuses at report time -- the right place to notice."""
    declaration = _declaration(opponent_identity={"group_id": "beta", "members": []})
    theirs = declaration["groups"][1]
    assert theirs["repos"] is None and theirs["mcp_servers"] is None
    assert set(theirs["undeclared_identity"]) == {"repos", "mcp_servers"}


def test_our_own_group_without_a_repo_link_is_refused() -> None:
    """Rule 49 is an obligation on what **we** declare, and we control ours."""
    with pytest.raises(DeclarationError, match="repo"):
        _declaration(our_identity={"group_id": "alpha", "members": [], "repos": {},
                                  "mcp_servers": {"cop": "https://a/mcp"},
                                  "group_name": "alpha"})
def test_a_group_without_a_group_id_is_refused() -> None:
    with pytest.raises(DeclarationError, match="group_id"):
        _declaration(opponent_identity={"members": [], "repos": {"a": "https://x/a"}})
