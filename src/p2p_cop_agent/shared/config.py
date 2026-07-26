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


def load_json_object(path: str | Path) -> JsonObject:
    """Load one explicit path as a JSON object without supplying defaults."""
    config_path = Path(path)
    try:
        with config_path.open(encoding="utf-8") as stream:
            value: object = json.load(stream, object_pairs_hook=_object_without_duplicates)
    except ConfigLoadError:
        raise
    except (OSError, JSONDecodeError) as exc:
        raise ConfigLoadError(f"Cannot load JSON configuration {config_path}: {exc}") from exc

    if not isinstance(value, dict):
        raise ConfigLoadError(f"JSON configuration {config_path} must contain an object")
    return value
