"""Tests for Step-0 host and code attestation sealed before play (M4-06)."""

import subprocess
from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.protocol import (
    AttestationError,
    HostSpec,
    build_step_zero,
    running_git_commit,
    seal_step_zero,
    verify_attestation,
)
from tests.conformance import neutral_stub

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"

GIT_COMMIT = "0" * 40
CONFIG_SHA = "a" * 64
NONCE = "1234567890abcdef1234567890abcdef"


def host() -> HostSpec:
    """Return a valid hardware declaration."""
    return HostSpec(os="Windows 11", cpu_type="Ryzen 9", cpu_freq_mhz=3600, cpu_cores=8, ram_gb=64, gpu_model="RTX 4090", vram_gb=24)


def declaration(git_commit: str = GIT_COMMIT) -> dict:
    """Return a valid Step-0 declaration payload."""
    return build_step_zero(
        host=host(),
        model="claude-opus-4-8",
        group_id="team-cop",
        game_id="game-001",
        git_commit=git_commit,
        config_sha256=CONFIG_SHA,
    )


def test_build_step_zero_seals_all_required_evidence() -> None:
    payload = declaration()
    assert payload["code"]["git_commit"] == GIT_COMMIT
    assert payload["game"] == {"game_id": "game-001", "config_sha256": CONFIG_SHA}
    assert payload["group"]["group_id"] == "team-cop"
    assert set(payload["host"]) == {"os", "cpu_type", "cpu_freq_mhz", "cpu_cores",
                                    "ram_gb", "gpu_model", "vram_gb"}
    assert payload["model"] == "claude-opus-4-8"


@pytest.mark.parametrize("bad_commit", ["deadbeef", "g" * 40, "", "0" * 39])
def test_git_commit_must_be_forty_hex(bad_commit: str) -> None:
    with pytest.raises(AttestationError, match="git_commit"):
        declaration(git_commit=bad_commit)


def test_bad_config_digest_is_rejected() -> None:
    with pytest.raises(AttestationError, match="config_sha256"):
        build_step_zero(
            host=host(), model="m", group_id="g", game_id="x",
            git_commit=GIT_COMMIT, config_sha256="short",
        )


@pytest.mark.parametrize("field", ["model", "group_id", "game_id"])
def test_empty_identity_fields_are_rejected(field: str) -> None:
    args = {"host": host(), "model": "m", "group_id": "g", "game_id": "x",
            "git_commit": GIT_COMMIT, "config_sha256": CONFIG_SHA}
    args[field] = ""
    with pytest.raises(AttestationError):
        build_step_zero(**args)


def test_non_positive_hardware_values_are_rejected() -> None:
    with pytest.raises(AttestationError, match="ram_gb"):
        HostSpec(os="o", cpu_type="c", cpu_freq_mhz=3600, cpu_cores=8, ram_gb=0, gpu_model="g", vram_gb=8).as_dict()


def test_empty_host_string_is_rejected() -> None:
    with pytest.raises(AttestationError, match="host os"):
        HostSpec(os="", cpu_type="c", cpu_freq_mhz=3600, cpu_cores=8, ram_gb=8, gpu_model="g", vram_gb=8).as_dict()


def test_non_hex_git_output_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Result:
        stdout = "not-a-sha\n"

    monkeypatch.setattr(
        "p2p_cop_agent.protocol.attestation.subprocess.run",
        lambda *args, **kwargs: _Result(),
    )
    with pytest.raises(AttestationError, match="unexpected Git commit"):
        running_git_commit()


def test_seal_is_reproducible_and_verifies() -> None:
    sealed = seal_step_zero(declaration(), nonce=NONCE)
    assert sealed.commit == seal_step_zero(declaration(), nonce=NONCE).commit
    assert verify_attestation(sealed) is True


def test_tampered_declaration_fails_verification() -> None:
    sealed = seal_step_zero(declaration(), nonce=NONCE)
    forged = seal_step_zero(declaration(git_commit="1" * 40), nonce=NONCE)
    assert forged.commit != sealed.commit  # a different running commit changes the seal
    tampered = type(sealed)(payload=forged.payload, nonce=sealed.nonce, commit=sealed.commit)
    assert verify_attestation(tampered) is False


def test_independent_peer_reproduces_the_seal() -> None:
    # The neutral stub shares no runtime code yet reproduces the Step-0 commit,
    # which is the signed payload's independent verification vector.
    sealed = seal_step_zero(declaration(), nonce=NONCE)
    assert neutral_stub.commit(sealed.payload, sealed.nonce) == sealed.commit


def test_running_git_commit_matches_head() -> None:
    expected = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert running_git_commit(PROJECT_ROOT) == expected


def test_running_git_commit_reports_a_clear_error_off_a_repo(tmp_path: Path) -> None:
    with pytest.raises(AttestationError):
        running_git_commit(tmp_path)


def test_sdk_seals_step_zero_binding_config_and_running_commit() -> None:
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    sealed = sdk.seal_step_zero_attestation(
        host=host(), model="claude-opus-4-8", group_id="team-cop",
        game_id="game-001", git_commit=GIT_COMMIT, nonce=NONCE,
    )
    assert sealed.payload["game"]["config_sha256"] == sdk.config_sha256
    assert sealed.payload["code"]["git_commit"] == GIT_COMMIT
    assert verify_attestation(sealed) is True


def test_sdk_defaults_to_the_real_running_commit() -> None:
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    sealed = sdk.seal_step_zero_attestation(
        host=host(), model="m", group_id="g", game_id="x",
    )
    assert sealed.payload["code"]["git_commit"] == running_git_commit(PROJECT_ROOT)
