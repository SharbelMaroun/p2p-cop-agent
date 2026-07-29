"""Configuration loading boundary for the behavior-free SDK."""

import json
from json import JSONDecodeError
from pathlib import Path

JsonObject = dict[str, object]


class ConfigLoadError(ValueError):
    """Raised when a configuration file is not a JSON object."""


def _object_without_duplicates(pairs: list[tuple[str, object]]) -> JsonObject:
    """Build an object while rejecting ambiguous duplicate member names."""
    value: JsonObject = {}
    for key, item in pairs:
        if key in value:
            raise ConfigLoadError(f"Duplicate JSON member {key!r}")
        value[key] = item
    return value


def _reject_non_json_number(value: str) -> object:
    """Reject Python's non-standard NaN and infinity decoder extensions."""
    raise ConfigLoadError(f"Non-finite JSON number {value!r} is not allowed")


def load_json_object_with_bytes(path: str | Path) -> tuple[JsonObject, bytes]:
    """Load one explicit JSON-object path and return the exact parsed bytes."""
    config_path = Path(path)
    try:
        raw = config_path.read_bytes()
        text = raw.decode("utf-8")
        value: object = json.loads(
            text,
            object_pairs_hook=_object_without_duplicates,
            parse_constant=_reject_non_json_number,
        )
    except ConfigLoadError:
        raise
    except (OSError, UnicodeDecodeError, JSONDecodeError) as exc:
        raise ConfigLoadError(f"Cannot load JSON configuration {config_path}: {exc}") from exc

    if not isinstance(value, dict):
        raise ConfigLoadError(f"JSON configuration {config_path} must contain an object")
    return value, raw


def load_json_object(path: str | Path) -> JsonObject:
    """Load one explicit path as a JSON object without supplying defaults."""
    value, _raw = load_json_object_with_bytes(path)
    return value
