"""Project one peer's negotiated identity into a declaration group entry (`M7-22f`).

Split out of `declaration.py` when the per-group hardware disclosure pushed that module past
the file-length limit. The seam is a real one rather than a convenience: `build_declaration`
assembles a document about the *series*, while everything here answers "what do we record
about one participant, and how much of it may we assert?" — a question with a different rule
behind every answer.

`ours` runs through all of it. The obligation is about what **we** declare: rule 24 is
Mandatory for our own hardware and model, and rule 39 keeps a credential out of any URL we
publish, but we cannot make a classmate send a display name or a spec, and refusing to play
over a missing one would assert more across the wire than any source supports (`C-031`,
"populate ours, tolerate theirs").
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from p2p_cop_agent.protocol.attestation import HARDWARE_MEMBERS
from p2p_cop_agent.shared.config import JsonObject

# `:2229` requires "addresses of the MCP server" in the declaration. Rule 39 (Prohibited)
# forbids pushing secrets, so a URL carrying a credential must never reach a committed,
# emailed artifact -- the two requirements meet here and only public URLs survive.
_CREDENTIAL_IN_URL = re.compile(
    r"://[^/@\s]+@"                                       # user:pass@host -- the @ is
    #   required, or a plain host:port like 127.0.0.1:8000 is refused as a credential
    r"|[?&][^=&]*(token|key|secret|password|passwd|auth)[^=&]*=",  # credential in a query
    re.I,
)


class DeclarationError(ValueError):
    """Raised when a pre-game declaration lacks a member it must carry before play."""


def _group(identity: Mapping[str, object], *, ours: bool = True) -> JsonObject:
    """Project one peer's identity into the declaration's group entry.

    `ours` decides how strict `group_name` is (`M7-28`). The obligation is about what
    **we** declare; we cannot make a classmate send a display name, and refusing to play
    over a missing one would assert more across the wire than any source supports.
    """
    group_id = identity.get("group_id")
    if not isinstance(group_id, str) or not group_id:
        raise DeclarationError("each group needs a non-empty group_id")
    repos = identity.get("repos")
    servers = identity.get("mcp_servers")
    has_repos = isinstance(repos, Mapping) and bool(repos)
    has_servers = isinstance(servers, Mapping) and bool(servers)
    if ours:
        # Rule 24 and `:2229` are obligations on **our** declaration, and we control ours.
        if not has_repos:
            raise DeclarationError(f"group {group_id!r} must carry at least one repo link")
        if not has_servers:
            raise DeclarationError(
                f"group {group_id!r} must declare its MCP addresses [`:2229`]")
    elif not has_servers or not has_repos:
        # **Their omission is theirs (corrected 2026-08-09, found in a live match).** This
        # module already refuses to invent an opponent's hardware or model, and says of
        # `group_name` that refusing to play over a missing one "would assert more across
        # the wire than any source supports". `repos` and `mcp_servers` were never given
        # that treatment, so a classmate who simply does not send them ended the match --
        # after terms had been agreed -- with a rule-24 error naming *their* group.
        # Nothing in the book lets us compel a peer's disclosure, and rule 38 forbids
        # supplying it for them, so it is recorded as withheld and the match proceeds.
        servers = servers if has_servers else None
        repos = repos if has_repos else None
    for role, url in (servers or {}).items():
        if not isinstance(url, str) or not url:
            raise DeclarationError(f"group {group_id!r} MCP address {role!r} must be a URL")
        if _CREDENTIAL_IN_URL.search(url):
            raise DeclarationError(
                f"group {group_id!r} MCP address {role!r} carries a credential; the "
                "declaration is committed and emailed, and rule 39 forbids that"
            )
    name = identity.get("group_name")
    if not isinstance(name, str) or not name:
        if ours:  # `inst/:1278`, p.39/104; rule 24 is Mandatory [AE-24]
            raise DeclarationError("our identity must declare group_name [AE-24]")
        name = group_id  # theirs: name it after the id, visibly, rather than refuse
    block: JsonObject = {
        "group_id": group_id,
        "group_name": name,
        "members": list(identity.get("members") or []),
        "repos": dict(repos) if repos else None,
        "mcp_servers": dict(servers) if servers else None,
    }
    absent = [n for n, got in (("repos", repos), ("mcp_servers", servers)) if not got]
    if absent:
        # Same posture as `_disclosure`: name what they withheld so the omission is
        # legible and lands where it belongs, rather than inventing a value (rule 38).
        block["undeclared_identity"] = absent
    block.update(_disclosure(identity, ours=ours, group_id=group_id))
    # Ours commits to what we declared; theirs is `None`, because nothing a peer sends
    # covers its own identity -- their negotiation signature is over the terms and the
    # challenge nonce, not the identity block, so presenting it here would claim an
    # authentication that does not exist. Added last, over the finished block, and
    # `lock_declaration` sorts keys so insertion order cannot change the digest.
    block["signature"] = _sign(block) if ours else None
    return block


def _disclosure(identity: Mapping[str, object], *, ours: bool, group_id: str) -> JsonObject:
    """The hardware and model each group declares (`M7-22f`, rule 24).

    These lived at the **top level** until 2026-08-07, describing only our own machine.
    That is not a formatting difference. `inst/:1276` asks whether it is fair for an agent
    on a phone to race one on a workstation, and says computational fairness "will be
    graded"; rule 24's sanction is denial of eligibility for the **computational bonus**.
    A bonus that compares two machines cannot be computed from one machine's spec, so the
    single top-level copy made the artifact unable to do the job it exists for.

    **An undeclared opponent gets `null`, never a value.** The reference implementation
    resolves this as `opp = series.peer_identity or own` -- an empty peer identity is
    falsy, so it **copies our own hardware and model into the opponent's slot**, which is
    visible in its sample artifacts as two groups sharing one machine. We do not: this
    document is signed and emailed, rule 38 makes a false declaration an absolute
    disqualification, and stating that an opponent ran on hardware we invented for them is
    exactly that. `undeclared` names what they withheld, so the omission is *theirs*,
    legible, and lands the sanction where it belongs.
    """
    llm_model, spec = identity.get("llm_model"), identity.get("spec")
    named = isinstance(llm_model, str) and bool(llm_model)
    specced = isinstance(spec, Mapping) and bool(spec)
    if ours:
        if not named or not specced:
            raise DeclarationError(
                "our group must declare llm_model and its hardware spec; rule 24 is "
                "Mandatory and its sanction is denial of the computational bonus [AE-24]")
        missing = [key for key in HARDWARE_MEMBERS if key not in spec]
        if missing:
            raise DeclarationError(
                f"our hardware spec omits {missing}; `inst/:1278` names the operating "
                "system, processor cores and their frequency, RAM, and GPU/VRAM [AE-24]")
        return {"llm_model": llm_model, "hardware_spec": dict(spec)}
    withheld = [n for n, got in (("llm_model", named), ("hardware_spec", specced)) if not got]
    disclosure: JsonObject = {
        "llm_model": llm_model if named else None,
        "hardware_spec": dict(spec) if specced else None,
    }
    if withheld:
        disclosure["undeclared"] = withheld
        disclosure["_note"] = (
            f"group {group_id} did not disclose {', '.join(withheld)} in the pre-game "
            "exchange. Recorded as absent rather than filled in: rule 24 is theirs to "
            "answer for [AE-24]")
    return disclosure


def _sign(block: JsonObject) -> str:
    """Commit to this group's declared block, reusing the document's own lock primitive."""
    from p2p_cop_agent.protocol.declaration import lock_declaration  # noqa: PLC0415

    return lock_declaration(block)
