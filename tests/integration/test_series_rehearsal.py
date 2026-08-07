"""`M7-20`: a full six-sub-game rehearsal, including the two ways it goes wrong.

A clean end-to-end run already exists (`M7-07`). It proves the pieces fit. It proves
nothing about the states the rules attach sanctions to, and those are the expensive ones:

* **`M7-20a` — a technical loss.** "A technical loss still produces a complete artifact
  set." A sub-game that ends badly is exactly when the evidence matters most, and exactly
  when a pipeline that only works on the happy path stops producing it.
* **`M7-20b` — a tampered audit.** "Detection, scoring, and reporting all behave." Rule 19
  scores 0 for **the falsifying group**; rule 35 scores 0 for **both** if we then file a
  contradicting report. Detecting the forgery and *not* reporting are two separate
  behaviours and both have to hold.

Run against the `X-06`-corrected shapes. Rehearsing before that would have produced a green
result that made the wrong artifact shape look settled.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from p2p_cop_agent.orchestration.series import (
    SUB_GAMES,
    Role,
    SubGameLine,
    run_series,
)
from p2p_cop_agent.orchestration.settlement import (
    agree,
    audit_series,
    require_reportable,
)
from p2p_cop_agent.protocol.commit import canonical_payload_bytes
from p2p_cop_agent.reporting import (
    MatchIdentity,
    build_config,
    build_result,
    config_filename,
    log_filename,
    validated_write,
    write_artifact,
)
from p2p_cop_agent.reporting.log_artifact import build_log, is_revealed, reveal_log

ROOT = Path(__file__).resolve().parents[2]
GAME = json.loads((ROOT / "shared_contract" / "fixtures" / "match_config.example.json").read_text("utf-8"))
IDENT = MatchIdentity("rehearsal", "e" * 32)
# The WIRE role vocabulary is `police`/`thief` (`OB-003`), while `series.Role` is an
# internal `cop`/`thief`. The rehearsal caught the difference by feeding a real audit
# payload through the real schema — `protocol.messages.require_wire_role` refuses `cop`.
# Worth the distinction: `Role` names which side we play, the wire names what a peer
# calls us, and only the latter is negotiable with an opponent.
WIRE_ROLE = "police"
GROUPS = [
    {"group_id": "sharNamr", "repos": {"cop": "https://x/1", "thief": "https://x/2"}},
    {"group_id": "opponent", "repos": {"cop": "https://x/3", "thief": "https://x/4"}},
]


def _sealed(step: int, move: str, nonce: str) -> tuple[dict, str]:
    payload = {"step": step, "move": move}
    commit = hashlib.sha256(canonical_payload_bytes(payload) + b"|" + nonce.encode()).hexdigest()
    return payload, commit


def _play_sub_game(directory: Path, sub_game: int, *, outcome: str, tamper: bool = False):
    """Emit one sub-game's config and log, and return its result line plus its reveal."""
    validated_write(
        directory, config_filename(IDENT, sub_game),
        build_config(identity=IDENT, sub_game=sub_game, game=GAME, config_sha256="a" * 64),
    )
    records, reveals = [], []
    for step in (1, 2):
        nonce = f"{sub_game}{step}".ljust(32, "0")
        payload, commit = _sealed(step, "N", nonce)
        records.append({"step": step, "sender": WIRE_ROLE, "commit": commit, "move": "N",
                        "hint": "near the north edge", "intent": True})
        revealed = {**payload, "move": "S"} if (tamper and step == 2) else payload
        reveals.append({"step": step, "nonce": nonce, "payload": revealed})

    log = build_log(identity=IDENT, sub_game=sub_game, records=records,
                    summary={"ended_at": "2026-08-07T12:00:00+03:00", "outcome": outcome, "turns": 2})
    assert not is_revealed(log), "the in-play log must not carry a nonce"
    revealed_log = reveal_log(log, reveals)
    write_artifact(directory, log_filename(IDENT, sub_game), revealed_log)

    scores = {"capture": (20, 5), "survival": (5, 10), "technical_loss": (0, 0)}[outcome]
    line = SubGameLine(sub_game, Role.COP, outcome, scores[0], scores[1], 10)
    return line, {"sub_game": sub_game, "payload": {"sender": WIRE_ROLE, "records": revealed_log["records"],
                                                    "result_claim": "capture"}}


def test_a_clean_six_sub_game_series_emits_a_consistent_set(tmp_path: Path) -> None:
    """The baseline the two failure rehearsals are measured against."""
    reveals = []

    def play(sub_game: int, role: Role) -> SubGameLine:
        line, reveal = _play_sub_game(tmp_path, sub_game, outcome="capture")
        reveals.append(reveal)
        return line

    result = run_series(IDENT, Role.COP, play)
    assert result.complete and len(list(tmp_path.iterdir())) == 2 * SUB_GAMES

    settled = agree(audit_series(reveals), "capture", "capture")
    require_reportable(settled)
    report = build_result(identity=IDENT, groups=GROUPS,
                          sub_games=[line.as_result_line() for line in result.lines],
                          commit_hash="abc1234", mutual_agreement=settled)
    assert report["final_result"]["cop_score"] == 20 * SUB_GAMES


def test_a_technical_loss_still_produces_its_artifacts(tmp_path: Path) -> None:
    """`M7-20a`. The sub-game that goes wrong is when the evidence matters most — and when
    a pipeline that only works on the happy path quietly stops producing it."""
    reveals = []

    def play(sub_game: int, role: Role) -> SubGameLine:
        outcome = "technical_loss" if sub_game == 3 else "capture"
        line, reveal = _play_sub_game(tmp_path, sub_game, outcome=outcome)
        reveals.append(reveal)
        return line

    result = run_series(IDENT, Role.COP, play)

    assert (tmp_path / config_filename(IDENT, 3)).exists()
    assert (tmp_path / log_filename(IDENT, 3)).exists()
    lost = json.loads((tmp_path / log_filename(IDENT, 3)).read_text("utf-8"))
    assert lost["summary"]["outcome"] == "technical_loss"
    assert len(list(tmp_path.iterdir())) == 2 * SUB_GAMES, "a bad sub-game must not skip a file"

    # 0/0 for that sub-game, and the series still settles and reports.
    assert result.lines[2].cop_score == 0 and result.lines[2].thief_score == 0
    settled = agree(audit_series(reveals), "capture", "capture")
    report = build_result(identity=IDENT, groups=GROUPS,
                          sub_games=[line.as_result_line() for line in result.lines],
                          commit_hash="abc1234", mutual_agreement=settled)
    assert report["final_result"]["cop_score"] == 20 * (SUB_GAMES - 1)
