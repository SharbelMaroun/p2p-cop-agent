"""Prove per-run contract inputs are explicit and independently validated."""

import hashlib
import json
from pathlib import Path

import pytest

from p2p_cop_agent import CopSDK
from p2p_cop_agent.shared.config import ConfigLoadError
from p2p_cop_agent.shared.contracts import ContractValidationError, load_match_contract

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
RATE_LIMITS = PROJECT_ROOT / "config" / "rate_limits.json"


def rate_config() -> dict:
    """Return a mutable copy of the repository's example local mirror."""
    return json.loads(RATE_LIMITS.read_text(encoding="utf-8"))


def write_rate_config(tmp_path: Path, config: object) -> Path:
    """Write a candidate per-run rate-limit mirror."""
    path = tmp_path / "rate-limits.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def test_loader_requires_an_explicit_match_path() -> None:
    with pytest.raises(TypeError, match="match_config_path"):
        load_match_contract(PROJECT_ROOT)  # type: ignore[call-arg]


def test_sdk_requires_an_explicit_match_path() -> None:
    with pytest.raises(TypeError, match="match_config_path"):
        CopSDK.from_repository(PROJECT_ROOT)  # type: ignore[call-arg]


def test_loader_requires_an_explicit_rate_limit_path() -> None:
    with pytest.raises(TypeError, match="rate_limits_path"):
        load_match_contract(PROJECT_ROOT, EXAMPLE)  # type: ignore[call-arg]


def test_sdk_requires_an_explicit_rate_limit_path() -> None:
    with pytest.raises(TypeError, match="rate_limits_path"):
        CopSDK.from_repository(PROJECT_ROOT, EXAMPLE)  # type: ignore[call-arg]


def test_offer_validation_requires_both_explicit_paths() -> None:
    sdk = CopSDK.from_repository(PROJECT_ROOT, EXAMPLE, rate_limits_path=RATE_LIMITS)
    with pytest.raises(TypeError, match="match_config_path"):
        sdk.validate_match_offer(PROJECT_ROOT)  # type: ignore[call-arg]
    with pytest.raises(TypeError, match="rate_limits_path"):
        sdk.validate_match_offer(PROJECT_ROOT, EXAMPLE)  # type: ignore[call-arg]


def test_explicit_rate_limit_file_is_loaded(tmp_path: Path) -> None:
    config = rate_config()
    config["extensions"] = {"local_queue_label": "match-42"}
    path = write_rate_config(tmp_path, config)

    contract = load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=path)

    assert contract.rate_limits["extensions"] == {"local_queue_label": "match-42"}


def test_explicit_mismatching_gatekeeper_is_rejected(tmp_path: Path) -> None:
    config = rate_config()
    config["rate_limiter_gatekeeper"]["requests_per_minute"] = 31
    path = write_rate_config(tmp_path, config)

    with pytest.raises(ContractValidationError, match="rate-limit mirror differs"):
        load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=path)


def test_missing_rate_limit_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigLoadError, match="Cannot load JSON configuration"):
        load_match_contract(
            PROJECT_ROOT,
            EXAMPLE,
            rate_limits_path=tmp_path / "missing.json",
        )


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("{", "Cannot load JSON configuration"),
        ("[]", "must contain an object"),
        ('{"version": "1.00", "version": "1.00"}', "Duplicate JSON member"),
    ],
)
def test_invalid_rate_limit_json_is_rejected(
    tmp_path: Path,
    raw: str,
    message: str,
) -> None:
    path = tmp_path / "rate-limits.json"
    path.write_text(raw, encoding="utf-8")

    with pytest.raises(ConfigLoadError, match=message):
        load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=path)


def test_schema_invalid_rate_limit_file_is_rejected(tmp_path: Path) -> None:
    config = rate_config()
    del config["extensions"]
    path = write_rate_config(tmp_path, config)

    with pytest.raises(ContractValidationError, match="rate-limit config"):
        load_match_contract(PROJECT_ROOT, EXAMPLE, rate_limits_path=path)


def test_match_hash_uses_the_same_bytes_that_were_parsed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = EXAMPLE.read_bytes()
    match_path = tmp_path / "match.json"
    match_path.write_bytes(original)
    read_bytes = Path.read_bytes

    def replace_after_read(path: Path) -> bytes:
        raw = read_bytes(path)
        if path == match_path:
            path.write_text("{}", encoding="utf-8")
        return raw

    monkeypatch.setattr(Path, "read_bytes", replace_after_read)
    contract = load_match_contract(PROJECT_ROOT, match_path, rate_limits_path=RATE_LIMITS)

    assert contract.game["version"] == "1.00"
    assert contract.config_file_sha256 == hashlib.sha256(original).hexdigest()
    assert match_path.read_text(encoding="utf-8") == "{}"
