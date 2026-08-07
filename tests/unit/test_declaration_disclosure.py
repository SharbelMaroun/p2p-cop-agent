"""`M7-22f`: each group declares its own hardware and model, and we never invent theirs.

Rule 24 is Mandatory and its sanction is "denial of eligibility for computational bonuses".
That word decides the shape. `inst/:1276` asks whether it is fair for an agent on a mobile
device to race one on a machine that runs heavy models, says computational fairness "will be
graded", and puts Step-0 before the first move to answer it. A bonus that compares two
machines cannot be computed from one machine's spec — so a single top-level copy, which is
what this repository emitted until 2026-08-07, leaves the artifact unable to do its job.

**The half worth reading is what happens when the opponent declares nothing.** The reference
implementation resolves it as `opp = series.peer_identity or own`; an empty peer identity is
falsy in Python, so it copies *its own* hardware and model into the opponent's slot. Its
sample artifacts show two groups sharing one machine, which is how the behaviour hides — it
looks like a match played on one laptop, not like a defect.

We refuse to do that. This document is signed, committed and emailed; rule 38 makes a false
declaration an absolute disqualification; and stating that an opponent ran on hardware we
made up is a false declaration however plausible the number. Recording the absence instead
also lands rule 24's sanction on whoever actually failed to declare.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.protocol.declaration import DeclarationError, build_declaration, lock_declaration

SPEC = {"os": "Windows 11", "cpu_type": "x86_64", "cpu_freq_mhz": 3600, "cpu_cores": 8,
        "ram_gb": 32.0, "gpu_model": "RTX 3060", "vram_gb": 6.0}
THEIRS = {**SPEC, "os": "Ubuntu 24.04", "cpu_type": "Apple M1", "cpu_cores": 4,
          "gpu_model": "none", "vram_gb": 0}


def identity(group_id: str, **overrides: object) -> dict:
    base = {"group_id": group_id, "group_name": group_id.title(), "members": ["a", "b"],
            "repos": {"cop": f"https://x/{group_id}/c", "thief": f"https://x/{group_id}/t"},
            "mcp_servers": {group_id: f"https://{group_id}.example.com/mcp"},
            "llm_model": "template-free", "spec": dict(SPEC)}
    base.update(overrides)
    return {k: v for k, v in base.items() if v is not None}


def declaration(**overrides: object) -> dict:
    kwargs: dict = {
        "game_id": "g1", "game_uid": "u1",
        "our_identity": identity("sharnamr"),
        "opponent_identity": identity("rival", llm_model="gpt-x", spec=dict(THEIRS)),
        "config_sha256": "a" * 64, "num_sub_games": 6, "max_tokens_per_game": 1000,
        "started_at": "2026-08-07T10:00:00Z", "github_commit": "abcdef1",
        "games_played_declaration": {"count": 0},
    }
    kwargs.update(overrides)
    return build_declaration(**kwargs)


# --- each group speaks for itself ------------------------------------------------------


def test_both_groups_declare_their_own_machine() -> None:
    ours, theirs = declaration()["groups"]
    assert ours["hardware_spec"] == SPEC and ours["llm_model"] == "template-free"
    assert theirs["hardware_spec"] == THEIRS and theirs["llm_model"] == "gpt-x"


def test_the_two_specs_are_actually_different() -> None:
    """A guard on the fixture. If both groups carried the same spec the copy-detection
    tests below would pass no matter what the builder did."""
    ours, theirs = declaration()["groups"]
    assert ours["hardware_spec"] != theirs["hardware_spec"]


def test_the_single_top_level_copy_is_gone() -> None:
    document = declaration()
    assert "hardware" not in document and "llm_model" not in document


def test_our_own_spec_must_carry_every_member_the_book_names() -> None:
    """`inst/:1278` names them one by one; an incomplete spec forfeits the bonus."""
    for missing in SPEC:
        thin = {k: v for k, v in SPEC.items() if k != missing}
        with pytest.raises(DeclarationError, match=missing):
            declaration(our_identity=identity("sharnamr", spec=thin))


def test_we_must_declare_our_own_model_and_spec() -> None:
    for absent in ("llm_model", "spec"):
        with pytest.raises(DeclarationError, match="rule 24|AE-24"):
            declaration(our_identity=identity("sharnamr", **{absent: None}))


# --- and never for the other side ---------------------------------------------------------


@pytest.mark.parametrize("withheld", ["llm_model", "spec", "both"])
def test_an_undeclared_opponent_is_recorded_as_absent_never_filled_in(withheld: str) -> None:
    """**The finding this file exists for.** The reference copies its own identity into an
    empty opponent slot. Ours must be `None` — anything else is a claim we cannot support."""
    absent = {"llm_model": None, "spec": None} if withheld == "both" else {withheld: None}
    ours, theirs = declaration(opponent_identity=identity("rival", **absent))["groups"]
    if withheld in ("llm_model", "both"):
        assert theirs["llm_model"] is None
        assert theirs["llm_model"] != ours["llm_model"]
    if withheld in ("spec", "both"):
        assert theirs["hardware_spec"] is None
        assert theirs["hardware_spec"] != ours["hardware_spec"]


def test_the_withheld_members_are_named_so_the_omission_is_theirs() -> None:
    _, theirs = declaration(opponent_identity=identity("rival", llm_model=None,
                                                       spec=None))["groups"]
    assert set(theirs["undeclared"]) == {"llm_model", "hardware_spec"}
    assert "rival" in theirs["_note"]


def test_a_fully_declaring_opponent_gets_no_undeclared_marker() -> None:
    """The marker must mean something. Present on every group, it would mean nothing."""
    _, theirs = declaration()["groups"]
    assert "undeclared" not in theirs and "_note" not in theirs


def test_an_opponent_that_declares_is_still_recorded_verbatim() -> None:
    """Not measuring, recording. Refusing to carry what a peer declared would lose the
    only evidence the computational-fairness comparison has."""
    _, theirs = declaration()["groups"]
    assert theirs["hardware_spec"]["cpu_type"] == "Apple M1"


# --- signatures ----------------------------------------------------------------------------


def test_our_group_signs_itself_and_the_signature_reproduces() -> None:
    ours = declaration()["groups"][0]
    unsigned = {k: v for k, v in ours.items() if k != "signature"}
    assert ours["signature"] == lock_declaration(unsigned)


def test_the_signature_changes_when_the_declared_spec_changes() -> None:
    """Otherwise it commits to nothing and a swapped spec would go unnoticed."""
    other = declaration(our_identity=identity("sharnamr", spec={**SPEC, "ram_gb": 8.0}))
    assert other["groups"][0]["signature"] != declaration()["groups"][0]["signature"]


def test_an_opponents_signature_is_null_rather_than_borrowed() -> None:
    """Their negotiation signature covers the terms and the challenge nonce, not their
    identity block. Presenting it here would claim an authentication that does not exist."""
    ours, theirs = declaration()["groups"]
    assert theirs["signature"] is None and ours["signature"] is not None
