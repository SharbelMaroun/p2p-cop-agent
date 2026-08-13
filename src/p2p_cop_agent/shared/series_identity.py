"""The one identifier that names every artifact in a series (`M7-02c`, Appendix F t20).

Its own module rather than a helper inside `adapters/serve.py` or
`shared/private_config.py`: both were already within a few lines of the 150-line gate,
and the reasoning below is the point of the change rather than decoration -- trimming it
to fit would delete the only record of why a hash-derived id is wrong. Split by
responsibility, as `M9-21` was.
"""

from __future__ import annotations

from collections.abc import Mapping


def series_game_id(config: Mapping[str, object]) -> str:
    """Return the agreed ``G00N`` label from the private config.

    Appendix F table 20 (p. 141/289) names all four artifacts from ``<game_id>``::

        declaration_<game_id>.json
        config_<game_id>_g<NN>.json
        log_<game_id>_g<NN>.json
        result_<game_id>.json

    and the book is explicit about where that value comes from: it is the label the two
    teams agree, or that league management assigns, and **not** a value derived from a
    hash of the configuration -- the hash locks the config under ``config_sha256`` and
    does nothing else. The reference implementation arrives at the same place by a
    different road, deriving a *human* id from the agreed terms plus both group ids
    (`domain/game_ids.py: derive_game_ids`), so both peers compute it without an extra
    round trip. Neither source supports naming artifacts from a config digest.

    **The defect this replaced.** ``derive_game_id(config_sha256)`` returned
    ``game-<12 hex>`` -- precisely the hash-derived form the book rules out. It survived
    the whole project because nothing cross-checks an artifact's *name* against the
    report that *points at* it: logs were written as ``log_game-5a7b4a6e58be_g01.json``
    while the result report, built from the agreed label, linked ``log_G005_g01.json``.
    Every local gate passed and every file was valid; only the links were unfollowable.
    Found 2026-08-13 by diffing our G005 report against `uoh-ay26`'s, whose set is
    self-consistent because they used the agreed label throughout.

    **Refuses rather than defaulting.** A missing label fails here, at launch, where it
    costs one restart. A guessed one fails at grading, where it cannot be fixed and where
    the symptom is a grader unable to open a single log.
    """
    game = config.get("game")
    label = ""
    if isinstance(game, Mapping):
        label = str(game.get("series_game_id") or "").strip()
    if not label:
        raise ValueError(
            "[game].series_game_id is required -- it names every artifact in the set "
            "(declaration_<id>.json, config_<id>_gNN.json, log_<id>_gNN.json, "
            "result_<id>.json). Agree the G00N label with the opponent and set it in the "
            "private game.toml. It is never derived from the config hash."
        )
    return label
