"""`M7-14`: nothing leaves the process without passing its own schema.

The condition is about **placement**, not about having a validator: "an artifact that
fails its own schema is never sent". A check living only in the test suite proves the
artifacts were valid on a developer's machine and says nothing about the file someone
emails after a hand-edit — so `validated_write` sits between building and writing.

The stakes are asymmetric, which is why these refuse rather than warn. `:2584`: a side
that does not report "will not be credited" — a cost to us alone. Rule 34 (Prohibited): a
report that is not JSON "will be rejected and result in a zero score". Rule 35
(Mandatory): a conflicting report costs **both** teams the game.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_cop_agent.reporting import MatchIdentity, build_config
from p2p_cop_agent.reporting.validate import (
    ArtifactInvalidError,
    check_one_identity,
    validate_artifact,
    validated_write,
)
from tests.unit.test_result_artifact import GAME, IDENT


def _config():
    return build_config(identity=IDENT, sub_game=1, game=GAME, config_sha256="a" * 64)


def test_a_valid_artifact_passes_and_is_written(tmp_path: Path) -> None:
    written = validated_write(tmp_path, "config_demo-series_g01.json", _config())
    assert json.loads(written.read_text("utf-8"))["game_uid"] == IDENT.game_uid


def test_an_invalid_artifact_is_refused_and_leaves_no_file(tmp_path: Path) -> None:
    """`M7-14`'s condition is about *placement*: validation before the write, so a bad
    artifact never reaches a disk anyone could email it from."""
    broken = {**_config(), "sub_game_number": 99}  # schema caps sub_game at 6
    with pytest.raises(ArtifactInvalidError, match="sub_game_number"):
        validated_write(tmp_path, "config_demo-series_g99.json", broken)
    assert not list(tmp_path.iterdir())


def test_an_artifact_with_no_schema_marker_cannot_be_called_validated() -> None:
    with pytest.raises(ArtifactInvalidError, match="carries no `_schema`"):
        validate_artifact({"game_id": "x"})


def test_an_unknown_artifact_kind_is_refused_rather_than_assumed_valid() -> None:
    """"Validated" must never quietly mean "unchecked" — that is how an unschema'd
    artifact ships looking exactly as trustworthy as a checked one."""
    with pytest.raises(ArtifactInvalidError, match="refusing to call it validated"):
        validate_artifact({"_schema": "not-a-real-kind"})


# --- M7-14e: the check no single schema can make ---------------------------------------


def test_a_set_sharing_one_identity_passes() -> None:
    check_one_identity([_config(), {**_config(), "sub_game": 2}])


def test_a_set_spanning_two_games_is_refused() -> None:
    """No per-file schema can catch this: each artifact is individually valid and they
    simply belong to different matches — a re-run config beside yesterday's log."""
    other = build_config(
        identity=MatchIdentity("other-series", "c" * 32), sub_game=1,
        game=GAME, config_sha256="a" * 64,
    )
    with pytest.raises(ArtifactInvalidError, match="game_uid"):
        check_one_identity([_config(), other])


def test_an_empty_set_is_refused() -> None:
    with pytest.raises(ArtifactInvalidError, match="proves nothing"):
        check_one_identity([])
