"""Scan repository text for common committed-secret patterns."""

import os
import re
from pathlib import Path
from re import Pattern

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".uv-cache",
    ".venv",
    "__pycache__",
    "htmlcov",
}
TEXT_SUFFIXES = {".env", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
DUMMY_MARKERS = (
    "abc123",
    "dummy",
    "example",
    "optional",
    "placeholder",
    "replace",
    "your-",
    "your_",
    "${",
    "<",
)
TOKEN_PATTERNS: dict[str, Pattern[str]] = {
    "private key": re.compile(r"-----BEGIN (?:EC |OPENSSH |RSA )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"(?:github_pat_|gh[pousr]_)[A-Za-z0-9_]{20,}"),
    "provider API key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b"),
}
ASSIGNMENT_PATTERN = re.compile(
    r"""(?ix)
    ["']?(?:api[_-]?key|auth[_-]?token|access[_-]?token|client[_-]?secret|password)["']?
    \s*[:=]\s*["']?([^"'#,\s]+)
    """
)


def candidate_files(root: Path) -> list[Path]:
    """Return scannable repository text files outside generated directories."""
    candidates: list[Path] = []
    for directory, directory_names, file_names in os.walk(root):
        directory_names[:] = [
            name
            for name in directory_names
            if name not in IGNORED_DIRECTORIES and not name.startswith(".venv")
        ]
        parent = Path(directory)
        for file_name in file_names:
            path = parent / file_name
            if path.name == ".env-example" or path.suffix.lower() in TEXT_SUFFIXES:
                candidates.append(path)
    return sorted(candidates)


def is_dummy(value: str) -> bool:
    """Return whether an assignment contains an obvious placeholder."""
    normalized = value.strip("'\"").lower()
    return not normalized or any(marker in normalized for marker in DUMMY_MARKERS)


def findings(path: Path, root: Path) -> list[str]:
    """Return line-level findings for one text file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    matches: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for label, pattern in TOKEN_PATTERNS.items():
            if pattern.search(line):
                matches.append(f"{path.relative_to(root)}:{line_number}: {label}")
        assignment = ASSIGNMENT_PATTERN.search(line)
        if assignment and not is_dummy(assignment.group(1)):
            matches.append(f"{path.relative_to(root)}:{line_number}: credential assignment")
    return matches


def scan(root: Path) -> list[str]:
    """Return all possible-secret findings under a repository root."""
    return [match for path in candidate_files(root) for match in findings(path, root)]


def main(root: Path = PROJECT_ROOT) -> int:
    """Scan repository text and fail when a plausible secret is present."""
    files = candidate_files(root)
    matches = [match for path in files for match in findings(path, root)]
    if matches:
        print("Possible secrets found:")
        print(*matches, sep="\n")
        return 1
    print(f"Secret scan OK: {len(files)} text files checked; 0 findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
