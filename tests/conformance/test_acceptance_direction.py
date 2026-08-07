"""`M8-03b`: the direction the existing suite does not cover — **we accept their offer**.

`test_neutral_stub_wire.py` proves the proposal direction end to end: our offer crosses a
real MCP boundary and a peer sharing no code with us accepts it. That is half the surface.
`M8-03b`'s condition is "**both** proposal and acceptance directions", and the reason the
second half matters is asymmetric: in a real league we do not choose who opens. If the
opponent proposes and our review path is the one with the bug, every match we did not
initiate is refused — and the failure looks like *their* fault.

The row's second clause — "neither direction needs a profile file edited" — is the sharper
one. A suite that passes only after someone tweaks a local profile has proved that our
tooling can be made to agree with itself, not that an unknown opponent will be understood.
So every offer here is built by the **stub**, from its own independently re-derived
canonicalization, and fed to our reviewer unmodified.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_cop_agent.protocol import terms_from_config
from p2p_cop_agent.protocol.offer_review import verify_offer
from tests.conformance.neutral_stub import commit

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
CHALLENGE = "0123456789abcdef0123456789abcdef"
# The full identity block, because rule 24 and `:2229` make every member of it mandatory --
# our own builder refuses a partial one, which is the correct behaviour and the reason this
# fixture is not trimmed to what the test happens to read.
IDENTITY = {
    "group_id": "neutral-group-alpha", "group_name": "Alpha", "members": ["a", "b"],
    "repos": {"cop": "https://example.test/cop", "thief": "https://example.test/thief"},
    "mcp_servers": {"cop": "https://cop.example.test/mcp"}, "llm_model": "cli-default",
    "spec": {"os": "Example OS", "cpu": "Example CPU"},
}


def game() -> dict:
    return json.loads(EXAMPLE.read_text("utf-8"))


def stub_offer(config: dict | None = None, *, nonce: str = CHALLENGE) -> dict:
    """An offer built entirely by the neutral side.

    Deliberately assembled from `commit()` — the stub's own reimplementation of the
    construction — rather than from `build_offer`. Using ours would make this a test of our
    reviewer against our own builder, which is exactly the self-agreement the neutral stub
    exists to break.
    """
    terms = terms_from_config(config or game())
    return {"terms": terms, "signature": commit(terms, nonce), "nonce": nonce,
            "group_id": "neutral-group-beta", "role": "thief"}


# --- the acceptance direction -------------------------------------------------------------


def test_we_accept_an_offer_the_neutral_peer_constructed() -> None:
    """**The gap this module closes.** Their bytes, their signature, our reviewer."""
    verify_offer(stub_offer(), terms_from_config(game()))


def test_acceptance_needs_no_local_profile_edit() -> None:
    """The row's second clause, made concrete: the offer is reviewed against the committed
    fixture exactly as it ships. If this ever needs a file adjusted first, the suite is
    measuring our willingness to accommodate rather than our interoperability."""
    pristine = json.loads(EXAMPLE.read_text("utf-8"))
    verify_offer(stub_offer(pristine), terms_from_config(pristine))


def test_a_signature_the_stub_computed_differently_is_refused() -> None:
    """The acceptance path has to be a *check*, not a formality. If any signature passed,
    the direction would "work" while proving nothing."""
    forged = {**stub_offer(), "signature": "f" * 64}
    with pytest.raises(Exception, match="(?i)signature|lock|mismatch"):
        verify_offer(forged, terms_from_config(game()))


def test_an_offer_whose_terms_differ_from_ours_is_refused() -> None:
    """Rule 11 (Mandatory): the configuration must be "identical, bit-for-bit, on both
    sides", sanction "disqualification of the game due to lack of symmetry". Accepting a
    differing offer would disqualify the game we just agreed to play."""
    theirs = game()
    theirs["movement_and_barriers"]["max_barriers"] = 99
    with pytest.raises(Exception, match="(?i)mismatch|differ|lock|config"):
        verify_offer(stub_offer(theirs), terms_from_config(game()))


def test_the_two_directions_agree_on_the_same_signed_bytes() -> None:
    """Proposal and acceptance must be the *same* protocol seen from two ends. If our
    builder and the stub's builder produced different signatures for identical terms, one
    direction would pass and the other fail — and which one broke would depend on who
    opened the match."""
    from p2p_cop_agent.protocol import build_offer  # noqa: PLC0415

    ours = build_offer(game(), IDENTITY, nonce=CHALLENGE)
    assert ours["signature"] == commit(ours["terms"], CHALLENGE)
    assert ours["terms"] == stub_offer()["terms"]


def test_a_replayed_nonce_does_not_make_a_second_offer_verify_as_new() -> None:
    """Same nonce, same terms, same signature — by construction. Pinned so nobody reads a
    passing second verification as freshness: the reviewer checks *integrity*, and replay
    protection lives in the turn ledger, not here."""
    first, second = stub_offer(), stub_offer()
    assert first["signature"] == second["signature"]
    verify_offer(second, terms_from_config(game()))
