"""Tests for the behavior-free CLI."""

import pytest

from p2p_cop_agent.cli import main


def test_cli_without_arguments_shows_scaffold_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Keep the default command informative without starting a runtime."""
    assert main([]) == 0
    output = capsys.readouterr().out
    assert "runtime behavior is not implemented" in output


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
