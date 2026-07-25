"""Source-file loading and validation for the proposed shared contract."""

from __future__ import annotations

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
    return SharedContract(version=version, game=game, rate_limits=rate_limits)


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
