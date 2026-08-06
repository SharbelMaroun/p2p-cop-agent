"""The four artifact filenames, fixed by the book (`M7-02c`).

`inst/police_thief_p2p_Summary.md:3600` names all four and they are not ours to choose:

| Artifact | Filename |
| --- | --- |
| Pre-game declaration | `declaration_<game_id>.json` |
| Agreed configuration | `config_<game_id>_g<NN>.json` |
| Game log | `log_<game_id>_g<NN>.json` |
| Results report | `result_<game_id>.json` |

Two are per-**series** and two per-**sub-game**, which is the whole reason this module
exists rather than an f-string at each call site: getting that split wrong produces a
plausible-looking set whose config and log describe different sub-games.

`<NN>` is zero-padded to two digits so six sub-games sort correctly as text — an auditor
listing a directory should see `g01…g06` in order, not `g1, g2` interleaved with `g10`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# A game_id becomes part of a filename, so it may not carry a path separator, a parent
# reference, or anything a filesystem would interpret. This is the one place a value
# negotiated with an opponent turns into a path.
_SAFE_GAME_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")


class NamingError(ValueError):
    """Raised when an identity cannot safely produce artifact filenames."""


@dataclass(frozen=True, slots=True)
class MatchIdentity:
    """The one identity every artifact in a set must share (`M7-02c`).

    Both members are validated here rather than at each artifact, so a mismatched set
    cannot be produced in the first place — `M7-14e` refuses one after the fact, but the
    cheaper guarantee is that the builders were never able to disagree.
    """

    game_id: str
    game_uid: str

    def __post_init__(self) -> None:
        if not isinstance(self.game_id, str) or _SAFE_GAME_ID.fullmatch(self.game_id) is None:
            raise NamingError(
                f"game_id {self.game_id!r} is not filename-safe; it becomes part of a path"
            )
        if not isinstance(self.game_uid, str) or not self.game_uid:
            raise NamingError("game_uid must be a non-empty string")


def _sub_game(number: object) -> str:
    if isinstance(number, bool) or not isinstance(number, int) or not 1 <= number <= 99:
        raise NamingError(f"sub-game number must be an integer in 1..99, got {number!r}")
    return f"g{number:02d}"


def declaration_filename(identity: MatchIdentity) -> str:
    """Per **series** — one declaration covers every sub-game."""
    return f"declaration_{identity.game_id}.json"


def result_filename(identity: MatchIdentity) -> str:
    """Per **series** — the emailed report carries the cumulative result."""
    return f"result_{identity.game_id}.json"


def config_filename(identity: MatchIdentity, sub_game: int) -> str:
    """Per **sub-game** — each sub-game has its own agreed configuration."""
    return f"config_{identity.game_id}_{_sub_game(sub_game)}.json"


def log_filename(identity: MatchIdentity, sub_game: int) -> str:
    """Per **sub-game** — each sub-game has its own commit-reveal record."""
    return f"log_{identity.game_id}_{_sub_game(sub_game)}.json"


def match_filenames(identity: MatchIdentity, sub_games: tuple[int, ...]) -> dict[str, str]:
    """Return every filename in one series, keyed for an auditor's directory listing."""
    names = {
        "declaration": declaration_filename(identity),
        "result": result_filename(identity),
    }
    for number in sub_games:
        names[f"config_g{number:02d}"] = config_filename(identity, number)
        names[f"log_g{number:02d}"] = log_filename(identity, number)
    return names
