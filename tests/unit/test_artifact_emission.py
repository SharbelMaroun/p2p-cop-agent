"""`M7-25`, `M7-02a/b`: an artifact reaches disk whole, or not at all.

`M7-25` requires emission to survive a dead peer — "a disconnected game still produces
its artifact set" — so nothing here holds a socket. Atomicity is the other half: an
artifact is read back during rule 19's audit phase, whose sanction is "score of 0 for
the falsifying group", and a half-written file is indistinguishable from a tampered one
by then.

`test_reporting_artifacts.py` carries the naming and config-content half.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_cop_agent.reporting import (
    EmitError,
    artifact_bytes,
    build_config,
    config_filename,
    write_artifact,
)
from tests.unit.test_reporting_artifacts import GAME, IDENT, SHA


def _artifact(**kw):
    kwargs = {"identity": IDENT, "sub_game": 1, "game": GAME, "config_sha256": SHA}
    kwargs.update(kw)
    return build_config(**kwargs)


def test_an_artifact_round_trips_through_the_written_file(tmp_path: Path) -> None:
    artifact = _artifact()
    written = write_artifact(tmp_path, config_filename(IDENT, 1), artifact)
    assert json.loads(written.read_text("utf-8")) == artifact


def test_no_temporary_file_survives_a_successful_write(tmp_path: Path) -> None:
    """The swap is `os.replace` in the same directory; a stray `.tmp` would later be
    committed alongside the real artifact and read as part of the evidence set."""
    write_artifact(tmp_path, config_filename(IDENT, 1), _artifact())
    assert [p.name for p in tmp_path.iterdir()] == [config_filename(IDENT, 1)]


def test_a_rewrite_replaces_rather_than_appends(tmp_path: Path) -> None:
    """Re-emitting after a post-game re-lock must leave one valid document."""
    name = config_filename(IDENT, 1)
    write_artifact(tmp_path, name, _artifact())
    write_artifact(tmp_path, name, _artifact(sub_game=1, config_sha256="b" * 64))
    assert json.loads((tmp_path / name).read_text("utf-8"))["config_sha256"] == "b" * 64


@pytest.mark.parametrize("bad", ["../escape.json", "a/b.json", "", "."])
def test_a_filename_with_a_path_component_is_refused(tmp_path: Path, bad: str) -> None:
    """The last line of defence if a negotiated `game_id` ever reached a path unchecked."""
    with pytest.raises(EmitError):
        write_artifact(tmp_path, bad, _artifact())


def test_the_bytes_are_utf8_with_a_trailing_newline(tmp_path: Path) -> None:
    """These are committed to a repository; a file without a final newline is a permanent
    diff nuisance, and `ensure_ascii=False` matches the canonicalization the hashes use."""
    raw = artifact_bytes({"hint": "café near the north edge"})
    assert raw.endswith(b"\n")
    assert "café" in raw.decode("utf-8")


def test_emission_needs_no_transport_or_peer(tmp_path: Path) -> None:
    """`M7-25`: "a disconnected game still produces its artifact set". The signature is
    the guarantee — a directory and an object, no socket, no client, no peer state."""
    from inspect import signature

    names = set(signature(write_artifact).parameters)
    assert names == {"directory", "filename", "artifact"}
