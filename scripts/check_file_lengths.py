"""Enforce the source and test file-size limits."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_LIMIT = 150
TEST_LIMIT = 150


def significant_line_count(path: Path) -> int:
    """Count nonblank physical lines that are not comment-only lines."""
    return sum(
        1
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def physical_line_count(path: Path) -> int:
    """Count every physical line in a test file."""
    return len(path.read_text(encoding="utf-8").splitlines())


def python_files(directory: Path) -> list[Path]:
    """Return Python files below an existing directory in stable order."""
    return sorted(directory.rglob("*.py")) if directory.exists() else []


def find_violations(root: Path) -> tuple[list[str], int, int]:
    """Return length violations and the number of files checked."""
    source_files = python_files(root / "src") + python_files(root / "scripts")
    test_files = python_files(root / "tests")
    violations: list[str] = []

    for path in source_files:
        count = significant_line_count(path)
        if count > SOURCE_LIMIT:
            relative = path.relative_to(root)
            violations.append(f"{relative}: {count} significant lines (limit {SOURCE_LIMIT})")

    for path in test_files:
        count = physical_line_count(path)
        if count > TEST_LIMIT:
            relative = path.relative_to(root)
            violations.append(f"{relative}: {count} physical lines (limit {TEST_LIMIT})")

    return violations, len(source_files), len(test_files)


def main(root: Path = PROJECT_ROOT) -> int:
    """Report files that exceed their controlling limit."""
    violations, source_count, test_count = find_violations(root)
    if violations:
        print("File-length violations:")
        print(*violations, sep="\n")
        return 1

    print(
        f"File lengths OK: {source_count} source/script files and "
        f"{test_count} test files checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
