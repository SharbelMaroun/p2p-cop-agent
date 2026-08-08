"""Tests for the behavior-free CLI."""

import json
from pathlib import Path

import pytest

from p2p_cop_agent.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "replay"
PLAYED = Path(__file__).resolve().parents[2] / "games" / "game-593df753457f"


def test_cli_without_arguments_shows_help_without_serving(capsys: pytest.CaptureFixture[str]) -> None:
    """With no subcommand, show help and start no runtime; `serve` is advertised."""
    assert main([]) == 0
    assert "serve" in capsys.readouterr().out


def test_replay_of_a_played_match_prints_the_verified_banner(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`replay` reaches `Verified OK` on the committed match and exits 0 (rule 20)."""
    assert main(["replay", "--log", str(PLAYED / "log_game-593df753457f_g01.json")]) == 0
    printed = capsys.readouterr().out
    assert "Verified OK" in printed
    assert "TAMPERED" not in printed


def test_verify_exits_non_zero_on_a_tampered_log_and_says_nothing(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The gate form is the point: a script must be able to *fail* on forgery (rule 19)."""
    assert main(["verify", "--log", str(FIXTURES / "log_tampered.json")]) == 1
    assert capsys.readouterr().out == ""


def test_verify_accepts_a_log_this_repository_did_not_write() -> None:
    """The opponent's revealed log verifies too -- rule 36's audit is mutual."""
    assert main(["verify", "--log", str(PLAYED / "log_game-593df753457f_g01.opponent.json")]) == 0


def test_an_unreadable_log_is_not_reported_as_tampering(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """**Exit 2, not 1.** Rule 19 has no appeal, so a missing or malformed file must never
    be scored as forgery -- that would be a false accusation with a fatal sanction."""
    assert main(["verify", "--log", str(tmp_path / "absent.json")]) == 2
    malformed = tmp_path / "malformed.json"
    malformed.write_text(json.dumps({"not": "a log"}), encoding="utf-8")
    assert main(["verify", "--log", str(malformed)]) == 2
    assert "cannot replay" in capsys.readouterr().out


def test_cli_help_exits_successfully(capsys: pytest.CaptureFixture[str]) -> None:
    """Provide standard command help."""
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])

    assert exit_info.value.code == 0
    assert "usage: p2p-cop" in capsys.readouterr().out


def test_cli_version_uses_public_code_version(capsys: pytest.CaptureFixture[str]) -> None:
    """Report the single-sourced code version."""
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == "p2p-cop 1.00"
