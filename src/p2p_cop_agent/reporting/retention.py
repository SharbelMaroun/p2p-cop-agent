"""Every game's config, kept where the repository can carry it (`M7-10`, `X-10`).

Appendix F obligation 4 (p.140/288): "It is mandatory to attach each game's configuration
file to the GitHub repository." That is the **only** hard commit obligation among the four
artifacts — the log has none in §9.4.1's minimum-contents list (though it is needed to run
the Replay app, which rule 20 makes a threshold condition), and the result's duty is to be
emailed under rule 51.

**This repository was not meeting obligation 4.** `.gitignore` excludes `/logs/`, where run
artifacts are written, so a config emitted there is retained on one machine and lost to the
repository. The failure is silent: the write succeeds, a directory listing shows the file,
and it is missing only from the place the obligation looks.

So configs go to `games/`, which is deliberately not ignored, and `store_config` refuses a
destination under an ignored path rather than writing a file that can never be committed.

Committing them is safe under rule 39 — which forbids secrets in the repository "even if it
is private and shared only with the lecturer" — **because** `protocol/private_fields.py`
already keeps strategy, model and credential fields out of the shared config, matching on key
names rather than values. Obligation 4 and rule 39 are jointly satisfiable only because that
guard runs first.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path

from p2p_cop_agent.reporting.emit import write_artifact

COMMITTED_GAMES_DIR = "games"

# Paths `.gitignore` excludes, as component runs rather than single names. `/logs/` is
# ignored wholesale; a bare `reports/` or `results/` is committable and refusing it would
# send a caller hunting for a problem that is not there. Kept as data rather than parsed from
# `.gitignore`, so a test can assert the two agree — a guard that derives its rule from the
# file it checks agrees with itself by construction.
IGNORED_PATHS: tuple[tuple[str, ...], ...] = (("logs",),)


class RetentionError(ValueError):
    """Raised when a config would be stored where the repository cannot carry it."""


def game_directory(root: Path, game_id: str) -> Path:
    """Where one match's committed configs live.

    Per `game_id` rather than one flat directory: a series is six configs, and flat storage
    turns "which configs belong to this match" into filename parsing for whoever audits it.
    """
    if not game_id or "/" in game_id or "\\" in game_id or game_id in {".", ".."}:
        raise RetentionError(f"game_id {game_id!r} cannot address a directory")
    return Path(root) / COMMITTED_GAMES_DIR / game_id


def _refuse_ignored(root: Path) -> None:
    """Refuse a destination `.gitignore` excludes, matched as a run of path components.

    Component-wise rather than by prefix, because the realistic caller builds this path by
    joining a base onto something else, so the excluded run appears in the middle
    (`build/logs/games`) rather than at the front.
    """
    parts = [part.lower() for part in Path(root).parts]
    for ignored in IGNORED_PATHS:
        width = len(ignored)
        if any(tuple(parts[i:i + width]) == ignored for i in range(len(parts) - width + 1)):
            raise RetentionError(
                f"{root} sits under {'/'.join(ignored)}/, which .gitignore excludes; a config "
                "written there is retained on this machine and lost to the repository, and "
                "Appendix F obligation 4 requires every game's config to be committed")


def config_filename(game_id: str, sub_game: int) -> str:
    return f"config_{game_id}_g{sub_game:02d}.json"


def store_config(root: Path, game_id: str, sub_game: int,
                 artifact: Mapping[str, object]) -> Path:
    """Write one sub-game's config where the repository will carry it (`M7-10a`)."""
    _refuse_ignored(root)
    return write_artifact(game_directory(root, game_id), config_filename(game_id, sub_game),
                          artifact)


def retrieve_config(root: Path, game_id: str, sub_game: int) -> dict:
    """Read back any past game's config (`M7-10b`).

    The retrieval half is what makes retention checkable. A store with no reader is a claim
    that files exist somewhere; this is the operation an auditor actually performs.
    """
    path = game_directory(root, game_id) / config_filename(game_id, sub_game)
    if not path.is_file():
        raise RetentionError(
            f"no committed config for {game_id!r} sub-game {sub_game}; Appendix F obligation "
            "4 requires it and the game cannot be reproduced without it")
    return json.loads(path.read_text(encoding="utf-8"))


def stored_games(root: Path) -> tuple[str, ...]:
    """Every `game_id` with at least one committed config."""
    base = Path(root) / COMMITTED_GAMES_DIR
    if not base.is_dir():
        return ()
    return tuple(sorted(entry.name for entry in base.iterdir() if entry.is_dir()))


def missing_configs(root: Path, game_id: str, sub_games: Sequence[int]) -> tuple[int, ...]:
    """Which sub-games of a played series have no committed config.

    Returned rather than raised: this is the pre-submission question, and the useful answer
    is every gap at once. Stopping at the first turns one review into six.
    """
    directory = game_directory(root, game_id)
    return tuple(n for n in sub_games
                 if not (directory / config_filename(game_id, n)).is_file())
