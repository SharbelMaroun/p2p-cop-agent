"""The labelled series uid, agreed with `yanell11` on 2026-08-17.

The unlabelled derivation consumes only the terms and the group pair, so it CANNOT tell two
series between the same peers apart -- by construction. Runs 4, 7 and 8 all carried
`9b80122e-…`, and runs 4 and 8 additionally share a consensus digest, both having finished
77-77 / 3-3 over a preimage with no timestamp. Two complete series, byte-indistinguishable.

The counter-example in `test_the_two_seeds_are_different_strings_for_the_same_pair` is the
one worth keeping: `yanell11`'s written spec described only the labelled formula while
claiming the unlabelled value was preserved, and the two disagree. Both teams now pin it so
nobody later "simplifies" the branches into one and silently renames every artifact either
side has written.
"""

import hashlib
import json
import uuid
from pathlib import Path

from p2p_cop_agent.adapters.report_identity import series_label
from p2p_cop_agent.protocol.negotiation import terms_from_config
from p2p_cop_agent.reporting.series_consensus import _canonical, derive_game_uid

GROUPS = ["sharNamr", "yanell11"]
MATCH = Path(__file__).resolve().parents[2] / "config" / "match_friendly_yanell11.json"

# Both values were reproduced independently by each team from the written formula alone,
# neither side reading the other's code. That is the only evidence the spec is implementable.
UNLABELLED = "9b80122e-75f9-c32d-5bff-abc032ae086b"
COUNTED_1 = "c7794f4c-325a-d005-74d0-7964090c098a"


def terms() -> dict:
    return terms_from_config(json.loads(MATCH.read_text(encoding="utf-8")))


def test_the_unlabelled_uid_is_unchanged() -> None:
    """Every artifact either peer has already written is named by this value."""
    assert derive_game_uid(terms(), GROUPS) == UNLABELLED
    assert derive_game_uid(terms(), GROUPS, None) == UNLABELLED


def test_the_counted_label_derives_the_agreed_uid() -> None:
    assert derive_game_uid(terms(), GROUPS, "sharNamr-vs-yanell11-counted-1") == COUNTED_1


def test_the_two_seeds_are_different_strings_for_the_same_pair() -> None:
    """The counter-example that caught the spec: `a-vs-b` is not `a|b`.

    Obvious written down, invisible in prose -- and following the prose renames everything.
    """
    seeded = _canonical(terms()) + b"|" + b"sharNamr-vs-yanell11"
    from_pair_string = str(uuid.UUID(bytes=hashlib.sha256(seeded).digest()[:16]))
    assert from_pair_string != UNLABELLED
    assert from_pair_string == "a971be34-4041-a76e-71b0-4b2c0f777c35"


def test_a_label_changes_the_uid() -> None:
    assert derive_game_uid(terms(), GROUPS, "sharNamr-vs-yanell11-counted-1") \
        != derive_game_uid(terms(), GROUPS, "sharNamr-vs-yanell11-counted-2")


def test_only_a_labelled_pair_id_triggers_the_new_branch() -> None:
    assert series_label("sharNamr-vs-yanell11-counted-1", GROUPS) \
        == "sharNamr-vs-yanell11-counted-1"
    assert series_label("yanell11-vs-sharNamr-counted-1", GROUPS) \
        == "yanell11-vs-sharNamr-counted-1"       # either ordering of the pair


def test_the_bare_pair_and_the_historical_ids_keep_the_old_derivation() -> None:
    """`G009` was reported to the lecturer under the unlabelled uid; it must not move."""
    for series_id in ("sharNamr-vs-yanell11", "G009", "G006", "game-5a7b4a6e58be", ""):
        assert series_label(series_id, GROUPS) is None
        assert derive_game_uid(terms(), GROUPS, series_label(series_id, GROUPS)) == UNLABELLED


def test_a_trailing_hyphen_is_not_a_label() -> None:
    assert series_label("sharNamr-vs-yanell11-", GROUPS) is None
