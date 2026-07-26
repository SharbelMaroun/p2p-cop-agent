"""Source-file loading and validation for the proposed shared contract."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from pathlib import Path

from jsonschema import ValidationError
from jsonschema.validators import validator_for

from p2p_cop_agent.shared.config import JsonObject, load_json_object


class ContractValidationError(ValueError):
    """Raised when proposed contract files are missing or incompatible."""


@dataclass(frozen=True, slots=True)
class SharedContract:
    """Validated shared configuration loaded entirely from repository files."""

    version: str
    game: JsonObject
    rate_limits: JsonObject
    config_sha256: str


def canonical_config_bytes(config: JsonObject) -> bytes:
    """Return the defined sorted, compact, unescaped-Unicode UTF-8 config bytes."""
    try:
        text = json.dumps(
            config,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ContractValidationError(f"Cannot canonicalize shared config: {exc}") from exc
    return text.encode("utf-8")


def shared_config_sha256(config: JsonObject) -> str:
    """Hash the complete shared source config; the artifact claim is external."""
    return hashlib.sha256(canonical_config_bytes(config)).hexdigest()


def verify_config_sha256(config: JsonObject, claimed: object) -> None:
    """Reject malformed or incorrect config-artifact hash claims."""
    if not isinstance(claimed, str) or re.fullmatch(r"[0-9a-f]{64}", claimed) is None:
        raise ContractValidationError("config_sha256 must be 64 lowercase hexadecimal digits")
    expected = shared_config_sha256(config)
    if not hmac.compare_digest(expected, claimed):
        raise ContractValidationError("config_sha256 does not match the shared config")


def _read_version(root: Path) -> str:
    path = root / "docs/contracts/CONTRACT_VERSION"
    try:
        version = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ContractValidationError(f"Cannot load contract version {path}: {exc}") from exc
    if not version:
        raise ContractValidationError("Contract version must not be empty")
    return version


def _load_schema(root: Path, filename: str) -> JsonObject:
    return load_json_object(root / "docs/schemas" / filename)


def validate_instance(instance: object, schema: JsonObject, label: str) -> None:
    """Validate one instance and translate library errors into a stable boundary."""
    validator_class = validator_for(schema)
    validator_class.check_schema(schema)
    errors = sorted(validator_class(schema).iter_errors(instance), key=lambda item: item.json_path)
    if errors:
        error: ValidationError = errors[0]
        raise ContractValidationError(f"{label} {error.json_path}: {error.message}")


def _check_profile(version: str, schemas: list[JsonObject]) -> None:
    profiles = {schema.get("x-contract-version") for schema in schemas}
    if profiles != {version}:
        shown = ", ".join(sorted(str(item) for item in profiles))
        raise ContractValidationError(
            f"Unsupported contract version {version!r}; schema profiles are {shown}"
        )


def _check_rate_limit_mirror(game: JsonObject, rate_limits: JsonObject) -> None:
    """Require the operational file to mirror signed Gatekeeper terms exactly."""
    if game.get("rate_limiter_gatekeeper") != rate_limits.get("rate_limiter_gatekeeper"):
        raise ContractValidationError("rate-limit mirror differs from shared game configuration")


def require_same_match_configuration(
    expected: SharedContract,
    offered: SharedContract,
) -> None:
    """Reject an offer whose validated match terms differ semantically."""
    if expected.version != offered.version:
        raise ContractValidationError("match contract version differs")
    if expected.game != offered.game:
        raise ContractValidationError("negotiated game configuration differs")
    if expected.rate_limits != offered.rate_limits:
        raise ContractValidationError("negotiated rate-limit configuration differs")
    if expected.config_sha256 != offered.config_sha256:
        raise ContractValidationError("shared configuration hash differs")


def load_shared_contract(root: str | Path) -> SharedContract:
    """Load and validate shared game and Gatekeeper files from one repository root."""
    repository = Path(root)
    version = _read_version(repository)
    game_schema = _load_schema(repository, "game-config.schema.json")
    rate_schema = _load_schema(repository, "rate-limits.schema.json")
    _check_profile(version, [game_schema, rate_schema])
    game = load_json_object(repository / "config/game.json")
    rate_limits = load_json_object(repository / "config/rate_limits.json")
    validate_instance(game, game_schema, "game config")
    validate_instance(rate_limits, rate_schema, "rate-limit config")
    _check_rate_limit_mirror(game, rate_limits)
    return SharedContract(
        version=version,
        game=game,
        rate_limits=rate_limits,
        config_sha256=shared_config_sha256(game),
    )


def load_artifact_keysets(root: str | Path) -> dict[str, JsonObject]:
    """Load all safe key-set snapshots and validate only their descriptor format."""
    repository = Path(root)
    version = _read_version(repository)
    schema = _load_schema(repository, "artifact-keyset-fixture.schema.json")
    _check_profile(version, [schema])
    fixtures: dict[str, JsonObject] = {}
    directory = repository / "tests/fixtures/contracts"
    for path in sorted(directory.glob("*.keyset.json")):
        fixture = load_json_object(path)
        validate_instance(fixture, schema, path.name)
        family = fixture["artifact_family"]
        if not isinstance(family, str):
            raise ContractValidationError(f"{path.name} artifact_family must be text")
        if family in fixtures:
            raise ContractValidationError(f"duplicate artifact family: {family}")
        fixtures[family] = fixture
    expected = set(schema["properties"]["artifact_family"]["enum"])  # type: ignore[index]
    missing = sorted(expected - set(fixtures))
    if missing:
        raise ContractValidationError(f"missing artifact key-set fixtures: {', '.join(missing)}")
    return fixtures
