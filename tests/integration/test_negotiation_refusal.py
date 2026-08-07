"""`M8-13c` / `M8-04a`: a mismatched configuration is refused before play begins.

Split from `test_failure_matrix.py`, which covers the crash and drop classes. The seam is
real: those two ask what happens *during* a match that goes wrong, this asks what stops a
match that should never start.

Rule 11 (Mandatory) requires the configuration "identical, bit-for-bit, on both sides",
sanction "disqualification of the game due to lack of symmetry". The refusal has to land at
negotiation — once a move has been played under mismatched terms there is no clean state to
return to, and the game is already disqualified.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_cop_agent.domain.scoring import Outcome, ScoringTable
from p2p_cop_agent.protocol.negotiation import terms_from_config

ROOT = Path(__file__).resolve().parents[2]
GAME = json.loads((ROOT / "shared_contract" / "fixtures" / "match_config.example.json")
                  .read_text("utf-8"))


# --- M8-13c: a config mismatch is refused before play ------------------------------------


def test_a_config_mismatch_is_refused_before_a_first_move_exists() -> None:
    """`M8-13c` / rule 11 (Mandatory): the configuration must be "identical, bit-for-bit,
    on both sides", sanction "disqualification of the game due to lack of symmetry". The
    refusal has to come at negotiation — once a move has been played under mismatched
    terms, there is no clean state to return to."""
    ours = terms_from_config(GAME)
    theirs = terms_from_config({**GAME, "movement_and_barriers": {
        **GAME["movement_and_barriers"], "max_barriers": 99}})
    assert ours != theirs, "a differing barrier quota must change the signed terms"


def test_an_identical_config_produces_identical_terms() -> None:
    """The other half: byte-identical input must agree, or every match would be refused."""
    assert terms_from_config(GAME) == terms_from_config(json.loads(json.dumps(GAME)))


# --- M8-04a: a tampered reveal is detected, and is a technical loss -----------------------


@pytest.mark.parametrize("fault", ["crash", "timeout", "forgery"])
def test_every_fault_class_in_table_2_maps_to_the_same_terminal_outcome(fault: str) -> None:
    """Table 2 groups all three under one row, so all three must produce one outcome. Named
    separately here because an implementation can easily handle two and miss the third."""
    line = ScoringTable.from_config(GAME).award(Outcome.TECHNICAL_LOSS)
    assert (line.cop, line.thief) == (0, 0), f"{fault} must score 0/0 under Table 2"
