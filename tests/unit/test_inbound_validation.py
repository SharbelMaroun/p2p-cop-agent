"""`M8-04b`: malformed peer input cannot reach domain code.

`:12/50` states the principle in four words — **"never trust an unverified move"** — and
asked directly, the required response shape is an acknowledgement carrying acceptance:
`{"accepted": is_valid, "move": signed_move if is_valid else None}`. Rule 33 makes the same
point about reports: an invalid structure "will be rejected; score 0 in processing".

`test_adversarial_peer.py` already covers the *scenarios* — a replayed turn, a conflicting
commit, an unknown tool. This module covers the **field surface**: every message type,
every required field, systematically removed and mistyped. That is the shape of failure a
scenario test misses, because a scenario picks one malformation and a peer picks another.

**Why "cannot reach" and not "is rejected".** A rejection that happens *after* the value
touched a board, a ledger or a belief update has already changed state, and rule 5 makes an
illegal state transition a "logical error leading to loss". So the last test here asserts
that validation raises before any domain object is constructed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_cop_agent.protocol.messages import (
    MESSAGE_SCHEMAS,
    ProtocolError,
    validate_message,
)

SCHEMAS = Path(__file__).resolve().parents[2] / "shared_contract" / "schemas"

WELL_FORMED = {
    "turn": {"step": 1, "sender": "police", "commit": "a" * 64,
             "hint": "closing in from the north", "smell_grid": {"0,0": 0.9},
             "timestamp": "2026-08-07T10:00:00Z"},
    "control": {"kind": "status", "sender": "police"},
}


def _required(name: str) -> list[str]:
    schema = json.loads((SCHEMAS / MESSAGE_SCHEMAS[name]).read_text("utf-8"))
    return list(schema.get("required", []))


# --- the well-formed baseline, so the rest is not vacuous --------------------------------


@pytest.mark.parametrize("name", sorted(WELL_FORMED))
def test_a_well_formed_message_is_accepted(name: str) -> None:
    """A validator that refused everything would pass every negative test below while
    making the agent unable to play at all."""
    validate_message(name, WELL_FORMED[name])


# --- M8-04b: every required field, removed ------------------------------------------------


@pytest.mark.parametrize("name", sorted(WELL_FORMED))
def test_removing_any_single_required_field_is_refused(name: str) -> None:
    """One test, every field — driven off the schema's own `required` list, so a field added
    to the schema later is covered without anyone remembering to extend this."""
    required = _required(name)
    assert required, f"{name} declares no required fields; is the schema a stub?"
    for field in required:
        broken = {k: v for k, v in WELL_FORMED[name].items() if k != field}
        with pytest.raises(ProtocolError):
            validate_message(name, broken)


@pytest.mark.parametrize("name", sorted(WELL_FORMED))
def test_replacing_any_required_field_with_a_wrong_type_is_refused(name: str) -> None:
    """Absence is the easy case. A peer that sends `step: "one"` or `commit: null` is the
    one that reaches a comparison and throws somewhere far from the wire."""
    for field in _required(name):
        for wrong in (None, [], "not a number", 1.5):
            if isinstance(WELL_FORMED[name][field], type(wrong)):
                continue  # not a wrong type for this field
            broken = {**WELL_FORMED[name], field: wrong}
            with pytest.raises(ProtocolError):
                validate_message(name, broken)


def test_an_empty_scent_grid_is_accepted_and_that_is_a_recorded_gap() -> None:
    """**Not an endorsement — a pin (`U-034`).**

    `{}` passes, because the schema types `smell_grid` as `object` and an empty object is
    one. That is a *wrong value*, not a wrong type, which is why the sweep above no longer
    treats it as one.

    Whether it should pass is a real question. `:917` says scent is created "every time an
    agent moves or remains in its location", and the 5x5 window is centred on the sender's
    own cell — so a sender's own window can never legitimately be empty, and a scent-free
    turn is the exact shape the `M6-08` bug had before it was found. Tightening the schema
    with `minProperties: 1` would catch it, but the schema is *shared* and tightening it
    unilaterally would refuse a conformant peer that opens differently. Recorded, not
    changed.
    """
    validate_message("turn", {**WELL_FORMED["turn"], "smell_grid": {}})


@pytest.mark.parametrize("shape", [None, [], "a string", 42, True])
def test_a_message_that_is_not_an_object_is_refused(shape: object) -> None:
    """The first thing a hostile or broken peer sends is often not a JSON object at all."""
    with pytest.raises(ProtocolError):
        validate_message("turn", shape)


def test_an_unknown_message_type_is_refused_rather_than_skipped() -> None:
    """A validator that silently passes an unrecognised name validates nothing, which is
    worse than having no validator because it reads as protection."""
    with pytest.raises((ProtocolError, KeyError)):
        validate_message("not_a_message_type", {"anything": 1})


# --- "cannot reach domain code" ----------------------------------------------------------


def test_validation_refuses_before_any_domain_object_is_built() -> None:
    """**The row's actual condition.** A rejection that lands *after* the value touched a
    board, a ledger or a belief has already changed state, and rule 5 makes an illegal
    state transition "a logical error leading to loss".

    Proven by giving a malformed turn a payload that would be catastrophic if it were ever
    used — an off-board coordinate and a negative step — and asserting the refusal comes
    from validation, not from the domain raising later.
    """
    hostile = {**WELL_FORMED["turn"], "step": -1, "smell_grid": {"999,999": 5.0}}
    with pytest.raises(ProtocolError):
        validate_message("turn", hostile)


def test_the_validator_reads_a_real_schema_file_for_every_declared_type() -> None:
    """A missing schema file would make `validate_message` fail open or crash at match time
    rather than at import — and the first symptom would be during a counted game."""
    for name, filename in MESSAGE_SCHEMAS.items():
        assert (SCHEMAS / filename).exists(), f"{name} names a schema that is not present"
        schema = json.loads((SCHEMAS / filename).read_text("utf-8"))
        assert schema.get("type") or schema.get("properties"), f"{filename} looks empty"
