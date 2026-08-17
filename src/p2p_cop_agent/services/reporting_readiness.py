"""Can this machine file the report, and should it be able to?

Split from `preflight.py` under the file-length gate, at a seam that is really two questions
about one setting -- which credential the SEND reads, and whether an absent one is a refusal
or merely information.

Both halves were wrong until 2026-08-17. It inspected `[reporting].credential_path`, a
separate and unused placeholder, so every preflight printed `reporting DISABLED (no credential
at C:/path/outside/this/repo/...)` while the sender worked perfectly from `[email].token_path`
and five series filed successfully. And its verdict was inverted for a counted game: an absent
credential was reported as information, when rule 32 says "absence of reporting disqualifies
the game points" -- so a counted series that plays six sub-games and then cannot file is the
one failure that must surface at kickoff.

`yanell11`'s driver refuses to start a counted series on a machine that could not report;
ours only announced it. Theirs made "armed" a precondition where ours left it a claim.
Adopted from them, with thanks.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING

from p2p_cop_agent.services.credential_location import credential_path

if TYPE_CHECKING:  # pragma: no cover - the import is a cycle at runtime, a type here
    from p2p_cop_agent.services.preflight import Check

ARMED = "ARMED"
DISABLED = "DISABLED"


def send_token_path(config: object) -> Path | None:
    """The token the SEND actually reads: `[email].token_path`.

    This check inspected `[reporting].credential_path` until 2026-08-17 -- a separate,
    unused placeholder. So every preflight of 2026-08-16/17 printed
    `reporting DISABLED (no credential at C:/path/outside/this/repo/...)` while the sender
    was working perfectly from `[email].token_path` and five series filed successfully. A
    check that reads a different setting than the code it is checking is not a check.
    """
    email = config.get("email") if isinstance(config, dict) else None
    raw = email.get("token_path") if isinstance(email, Mapping) else None
    if isinstance(raw, str) and raw.strip():
        return Path(raw.strip()).expanduser()
    return None


def reporting_check(config: object) -> Check:
    """**The question this command was built to answer**, and it depends on `[league]`.

    A COUNTED series that plays six sub-games and then cannot file is exactly the failure
    rule 32 does not credit -- "absence of reporting disqualifies the game points" -- so an
    absent credential must refuse at kickoff rather than surface after the game. `yanell11`'s
    driver enforces this and ours only announced it; theirs made "armed" a precondition
    where ours left it a claim. Adopted from them on 2026-08-17.

    For an uncounted friendly the verdict inverts: an armed sender is the surprising state,
    because a rehearsal that files with the league is a rule-35 conflict scoring 0/0 for
    both teams.
    """
    from p2p_cop_agent.services.preflight import Check  # noqa: PLC0415

    league = config.get("league") if isinstance(config, dict) else None
    counted = bool(league.get("counted")) if isinstance(league, Mapping) else False
    path = send_token_path(config)
    if path is None:
        try:
            path = credential_path(config)  # type: ignore[arg-type]
        except Exception as exc:  # noqa: BLE001 - any refusal means no usable credential
            label = f"{DISABLED} ({exc})"
            return Check("reporting", f"COUNTED SERIES CANNOT FILE -- {label}",
                         ok=False) if counted else Check("reporting", label, ok=None)
    if not path.exists():
        label = f"{DISABLED} (no credential at {path})"
        if counted:
            return Check("reporting", f"COUNTED SERIES CANNOT FILE -- {label} [AE-32]",
                         ok=False)
        return Check("reporting", label, ok=None)
    if counted:
        return Check("reporting", f"{ARMED} for a COUNTED series (credential at {path})")
    return Check("reporting", f"{ARMED} (credential present at {path})", ok=False)
