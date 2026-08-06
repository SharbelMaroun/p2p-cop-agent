"""`M7-23`, `M7-02a/b/c`, `M7-25`: the artifact set is named, locked, and safely written.

The condition that shapes this file is `M7-23`'s: "the emitted config is **the one
actually played, not a template**". `fixtures/match_config.example.json` is a valid config
that describes no game; an artifact built from it would pass its own schema and a casual
read. So the tests below check the artifact against the *game object it was built from*,
never against a constant.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema.validators import validator_for

from p2p_cop_agent.reporting import (
    ConfigArtifactError,
    MatchIdentity,
    NamingError,
    build_config,
    config_filename,
    declaration_filename,
    log_filename,
    match_filenames,
    quantitative_parameters,
    result_filename,
)

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "shared_contract"
GAME = json.loads((BUNDLE / "fixtures" / "match_config.example.json").read_text("utf-8"))
IDENT = MatchIdentity("demo-series", "b1946ac92492d2347c6235b4d2611184")
SHA = "a" * 64


def _artifact(**kw):
    kwargs = {"identity": IDENT, "sub_game": 1, "game": GAME, "config_sha256": SHA}
    kwargs.update(kw)
    return build_config(**kwargs)


# --- naming (M7-02c) -----------------------------------------------------------------


def test_the_four_names_follow_the_book() -> None:
    """`:3600` fixes all four; two are per-series and two per-sub-game."""
    assert declaration_filename(IDENT) == "declaration_demo-series.json"
    assert result_filename(IDENT) == "result_demo-series.json"
    assert config_filename(IDENT, 1) == "config_demo-series_g01.json"
    assert log_filename(IDENT, 6) == "log_demo-series_g06.json"


def test_sub_game_numbers_are_zero_padded_so_they_sort() -> None:
    """An auditor lists a directory; `g1, g10, g2` would read as a different series."""
    names = sorted(match_filenames(IDENT, (1, 2, 10)).values())
    assert names.index("config_demo-series_g02.json") < names.index("config_demo-series_g10.json")


@pytest.mark.parametrize("bad", ["../escape", "a/b", "", "..", "x" * 80])
def test_a_game_id_that_is_not_filename_safe_is_refused(bad: str) -> None:
    """`game_id` is negotiated with an opponent and then becomes part of a path."""
    with pytest.raises(NamingError):
        MatchIdentity(bad, "uid")


@pytest.mark.parametrize("bad", [0, 100, True, "1"])
def test_an_impossible_sub_game_number_is_refused(bad: object) -> None:
    with pytest.raises(NamingError):
        config_filename(IDENT, bad)  # type: ignore[arg-type]


# --- the config artifact (M7-23, M7-23a, M7-23b) --------------------------------------


def test_the_artifact_validates_against_the_bundles_own_schema() -> None:
    """The shape is not ours to invent — `per-subgame-config.schema.json` already fixes it."""
    schema = json.loads((BUNDLE / "schemas" / "per-subgame-config.schema.json").read_text("utf-8"))
    validator_for(schema)(schema).validate(_artifact())


def test_every_appendix_f_section_is_carried_with_its_agreed_value() -> None:
    """`M7-23a`. Compared against the *source game object*, not a literal, so the test
    cannot pass while the artifact quietly describes something else."""
    flat = quantitative_parameters(_artifact())
    assert flat["board_and_agents.grid_size"] == GAME["board_and_agents"]["grid_size"]
    assert flat["pheromones.pheromone_decay"] == GAME["pheromones"]["pheromone_decay"]
    assert flat["scoring.capture_cop"] == GAME["scoring"]["capture_cop"]
    assert flat["network_and_league.num_games"] == GAME["network_and_league"]["num_games"]


def test_the_artifact_is_the_game_played_not_a_template() -> None:
    """`M7-23`'s actual condition. Change one agreed value and the artifact must follow."""
    played = {**GAME, "movement_and_barriers": {**GAME["movement_and_barriers"], "max_moves": 41}}
    assert quantitative_parameters(_artifact(game=played))["movement_and_barriers.max_moves"] == 41


def test_both_cryptographic_locks_are_present() -> None:
    """`M7-23b`. Rule 11 (Mandatory) for the config hash — configuration "identical,
    bit-for-bit", sanction "disqualification… for lack of symmetry"; rule 23 (Mandatory)
    for the scent model — "lock the cryptographic hash of the scent model before the
    start of the game. Sanction: deviation from the formula cancels the game"."""
    artifact = _artifact()
    assert artifact["config_sha256"] == SHA
    assert len(artifact["scent_model_sha256"]) == 64


def test_the_scent_lock_is_the_one_both_repositories_reproduce() -> None:
    """Not a fresh digest: the same locked model the Thief reproduces independently."""
    from p2p_cop_agent.strategy.scent_lock import scent_model_hash

    assert _artifact()["scent_model_sha256"] == scent_model_hash()


def test_a_missing_appendix_f_section_is_refused_by_name() -> None:
    thin = {k: v for k, v in GAME.items() if k != "pheromones"}
    with pytest.raises(ConfigArtifactError, match="pheromones"):
        _artifact(game=thin)


@pytest.mark.parametrize("bad", ["", "abc", "a" * 63])
def test_a_malformed_config_hash_is_refused(bad: str) -> None:
    with pytest.raises(ConfigArtifactError, match="config_sha256"):
        _artifact(config_sha256=bad)


def test_an_empty_game_object_is_refused_rather_than_producing_an_empty_artifact() -> None:
    with pytest.raises(ConfigArtifactError, match="not a template"):
        _artifact(game={})
