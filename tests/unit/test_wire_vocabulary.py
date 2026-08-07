"""`M8-04b`: the wire vocabulary, which decides who is allowed to act.

Split from `test_inbound_validation.py`, which covers the field surface. The seam is real:
that file asks whether a message is *well formed*, this asks whether its `sender` names a
role that exists on the wire — a semantic question the schema's `type: string` cannot reach.

The wire vocabulary is `police`/`thief` (`OB-003`). `cop` is our **internal** name and is
not on the wire; the series rehearsal caught that distinction and this keeps it caught.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.protocol.messages import ProtocolError, require_wire_role

# --- the role field, which decides who may act -------------------------------------------


@pytest.mark.parametrize("bad", ["cop", "COP", "Police", "", None, 1, "thief ", "police\n"])
def test_a_role_outside_the_wire_vocabulary_is_refused(bad: object) -> None:
    """The wire vocabulary is `police`/`thief` (`OB-003`). `cop` is our *internal* name and
    is not on the wire — the series rehearsal caught that distinction, and this keeps it."""
    with pytest.raises(ProtocolError):
        require_wire_role(bad)


@pytest.mark.parametrize("good", ["police", "thief"])
def test_both_wire_roles_are_accepted(good: str) -> None:
    assert require_wire_role(good) == good
