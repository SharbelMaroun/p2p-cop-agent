"""M6-18: internal certainty stays private; only the agreed observation crosses.

The Cop's belief over the Thief's position, and the trust it assigns a hint, are local
inference. They are not secrets in the cryptographic sense — nothing is hashed to hide
them — which is exactly why they need a *structural* guard rather than a convention: a
belief field added to a message would work perfectly and be caught by nothing.

**What the sources actually say, and what they do not.** Appendix E rules 8 and 9 are
narrower than they are often quoted as being — verified verbatim at
`inst/police_thief_p2p_Summary.md:3311-3312`, they govern the **live user interface**:

    8  Mandatory   Display true local information only in the live user interface.
    9  Prohibited  Do not display the full objective board state in the live user
                   interface.

Those are M8's problem. The *wire* constraint comes from the Zero-Trust rules instead:
sharing state creates "a 'backdoor' through which one agent might see the local truth of
its rival" (`:705`). And the reference agrees by construction — asked directly, its
belief grid never leaves a peer, appearing in no wire message, no sealed record, and no
audit payload, because "the sealed payload is designed to verify the truth of an agent's
own state and actions, not its internal guesses about the opponent."

So this file pins two structural properties. Both would survive a careless edit that a
reviewer might not.
"""

from __future__ import annotations

from pathlib import Path

from p2p_cop_agent.protocol.commit_reveal import _SECRET_KEYS
from p2p_cop_agent.shared.config import load_json_object

_SRC = Path(__file__).resolve().parents[2] / "src" / "p2p_cop_agent"
_SCHEMAS = Path(__file__).resolve().parents[2] / "shared_contract" / "schemas"

# Layers that serialise to, or carry, the wire. Nothing here may reach inference.
WIRE_LAYERS = (_SRC / "protocol", _SRC / "adapters")

# The private inference modules. `strategy.scent` and `strategy.scent_field` are
# deliberately NOT listed: the scent field is the one thing we are *required* to
# publish, so the wire layer legitimately builds it. What must never cross is what we
# *concluded* from it.
PRIVATE_INFERENCE = (
    "strategy.belief",
    "strategy.belief_pursuit",
    "strategy.consume",
    "strategy.hint_decode",
    "strategy.hint_consumption",
    "strategy.trust",
)
PRIVATE_SYMBOLS = (
    "Belief",
    "TrustScore",
    "Perception",
    "consume_turn",
    "scent_likelihood",
    "trust_weighted",
    "corroboration",
    "decode_hint",
    "pursue_belief",
)
CERTAINTY_MARKERS = ("belief", "certainty", "probab", "trust", "posterior", "likelihood")


def test_the_public_turn_schema_carries_no_certainty_field() -> None:
    """A belief member on the wire would work perfectly and be caught by nothing."""
    schema = load_json_object(_SCHEMAS / "turn-message.schema.json")
    published = set(schema["properties"])
    assert published == {
        "step", "sender", "hint", "smell_grid", "commit", "timestamp",
        "barrier_placed", "capture_claim", "claim_response", "win_claim",
    }
    offenders = [
        name for name in published
        if any(marker in name.lower() for marker in CERTAINTY_MARKERS)
    ]
    assert not offenders, f"the public turn message publishes certainty: {offenders}"


def test_the_public_turn_schema_still_forbids_our_own_private_truth() -> None:
    """The existing guard against position/move/nonce/intent/verdict must not erode."""
    schema = load_json_object(_SCHEMAS / "turn-message.schema.json")
    forbidden = {tuple(clause["required"])[0] for clause in schema["not"]["anyOf"]}
    assert forbidden == {"position", "move", "nonce", "intent", "verdict"}


def test_the_sealed_record_keeps_our_own_truth_secret_and_holds_no_belief() -> None:
    """What we seal proves *our* actions; it is not a confession of our guesses."""
    assert set(_SECRET_KEYS) == {"payload", "nonce", "position", "move", "intent", "verdict"}
    assert not any(
        marker in key for key in _SECRET_KEYS for marker in CERTAINTY_MARKERS
    )


def test_the_wire_layers_never_import_the_private_inference_modules() -> None:
    """Belief must not be able to reach a message even indirectly.

    The roster test above only catches a field someone *named* honestly. This catches
    the case where inference is imported into the wire layer and its output smuggled
    into an existing field — a hint, say, or the scent grid.
    """
    offenders: list[str] = []
    for layer in WIRE_LAYERS:
        for path in sorted(layer.rglob("*.py")):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                stripped = line.strip()
                if not stripped.startswith(("import ", "from ")):
                    continue
                if any(module in stripped for module in PRIVATE_INFERENCE) or any(
                    f" {symbol}" in stripped or f"{symbol}," in stripped
                    for symbol in PRIVATE_SYMBOLS
                ):
                    offenders.append(f"{path.relative_to(_SRC)}:{number}: {stripped}")
    assert not offenders, "the wire layer reaches private inference:\n" + "\n".join(offenders)


def test_the_wire_layer_may_still_build_the_scent_it_is_required_to_publish() -> None:
    """The guard must not over-reach: emitting scent is an obligation, not a leak.

    `:895` — "each side emits its own scent". A guard that forbade the wire layer from
    touching the scent modules would forbid the very thing rule 23 locks us into doing,
    so `strategy.scent` and `strategy.scent_field` are deliberately outside the ban.
    """
    assert not any("scent" in module for module in PRIVATE_INFERENCE)
    serve = (_SRC / "adapters" / "serve.py").read_text(encoding="utf-8")
    assert "ScentField" in serve, "the live path must still emit a real trail"
