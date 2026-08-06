"""`X-06`: the artifact key names are the lecturer's templates', not ours.

Found by reading a notebook answer as **text** rather than from a screenshot — the code
notebook had already given the exact config roster, including `sub_game_number` and
`config_name`, and it went unregistered when read as pixels.

An auditor diffs our artifact against the template. A key that is merely *equivalent*
still reads as missing, and the companion Thief repository already had these right, so the
two repos were emitting different shapes for the same game.
"""

from __future__ import annotations

from p2p_cop_agent.reporting import build_config
from tests.unit.test_reporting_artifacts import GAME, IDENT, SHA, _artifact


def test_the_config_uses_the_templates_key_names() -> None:
    """`X-06`. An auditor diffs our artifact against the lecturer's template; a key that is
    merely *equivalent* still reads as missing. `inst/:3019` writes `sub_game_number` and
    `:2928` shows `"agreed_between": ["group-a", "group-b"]`."""
    artifact = _artifact()
    assert artifact["sub_game_number"] == 1
    assert "sub_game" not in artifact
    assert artifact["config_name"] == "config_demo-series_g01.json"
    assert "agreed_between" in artifact


def test_agreed_between_is_carried_from_the_negotiated_object_or_supplied() -> None:
    """Who agreed this configuration is not derivable from the game object's parameters."""
    named = build_config(identity=IDENT, sub_game=1, game=GAME, config_sha256=SHA,
                         agreed_between=["alpha", "beta"])
    assert named["agreed_between"] == ["alpha", "beta"]
    assert _artifact()["agreed_between"] == GAME["agreed_between"]
