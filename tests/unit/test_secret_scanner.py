"""Tests for repository secret scanning."""

from pathlib import Path

import pytest

from scripts.check_secrets import main, scan


def test_secret_scan_accepts_documented_dummy_values(tmp_path: Path) -> None:
    """Allow obvious placeholders in the committed environment example."""
    example = tmp_path / ".env-example"
    example.write_text(
        "PROVIDER_API_KEY=<optional-provider-key>\n"
        "AUTH_TOKEN=${OPTIONAL_AUTH_TOKEN}\n"
        "PASSWORD=dummy-password\n",
        encoding="utf-8",
    )

    assert scan(tmp_path) == []
    assert main(tmp_path) == 0


@pytest.mark.parametrize(
    "secret",
    [
        "ghp_" + ("a" * 40),
        "AK" + "IA" + ("A" * 16),
        "sk-" + ("z" * 30),
        "-----BEGIN " + "PRIVATE KEY-----",
    ],
)
def test_secret_scan_rejects_representative_tokens(tmp_path: Path, secret: str) -> None:
    """Reject fake values with the shape of real credentials."""
    candidate = tmp_path / "settings.txt"
    candidate.write_text(secret, encoding="utf-8")

    assert scan(tmp_path)
    assert main(tmp_path) == 1


def test_secret_scan_rejects_non_dummy_assignment(tmp_path: Path) -> None:
    """Reject a generic credential assignment without naming a provider."""
    candidate = tmp_path / "settings.toml"
    label = "API" + "_KEY="
    candidate.write_text(label + "live-secret-value", encoding="utf-8")

    assert any("credential assignment" in item for item in scan(tmp_path))
