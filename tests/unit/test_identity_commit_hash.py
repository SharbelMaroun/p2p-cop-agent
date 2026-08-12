"""C-038: the negotiation identity carries `git_commit_hash` when resolvable.

Group `uoh-ay26`'s `mutual_sign_off` requires `identity.git_commit_hash` to match
`^[0-9a-f]{40}$` in the **negotiation identity** and quietly voids the mutual result
when it is absent -- which is what turned a cleanly audited survival into
`mutual_sign_off=false` on 2026-08-12. The book homes the hash in the sealed Step-0
declaration instead (rules 24/53, `inst/:1295`), and the reference's wire identity
carries no code version at all, so this is an outbound peer accommodation, not a
book member: attached when resolvable, omitted -- never fatal -- when not.
"""

import re

from p2p_cop_agent.shared.team_config import load_identity

CONFIG = {
    "game": {
        "group_id": "sharnamr",
        "group_name": "sharNamr",
        "members": ["Sharbel Maroun", "Amr safadi"],
        "repos": {"cop": "https://example.invalid/cop", "thief": "https://example.invalid/thief"},
    },
    "llm": {"model": "template"},
    "hardware": {"os": "Windows-11", "cpu": "x86_64", "cpu_freq_mhz": 3600, "ram_gb": 16,
                 "gpu": "none", "vram_gb": 0},
    "network": {"public_url": "https://example.invalid/mcp"},
}


def test_identity_carries_a_40_hex_commit_hash_from_a_git_checkout() -> None:
    """Running from this repository, the hash resolves and matches their regex."""
    identity = load_identity(CONFIG)
    assert re.fullmatch(r"[0-9a-f]{40}", identity["git_commit_hash"])


def test_the_mandated_members_are_untouched_by_the_addition() -> None:
    """The accommodation extends the identity; it must not reshape it."""
    identity = load_identity(CONFIG)
    for member in ("group_id", "members", "repos", "mcp_servers", "llm_model", "spec"):
        assert member in identity


def test_an_unresolvable_commit_omits_the_field_instead_of_failing(monkeypatch) -> None:
    """Best-effort on purpose: an optional duplicate must never refuse a match."""
    from p2p_cop_agent.protocol.attestation import AttestationError
    from p2p_cop_agent.shared import team_config

    def refuse() -> str:
        raise AttestationError("no git here")

    monkeypatch.setattr(team_config, "running_git_commit", refuse)
    identity = team_config.load_identity(CONFIG)
    assert "git_commit_hash" not in identity
    assert identity["group_id"] == "sharnamr"
