"""`M7-28`: the declaration carries the group name, and whose name is enforced.

Split from `test_declaration.py`, which pins the builder and the lock. This covers one
requirement and the asymmetry it needed.

`inst/:1278` says the Step-0 declaration "documents the code version, **the group name**, and
the game number"; p.39/104 lists group identity as name, id and members. Rule 24 is Mandatory
and its sanction is denial of eligibility for computational bonuses.

**The obligation is about what we declare.** We control our own identity and cannot make a
classmate send a display name, so ours is enforced at build time and theirs falls back to
their `group_id` — visibly, in the artifact. Refusing to play over a missing display name
would assert more across the wire than any source supports, which is `X-04` in a different
costume.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.protocol.declaration import DeclarationError
from tests.unit.test_declaration import _declaration, _identity


def test_our_group_must_declare_its_name() -> None:
    """`M7-28`. `inst/:1278`: the Step-0 declaration "documents the code version, **the group
    name**, and the game number", and p.39/104 lists group identity as name, id and members.
    Rule 24 is Mandatory, sanction denial of the computational bonus."""
    with pytest.raises(DeclarationError, match="group_name"):
        _declaration(our_identity={k: v for k, v in _identity("alpha").items()
                                   if k != "group_name"})


def test_an_opponent_without_a_name_is_named_after_their_id_rather_than_refused() -> None:
    """**The asymmetry is the design.** The obligation is about what *we* declare, and we
    cannot make a classmate send a display name. Refusing to play over a missing one would
    assert more across the wire than any source supports — `X-04` in a different costume —
    so theirs falls back visibly instead."""
    theirs = {k: v for k, v in _identity("beta").items() if k != "group_name"}
    groups = _declaration(opponent_identity=theirs)["groups"]
    assert groups[1]["group_name"] == "beta"
