r"""`M7-02`: the declaration names files that exist, not the pattern they are named by.

Until 2026-08-07 `build_declaration` emitted the literal `g<NN>`:

    "config": "config_<game_id>_g<NN>.json"

The book's table at `inst/:3600-3602` writes the naming convention that way, and copying it
into the artifact conflated *how a name is formed* with *the name of a file that exists*.
`inst/:2243` is explicit that each name is derived from the `game_id` "so that files from
different games do not get mixed up" — which a placeholder cannot do.

**This is `X-04` seen from the other side.** That defect was fixed in the *schema*, which now
demands `_g\d{2}\.json`, and the **producer was left emitting the placeholder** — so the
contract became right while the artifact stayed wrong, and the declaration's own links would
have failed the pattern its own bundle publishes. Nothing noticed, because no test validated
the declaration against that pattern.

The last test here is the one that keeps it fixed: no emitted artifact may contain an angle
bracket anywhere. It is blunt on purpose — a pattern-specific check would miss the next
placeholder someone copies out of a table.
"""

from __future__ import annotations

import json

import pytest

from p2p_cop_agent.protocol.declaration import build_declaration
from p2p_cop_agent.reporting.validate import validate_artifact

SPEC = {"os": "Windows 11", "cpu_type": "x86_64", "cpu_cores": 8, "ram_gb": 16,
        "gpu_model": "none", "vram_gb": 0}


def identity(gid: str) -> dict:
    return {"group_id": gid, "group_name": gid, "members": ["s1"],
            "repos": {"cop": f"https://github.com/{gid}/cop",
                      "thief": f"https://github.com/{gid}/thief"},
            "mcp_servers": {"peer": f"https://{gid}.example.com/mcp"},
            "llm_model": "template-free", "spec": SPEC}


def declaration(sub_games: int = 6) -> dict:
    return build_declaration(
        game_id="sharNamr-vs-rival", game_uid="u" * 32,
        our_identity=identity("sharNamr"), opponent_identity=identity("rival"),
        config_sha256="a" * 64, num_sub_games=sub_games,
        github_commit="a" * 40,
        games_played_declaration={"opponent_group_id": "rival", "games_played_including_this": 1},
        max_tokens_per_game=200_000, started_at="2026-08-07T10:00:00+03:00")


def test_the_links_carry_no_placeholder() -> None:
    """**The regression this file exists for.** `g<NN>` names no file on disk."""
    links = declaration()["links"]
    assert "<NN>" not in json.dumps(links)


def test_one_config_and_one_log_per_sub_game() -> None:
    """A series has `num_sub_games` of each, not one. A single name could only ever be
    right for a one-sub-game series."""
    links = declaration(sub_games=6)["links"]
    assert len(links["config"]) == 6
    assert len(links["log"]) == 6
    assert links["config"][0].endswith("_g01.json")
    assert links["config"][5].endswith("_g06.json")


def test_the_declaration_and_result_are_one_each() -> None:
    """One declaration and one result cover the whole series, so these stay strings."""
    links = declaration()["links"]
    assert links["declaration"] == "declaration_sharNamr-vs-rival.json"
    assert links["result"] == "result_sharNamr-vs-rival.json"


def test_every_link_derives_from_the_game_id() -> None:
    """`inst/:2243`: names derive from the `game_id` so files from different games do not
    get mixed up."""
    for name in json.loads(json.dumps(declaration()["links"])).values():
        for value in ([name] if isinstance(name, str) else name):
            assert "sharNamr-vs-rival" in value


def test_the_declaration_validates_against_its_own_schema() -> None:
    """The check nobody was making. The old placeholder would have failed the very pattern
    this repository publishes."""
    validate_artifact(declaration())


def test_a_placeholder_link_is_refused_by_the_schema() -> None:
    """Proves the schema bites rather than merely describing. This is the exact artifact
    the builder produced until today."""
    broken = declaration()
    broken["links"]["config"] = "config_sharNamr-vs-rival_g<NN>.json"
    with pytest.raises(Exception, match="links"):
        validate_artifact(broken)


def test_no_emitted_artifact_contains_an_angle_bracket() -> None:
    """Blunt on purpose. A pattern-specific check would miss the next placeholder somebody
    copies out of a table in the book, and every one of those is a value that looks
    structured and refers to nothing."""
    assert "<" not in json.dumps(declaration())
