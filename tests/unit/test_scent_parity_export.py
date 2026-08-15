"""`M6-15`: what we offer an opponent is enough to reproduce our field, and nothing more.

Two failures matter here and they pull opposite ways. Offer too little and the opponent
cannot check interpretation, which is the whole point of the book's boxed method — the hash
alone tells two peers *that* they differ, never *where*. Offer too much and rule 2 is
breached: "Do not share memory or variables between parties at all. Sanction: Immediate
disqualification due to data leakage." Belief, trust and pursuit are agent-private by
`M6-18`; the scent model is the one part that is supposed to be public.

So both directions are asserted. The sufficiency tests would pass on a bundle that also
carried our belief state, and the leak tests would pass on an empty file.
"""

from __future__ import annotations

import json

import pytest

from p2p_cop_agent.strategy.scent import CENTER_INTENSITY, DECAY_RATE, DOCUMENTED_EMISSION
from p2p_cop_agent.strategy.scent_lock import scent_model_hash, scent_model_record
from scripts.export_scent_parity import PLACES, WALK, bundle, main, trace

BUNDLE = bundle()


# --- enough to reproduce the field ------------------------------------------------------


def test_the_offered_hash_is_the_one_we_would_negotiate_with() -> None:
    """A bundle quoting a different hash than the peer receives in negotiation would look
    like tampering — and rule 23 cancels the game for a scent deviation."""
    assert BUNDLE["scent_model_hash"] == scent_model_hash()
    assert BUNDLE["model_record"] == scent_model_record()


def test_the_worked_example_revisits_a_cell() -> None:
    """**The property the example exists for.** Decay ordering only diverges on
    re-emission: a walk over fresh cells agrees under both orderings, so a trace that never
    revisited would certify two peers as identical while they ran different physics."""
    assert len(set(WALK)) < len(WALK)
    assert WALK[0] == WALK[-1]


def test_the_trace_separates_decay_then_add_from_add_then_decay() -> None:
    """Re-derived from the emission table rather than compared to a stored number, so this
    fails if `ScentField` and the published profile ever stop agreeing.

    The first draft of this test expected `0.9 + 0.9*(1-0.1)^4` and was wrong: the walk's
    other three cells are all within the 5x5 window of `(3,3)`, so each of them deposits on
    it too. That mistake is the argument for publishing a trace at all — the arithmetic is
    not obvious even to someone holding the formula, the constants and the walk.
    """
    tau = 0.0
    for row, col in WALK:  # decay first, then add, then clamp: the book's order (`C-048`)
        delta = DOCUMENTED_EMISSION.get((WALK[0][0] - row, WALK[0][1] - col), 0.0)
        tau = min(max(0.0, (1.0 - DECAY_RATE) * tau + delta), CENTER_INTENSITY)

    steps = trace()
    revisited = f"{WALK[0][0]},{WALK[0][1]}"
    fresh, after = steps[0]["field"][revisited], steps[-1]["field"][revisited]
    assert fresh == 0.9, "a cell just stepped on reads the full centre intensity"
    assert after == pytest.approx(tau, abs=10 ** -PLACES)
    # The revisited centre used to end ABOVE `fresh`, and asserting that was how this test
    # showed re-emission adds rather than replaces. Under the `C-048` clamp it saturates at
    # the centre intensity instead, so that cell no longer discriminates and the assertion
    # would now pass for the wrong reason under either evaluation order.
    assert after == pytest.approx(CENTER_INTENSITY), "the revisited cell saturates"
    # The orderings still separate, just not at the ceiling: a cell that only ever receives
    # off-centre deposits stays below the cap, where decay-then-add and add-then-decay give
    # different numbers. Asserted on the first cell of the trace that is still below it, so
    # the test keeps the discriminating power the clamp took away from the centre.
    below = {cell: value for cell, value in steps[-1]["field"].items()
             if value < CENTER_INTENSITY - 10 ** -PLACES}
    assert below, "every published cell saturated; this trace can no longer separate orders"
    cell, decayed_then_added = next(iter(sorted(below.items())))
    added_then_decayed = decayed_then_added * (1.0 - DECAY_RATE)
    assert decayed_then_added != pytest.approx(added_then_decayed, abs=10 ** -PLACES), (
        f"cell {cell} reads the same under both orders; the trace proves nothing there")


def test_the_whole_board_is_published_not_just_a_window() -> None:
    """A 5x5 window hides whether cells outside it decayed. A peer decaying only inside its
    window would match every published number and still be wrong."""
    assert len(trace()[0]["field"]) == 25, "step 0 should show all 25 emitting cells"


def test_the_axis_convention_travels_with_the_numbers() -> None:
    """`row,col` under a different origin names a different cell, so the keys are
    meaningless without it — and the two peers here disagreed about axes before."""
    example = BUNDLE["worked_example"]
    assert example["keys"] == "row,col"
    assert example["axis_origin_corner"] == "top-left"
    assert example["axis_start_index"] == 0


def test_the_unbacked_ring_is_offered_as_negotiable_not_as_fact() -> None:
    """`U-030`: the eight cells at squared distance 5 have no book value. Presenting our
    choice as a constant would invite an opponent to adopt it as though the book said so."""
    assert "U-030" in BUNDLE["negotiable"]["_note"]
    assert "outer_ring_delta" in BUNDLE["negotiable"]


# --- and nothing more ---------------------------------------------------------------------


@pytest.mark.parametrize("private", ["belief", "trust", "posterior", "likelihood",
                                     "pursuit", "prior", "hint", "probabilit"])
def test_no_agent_private_state_is_offered(private: str) -> None:
    """Rule 2's sanction is immediate disqualification for data leakage. The `_note` names
    these as excluded, so the check reads the payload members rather than the whole text."""
    payload = json.dumps({k: v for k, v in BUNDLE.items() if not k.startswith("_")})
    assert private not in payload.lower().replace(
        "belief, trust and pursuit are agent-private", "")


def test_no_address_or_credential_travels_with_the_model() -> None:
    text = json.dumps(BUNDLE).lower()
    for secret in ("ngrok", "authtoken", "token", "client_secret", "password", "127.0.0.1"):
        assert secret not in text


def test_the_leak_checks_are_not_passing_on_an_empty_bundle(tmp_path) -> None:
    """The failure mode of an absence test is asserting against nothing."""
    assert main([str(tmp_path / "p.json")]) == 0
    written = json.loads((tmp_path / "p.json").read_text(encoding="utf-8"))
    assert len(json.dumps(written)) > 2000
    assert written["scent_model_hash"] == scent_model_hash()
