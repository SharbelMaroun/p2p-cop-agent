"""`M7-10*`, `X-10`: every game's config is committed, and any past one is retrievable.

Appendix F obligation 4 requires each game's configuration attached to the GitHub repository.
The finding that produced this module is that **this repository was not meeting it**:
`/logs/` is gitignored, so a config emitted there lives on one machine and nowhere the
obligation can see. The failure is silent — the write succeeds and the file is present.

So the test that matters most reads the real `.gitignore` and fails if `games/` is ever added
to it, because the realistic way this regresses is somebody tidying the working tree.
"""

from __future__ import annotations

import pathlib

import pytest

from p2p_cop_agent.reporting.retention import (
    COMMITTED_GAMES_DIR,
    IGNORED_PATHS,
    RetentionError,
    game_directory,
    missing_configs,
    retrieve_config,
    store_config,
    stored_games,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
GAME = "sharNamr-vs-rival"
SERIES = (1, 2, 3, 4, 5, 6)
CONFIG = {"_schema": "per-subgame-config", "config_sha256": "a" * 64,
          "scoring": {"capture": 20}}


def gitignore_lines() -> set[str]:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    return {line.strip().strip("/") for line in text.splitlines()
            if line.strip() and not line.startswith("#")}


def test_the_committed_games_directory_is_not_gitignored() -> None:
    """**The test this module exists for.** `games/` must stay committable, and the way this
    regresses is somebody adding it to `.gitignore` for tidiness — the same reasoning that
    put `/logs/` there and lost every config with it."""
    assert COMMITTED_GAMES_DIR not in gitignore_lines(), (
        f"{COMMITTED_GAMES_DIR}/ is excluded; Appendix F obligation 4 requires every game's "
        "config to be committed")


def test_every_refused_path_is_one_gitignore_actually_excludes() -> None:
    """The refusal list is data, not a reading of `.gitignore` — a guard deriving its rule
    from the file it checks agrees with itself. This asserts the two still say the same."""
    lines = gitignore_lines()
    for ignored in IGNORED_PATHS:
        assert "/".join(ignored) in lines, f"{'/'.join(ignored)}/ is refused but not ignored"


def test_storing_under_an_ignored_root_is_refused(tmp_path) -> None:
    """The write would succeed and the file would be there; only the commit would be
    missing, which is the part nobody notices until grading."""
    with pytest.raises(RetentionError, match="obligation 4"):
        store_config(tmp_path / "logs", GAME, 1, CONFIG)


def test_an_ignored_run_is_caught_at_any_depth(tmp_path) -> None:
    """Matched as a run of components, so `build/logs/out` is caught — the shape a path
    assembled from a base and a suffix actually takes."""
    with pytest.raises(RetentionError):
        store_config(tmp_path / "build" / "logs" / "out", GAME, 1, CONFIG)


def test_a_config_is_stored_under_a_game_id_derived_path(tmp_path) -> None:
    path = store_config(tmp_path, GAME, 1, CONFIG)
    assert path.parent == game_directory(tmp_path, GAME)
    assert path.name == f"config_{GAME}_g01.json"


def test_each_sub_game_gets_its_own_file(tmp_path) -> None:
    """Six sub-games, six configs. One file per match would let a later sub-game's terms
    overwrite an earlier one's, and the overwritten game becomes irreproducible."""
    for number in (1, 2, 3):
        store_config(tmp_path, GAME, number, {**CONFIG, "sub_game_number": number})
    assert len(list(game_directory(tmp_path, GAME).iterdir())) == 3


def test_a_game_id_that_could_climb_out_is_refused(tmp_path) -> None:
    """`game_id` is negotiated with an opponent, so it is untrusted input reaching a path."""
    for hostile in ("../escape", "a/b", ".."):
        with pytest.raises(RetentionError, match="cannot address a directory"):
            game_directory(tmp_path, hostile)


def test_a_stored_config_round_trips(tmp_path) -> None:
    """The retrieval half is what makes retention checkable — a store with no reader is a
    claim that files exist somewhere."""
    store_config(tmp_path, GAME, 2, CONFIG)
    assert retrieve_config(tmp_path, GAME, 2) == CONFIG


def test_retrieving_an_uncommitted_config_says_which_sub_game(tmp_path) -> None:
    with pytest.raises(RetentionError, match="sub-game 4"):
        retrieve_config(tmp_path, GAME, 4)


def test_stored_games_lists_every_match(tmp_path) -> None:
    store_config(tmp_path, GAME, 1, CONFIG)
    store_config(tmp_path, "older", 1, CONFIG)
    assert stored_games(tmp_path) == ("older", GAME)


def test_stored_games_on_a_fresh_clone_is_empty(tmp_path) -> None:
    """Empty, not an error: a clone before the first game is a normal state, and raising
    would make the pre-submission check loudest when it has least to say."""
    assert stored_games(tmp_path) == ()


def test_missing_configs_reports_every_gap(tmp_path) -> None:
    """The pre-submission question, where the useful answer is the whole list."""
    store_config(tmp_path, GAME, 1, CONFIG)
    store_config(tmp_path, GAME, 4, CONFIG)
    assert missing_configs(tmp_path, GAME, SERIES) == (2, 3, 5, 6)


def test_a_complete_series_reports_no_gaps(tmp_path) -> None:
    for number in SERIES:
        store_config(tmp_path, GAME, number, CONFIG)
    assert missing_configs(tmp_path, GAME, SERIES) == ()
