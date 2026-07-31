"""`M5-04d`: Appendix F parameter policy, on its own.

`Fixed` values may not change at all and `Minimum` values may be raised by
agreement but never lowered (`[AE-12]` `[AF-§1]`). Split out of
`test_negotiation.py` so the offer-acceptance tests and the parameter policy can
each be read without the other.
"""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.protocol.negotiation import (
    NegotiationError,
    check_appendix_f,
    terms_from_config,
)

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"


def game() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("term", "value"),
    [("smell_grid_size", 3), ("decay_per_step", 0.5), ("emit_intensity", 1.0), ("num_games", 1)],
)
def test_an_altered_fixed_value_is_refused(term: str, value: object) -> None:
    """`[AE-12]`: a Fixed Appendix F parameter may not change at all."""
    with pytest.raises(NegotiationError, match=f"{term} is Fixed"):
        check_appendix_f(terms_from_config(game()) | {term: value})


@pytest.mark.parametrize(("term", "value"), [("board_size", 6), ("max_steps", 34),
                                             ("barriers_max", 13)])
def test_a_lowered_minimum_is_refused(term: str, value: int) -> None:
    """`[AE-12]`: a Minimum may be raised by agreement but never lowered."""
    with pytest.raises(NegotiationError, match=f"{term} is a Minimum"):
        check_appendix_f(terms_from_config(game()) | {term: value})


@pytest.mark.parametrize(("term", "value"), [("board_size", 9), ("max_steps", 50),
                                             ("barriers_max", 20)])
def test_a_raised_minimum_is_allowed(term: str, value: int) -> None:
    check_appendix_f(terms_from_config(game()) | {term: value})

