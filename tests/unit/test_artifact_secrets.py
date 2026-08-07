"""`M8-09a` / `M8-09c`: nothing secret leaves in an artifact, and the lockfile is the truth.

Rule 39 (Prohibited): "Do not push secrets and credentials to the repository, **even if it
is private and shared only with the lecturer**. Sanction: severe security failure and
project failure." Rule 40 (Mandatory): credential files go in `.gitignore`.

`scripts/check_secrets.py` already scans the tree, and that is the right first line. It is
not sufficient here, because the four artifacts are **generated at runtime and then shared
with an opponent and emailed to the lecturer**. A secret that reaches one of them never sits
in the repository at all — the scanner would pass, the file would leave the machine, and the
sanction is project failure.

So this builds each artifact the way the pipeline builds it and inspects the *product*.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import tomllib

from p2p_cop_agent.protocol.declaration import build_declaration
from p2p_cop_agent.reporting import MatchIdentity, build_config, build_result
from p2p_cop_agent.reporting.log_artifact import build_log

ROOT = Path(__file__).resolve().parents[2]
GAME = json.loads((ROOT / "shared_contract" / "fixtures" / "match_config.example.json")
                  .read_text("utf-8"))
IDENT = MatchIdentity("secret-scan", "d" * 32)

# Shapes a credential takes. Deliberately broader than the repository scanner's, because an
# artifact is a small document and a false positive here costs one look.
SECRET_SHAPES = (
    (r"(?i)\bsk-[A-Za-z0-9]{16,}", "an OpenAI-style API key"),
    (r"(?i)\bAIza[0-9A-Za-z_\-]{20,}", "a Google API key"),
    (r"(?i)\bghp_[A-Za-z0-9]{20,}", "a GitHub token"),
    (r"(?i)\b(client_secret|refresh_token|access_token|private_key)\b", "a credential field"),
    (r"(?i)\bBEGIN [A-Z ]*PRIVATE KEY\b", "an embedded private key"),
    (r"(?i)://[^/\s:@]+:[^/\s:@]+@", "credentials embedded in a URL"),
    (r"(?i)\b(password|passwd|api[_-]?key)\s*[:=]", "an inline password or key"),
)

GROUPS = [{"group_id": "sharNamr", "repos": {"cop": "https://x/1", "thief": "https://x/2"}},
          {"group_id": "opponent", "repos": {"cop": "https://x/3", "thief": "https://x/4"}}]


def _identity(group_id: str) -> dict:
    """An identity block as the handshake produces one — including the fields most likely
    to carry a leak: repository URLs, an MCP endpoint and a model name."""
    return {
        "group_id": group_id,
        "group_name": group_id,
        "repos": {"cop": f"https://github.com/{group_id}/cop",
                  "thief": f"https://github.com/{group_id}/thief"},
        "links": {"agent": f"https://example.com/{group_id}/agent",
                  "report": f"https://example.com/{group_id}/report"},
        "mcp_servers": {"peer": f"https://{group_id}.example.com/mcp"},
        "llm_model": "template-free",
        "spec": {"os": "Windows 11", "cpu_type": "x86_64", "cpu_freq_mhz": 3600, "cpu_cores": 8, "ram_gb": 31.8, "gpu_model": "RTX 3060", "vram_gb": 6.0},
    }


def _artifacts() -> dict[str, object]:
    """One of each of the four artifact families, built by the real builders."""
    records = [{"step": 1, "sender": "police", "commit": "a" * 64, "move": "N",
                "hint": "closing in from the north", "intent": True}]
    return {
        "declaration": build_declaration(
            game_id=IDENT.game_id, game_uid=IDENT.game_uid,
            our_identity=_identity("sharNamr"), opponent_identity=_identity("opponent"),
            config_sha256="c" * 64, num_sub_games=6, max_tokens_per_game=200_000,
            github_commit="a" * 40,
            games_played_declaration={"opponent_group_id": "rival", "games_played_including_this": 1},
            started_at="2026-08-07T10:00:00Z"),
        "config": build_config(identity=IDENT, sub_game=1, game=GAME,
                               config_sha256="b" * 64),
        "log": build_log(identity=IDENT, sub_game=1, records=records,
                         summary={"ended_at": "2026-08-07T12:00:00+03:00", "outcome": "capture", "turns": 1}),
    }


@pytest.mark.parametrize("name", ["declaration", "config", "log"])
def test_no_built_artifact_contains_anything_shaped_like_a_secret(name: str) -> None:
    """**The check the repository scanner cannot make.** These documents are generated,
    then shared with an opponent and attached to an email — a secret reaching one of them
    leaves the machine without ever being committed."""
    text = json.dumps(_artifacts()[name], ensure_ascii=False)
    for pattern, description in SECRET_SHAPES:
        assert not re.search(pattern, text), f"{name} artifact appears to carry {description}"


def test_the_result_artifact_is_scanned_too() -> None:
    """Built separately because it needs a settled agreement, and it is the one that gets
    emailed — so it is the artifact a leak would travel furthest in."""
    result = build_result(
        identity=IDENT, groups=GROUPS,
        sub_games=[{"sub_game": 1, "role": "police", "outcome": "capture",
                    "cop_score": 20, "thief_score": 5, "tokens": 10}],
        commit_hash="abc1234", mutual_agreement={"agreed": True, "state": "AGREED"})
    text = json.dumps(result, ensure_ascii=False)
    for pattern, description in SECRET_SHAPES:
        assert not re.search(pattern, text), f"result artifact appears to carry {description}"


def test_the_scan_is_not_vacuous_because_the_patterns_do_match_a_real_shape() -> None:
    """A scanner that matches nothing passes everything. Proven against a synthetic value
    that is not a credential and never reaches a file."""
    planted = json.dumps({"note": "sk-" + "A" * 24})
    assert any(re.search(pattern, planted) for pattern, _ in SECRET_SHAPES)


def test_no_artifact_carries_a_field_named_for_a_secret() -> None:
    """Shape-matching catches a value; this catches an empty or placeholder field, which is
    how a credential arrives in a template before anyone fills it in."""
    forbidden = {"token", "secret", "credential", "credentials", "api_key", "apikey",
                 "password", "private_key", "client_secret", "refresh_token"}
    for name, artifact in _artifacts().items():
        keys = set(re.findall(r'"([^"]+)":', json.dumps(artifact)))
        assert not (keys & forbidden), f"{name} carries {sorted(keys & forbidden)}"


# --- M8-09c: the lockfile is authoritative ----------------------------------------------


def test_the_lockfile_exists_and_is_the_authority() -> None:
    """`G§8.4`: `uv.lock` is authoritative. A repository that resolves dependencies fresh
    on the grader's machine is a repository whose test results are not the ones we ran."""
    assert (ROOT / "uv.lock").exists(), "uv.lock is missing; dependencies are unpinned"


def test_every_runtime_dependency_carries_a_lower_bound() -> None:
    """An unbounded `>=`-free dependency resolves to whatever exists on the day. Named
    bounds are what make `uv sync --frozen` mean the same thing next month."""
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))
    loose = [d for d in pyproject["project"].get("dependencies", [])
             if not re.search(r"[<>=~^]", d)]
    assert not loose, f"unpinned dependencies: {loose}"


def test_the_gitignore_covers_every_credential_filename_rule_40_names() -> None:
    """Rule 40 (Mandatory). Checked here as well as by the secret scanner because the
    scanner proves no secret is *present*; this proves one could not be *added* silently."""
    ignored = (ROOT / ".gitignore").read_text("utf-8")
    for pattern in ("credentials.json", "token.json", ".env"):
        assert pattern in ignored, f".gitignore does not cover {pattern} [AE-40]"
