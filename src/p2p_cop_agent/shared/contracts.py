"""Load and validate a per-match shared game object against the stable bundle.

The stable contract lives in the role-neutral ``shared_contract`` bundle. A match
configuration is supplied at runtime by an explicit path (defaulting to the bundle
example template) rather than a permanent in-repository match file. Three hash
domains are kept distinct: the canonical object ``config_sha256``, the exact-byte
``config_file_sha256``, and (elsewhere) the move/negotiation commitment.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from pathlib import Path

from jsonschema import ValidationError
from jsonschema.validators import validator_for

from p2p_cop_agent.domain.board import BoardError, validate_start_coordinates
from p2p_cop_agent.shared.config import JsonObject, load_json_object

BUNDLE_DIR = "shared_contract"
MATCH_SCHEMA = "schemas/match-config.schema.json"
EXAMPLE_MATCH_CONFIG = "fixtures/match_config.example.json"
RATE_LIMITS_SCHEMA = "config/rate_limits.schema.json"
RATE_LIMITS_CONFIG = "config/rate_limits.json"


class ContractValidationError(ValueError):
    """Raised when the match config or stable bundle is missing or incompatible."""


@dataclass(frozen=True, slots=True)
class SharedContract:
    """A validated per-match shared configuration and its two config hashes."""

    version: str
    game: JsonObject
    rate_limits: JsonObject
    config_sha256: str
    config_file_sha256: str


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
    """Hash the complete parsed match object; the artifact claim stays external."""
    return hashlib.sha256(canonical_config_bytes(config)).hexdigest()


def _file_sha256(path: Path) -> str:
    """Hash exact source bytes for the separate byte-identity rule."""
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ContractValidationError(f"Cannot hash match config {path}: {exc}") from exc
    return hashlib.sha256(raw).hexdigest()


def verify_config_sha256(config: JsonObject, claimed: object) -> None:
    """Reject malformed or incorrect config-artifact hash claims."""
    if not isinstance(claimed, str) or re.fullmatch(r"[0-9a-f]{64}", claimed) is None:
        raise ContractValidationError("config_sha256 must be 64 lowercase hexadecimal digits")
    expected = shared_config_sha256(config)
    if not hmac.compare_digest(expected, claimed):
        raise ContractValidationError("config_sha256 does not match the shared config")


def _read_version(root: Path) -> str:
    path = root / BUNDLE_DIR / "CONTRACT_VERSION"
    try:
        version = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ContractValidationError(f"Cannot load contract version {path}: {exc}") from exc
    if not version:
        raise ContractValidationError("Contract version must not be empty")
    return version


def validate_instance(instance: object, schema: JsonObject, label: str) -> None:
    """Validate one instance and translate library errors into a stable boundary."""
    validator_class = validator_for(schema)
    validator_class.check_schema(schema)
    errors = sorted(validator_class(schema).iter_errors(instance), key=lambda item: item.json_path)
    if errors:
        error: ValidationError = errors[0]
        raise ContractValidationError(f"{label} {error.json_path}: {error.message}")


def _check_profile(version: str, schema: JsonObject) -> None:
    profile = schema.get("x-contract-version")
    if profile != version:
        raise ContractValidationError(
            f"Unsupported contract version {version!r}; match schema profile is {profile!r}"
        )


def _check_start_coordinates(game: JsonObject) -> None:
    """Apply cross-field board validation that JSON Schema alone cannot express.

    Schema validation proves each coordinate is a well-formed integer pair. It
    cannot prove a pair lies inside the negotiated board, because that depends on
    ``grid_size`` and ``axis_start_index`` in a sibling object, nor that the two
    starts differ. Both are checked here against the negotiated geometry.
    """
    try:
        validate_start_coordinates(game)
    except BoardError as exc:
        raise ContractValidationError(f"match config board_and_agents: {exc}") from exc


def _check_rate_limit_mirror(game: JsonObject, rate_limits: JsonObject) -> None:
    """Require the local operational file to mirror signed Gatekeeper terms exactly."""
    if game.get("rate_limiter_gatekeeper") != rate_limits.get("rate_limiter_gatekeeper"):
        raise ContractValidationError("rate-limit mirror differs from shared match configuration")


def require_same_match_configuration(
    expected: SharedContract,
    offered: SharedContract,
) -> None:
    """Reject an offer whose validated match terms differ semantically."""
    if expected.version != offered.version:
        raise ContractValidationError("match contract version differs")
    if expected.game != offered.game:
        raise ContractValidationError("negotiated game configuration differs")
    if expected.config_sha256 != offered.config_sha256:
        raise ContractValidationError("shared configuration hash differs")
    if expected.config_file_sha256 != offered.config_file_sha256:
        raise ContractValidationError("shared match source bytes differ")


def load_match_contract(
    root: str | Path,
    match_config_path: str | Path | None = None,
) -> SharedContract:
    """Load and validate a per-match game object supplied by explicit path.

    ``match_config_path`` defaults to the role-neutral example template inside the
    stable bundle. A real match supplies its own path outside the stable bundle.
    """
    repository = Path(root)
    version = _read_version(repository)
    match_schema = load_json_object(repository / BUNDLE_DIR / MATCH_SCHEMA)
    _check_profile(version, match_schema)
    game_path = (
        Path(match_config_path)
        if match_config_path is not None
        else repository / BUNDLE_DIR / EXAMPLE_MATCH_CONFIG
    )
    game = load_json_object(game_path)
    validate_instance(game, match_schema, "match config")
    _check_start_coordinates(game)
    rate_schema = load_json_object(repository / RATE_LIMITS_SCHEMA)
    rate_limits = load_json_object(repository / RATE_LIMITS_CONFIG)
    validate_instance(rate_limits, rate_schema, "rate-limit config")
    _check_rate_limit_mirror(game, rate_limits)
    return SharedContract(
        version=version,
        game=game,
        rate_limits=rate_limits,
        config_sha256=shared_config_sha256(game),
        config_file_sha256=_file_sha256(game_path),
    )
