"""`M7-14a`/`M7-14c`/`M7-14d`/`M7-26`: schemas that assert only what the book asserts.

The Cop validates artifacts with JSON Schema where the companion Thief uses a citation
table. Both are pinned as correct for their own repository — but a schema carries a risk the
table does not, and this repository has already paid it. **`X-04`**: the per-sub-game config
schema pinned the literal pattern `g<NN>`, so it validated a *template* and refused every
real artifact. A schema is only as honest as its `required` list.

So the two properties tested hardest here are the two that keep it honest:

* **`additionalProperties` is `true` on the reporting artifacts.** The book was asked
  directly and is `NOT-SPECIFIED` on whether extra non-contradicting fields are forbidden
  there. Refusing an opponent's declaration over a key no source forbids would fail the very
  audit rule 36 requires. The **config** is the exception, and deliberately so: p.111/243
  says it must hold "only items the parties must agree on", and an unagreed field means a
  refusal to play (p.140/288).
* **Every schema declares the same `x-contract-version`.** `X-04` shipped because a bundle
  bump edited some declarations and not others. The guard caught exactly that on its first
  run — `per-subgame-config` was still `0.2.9` while the three new schemas were `0.2.10`.
"""

from __future__ import annotations

import json

import pytest

from p2p_cop_agent.reporting.validate import (
    BUNDLE_SCHEMAS,
    SCHEMA_FILES,
    ArtifactInvalidError,
    validate_artifact,
)

REPORTING_KINDS = ("declaration", "log", "result")
SHA = "a" * 40


def schema(kind: str) -> dict:
    return json.loads((BUNDLE_SCHEMAS / SCHEMA_FILES[kind]).read_text("utf-8"))


def declaration() -> dict:
    group = {
        "group_id": "sharNamr", "group_name": "sharNamr", "members": ["s1", "s2"],
        "repos": {"cop": "https://x/1", "thief": "https://x/2"},
        "mcp_servers": {"peer": "https://x.example.com/mcp"},
        "llm_model": "template-free",
        "hardware_spec": {"os": "Windows 11", "cpu_type": "x86_64", "cpu_freq_mhz": 3600,
                          "cpu_cores": 8, "ram_gb": 16, "gpu_model": "none", "vram_gb": 0},
        "signature": "0" * 64,
    }
    return {"_schema": "declaration", "groups": [group, {**group, "group_id": "rival"}],
            # `M7-02`: resolved filenames, never the `g<NN>` pattern the book's naming table
            # writes. A placeholder here names no file that exists.
            "links": {"declaration": "declaration_g.json", "result": "result_g.json",
                      "config": ["config_g_g01.json"], "log": ["log_g_g01.json"]},
            "github_commit": SHA, "max_tokens_per_game": 200_000,
            "game_started_at": "t0", "game_ended_at": "t1",
            "games_played_declaration": {"opponent_group_id": "rival",
                                         "games_played_including_this": 1}}


def log() -> dict:
    return {"_schema": "log", "game_id": "g", "game_uid": "u", "sub_game_number": 1,
            "records": [{"step": 1, "commit": "c" * 64, "move": "N", "intent": True,
                         "hint": "north", "nonce": "n" * 32}],
            "mutual_agreement": {"confirmed": True}}


def result() -> dict:
    group = {"group_id": "sharNamr", "repos": {"cop": "https://x/1", "thief": "https://x/2"}}
    return {"_schema": "result", "game_id": "g", "game_uid": "u",
            "groups": [group, {**group, "group_id": "rival"}],
            "sub_games": [{"sub_game_number": 1, "result": "capture", "score": 20,
                           "tokens": 0, "github_commit": SHA}],
            "final_result": {"total_score": 20, "tokens_total_series": 0},
            "mutual_agreement": {"confirmed": True}}


ARTIFACTS = {"declaration": declaration, "log": log, "result": result}


# --- the honesty properties ---------------------------------------------------------------


@pytest.mark.parametrize("kind", REPORTING_KINDS)
def test_a_reporting_schema_accepts_unknown_fields(kind: str) -> None:
    """**The property that keeps this from repeating `X-04`.** The book is NOT-SPECIFIED on
    extra fields in reporting artifacts, so refusing one would assert more than any source
    does — and would fail rule 36's mutual audit over a difference nothing forbids."""
    assert schema(kind)["additionalProperties"] is True
    validate_artifact({**ARTIFACTS[kind](), "some_future_key": 1})


def test_the_config_schema_is_the_deliberate_exception() -> None:
    """p.111/243: the config must hold "only items the parties must agree on", and a field
    added by one side without agreement means a refusal to play (p.140/288). The asymmetry
    is book-backed, not an oversight."""
    assert "per-subgame-config" in SCHEMA_FILES


@pytest.mark.parametrize("kind", REPORTING_KINDS)
def test_every_required_field_actually_bites(kind: str) -> None:
    """A `required` list nothing is checked against is documentation. Each entry is removed
    in turn and must be refused."""
    for field in schema(kind)["required"]:
        broken = {k: v for k, v in ARTIFACTS[kind]().items() if k != field}
        with pytest.raises(ArtifactInvalidError):
            validate_artifact(broken)


@pytest.mark.parametrize("kind", REPORTING_KINDS)
def test_the_real_shape_validates(kind: str) -> None:
    validate_artifact(ARTIFACTS[kind]())


# --- book-mandated fields that were missing --------------------------------------------------


def test_the_schema_requires_the_hardware_and_model_per_group() -> None:
    """Rule 24, per group since `M7-22f`. **This test asserted the opposite until
    2026-08-07**, reasoning that repeating an opponent's spec "would assert something it
    never measured" — but recording what a peer *declared* is not measuring it, and rule
    24's sanction is the **computational bonus**, an award comparing two machines that one
    machine's spec cannot express. `test_declaration_disclosure.py` carries the rest."""
    for missing in ("llm_model", "hardware_spec", "signature"):
        broken = declaration()
        broken["groups"] = [{k: v for k, v in g.items() if k != missing}
                            for g in broken["groups"]]
        with pytest.raises(ArtifactInvalidError, match=missing):
            validate_artifact(broken)


def test_the_declaration_requires_the_games_played_count() -> None:
    """Rule 37 (p.131/275) requires an accurate count declared at the start of each game;
    rule 38 makes a false one absolute disqualification of the project."""
    document = declaration()
    del document["games_played_declaration"]
    with pytest.raises(ArtifactInvalidError, match="games_played_declaration"):
        validate_artifact(document)


def test_a_sub_game_commit_of_unknown_is_refused() -> None:
    """The reference hard-codes `"unknown"` here — it satisfies every shape check and
    identifies nothing (`M9-09b`)."""
    document = result()
    document["sub_games"][0]["github_commit"] = "unknown"
    with pytest.raises(ArtifactInvalidError):
        validate_artifact(document)
