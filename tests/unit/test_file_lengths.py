"""Tests for source and test file-length enforcement."""

from pathlib import Path

from scripts.check_file_lengths import (
    SOURCE_LIMIT,
    TEST_LIMIT,
    find_violations,
    main,
    significant_line_count,
)


def test_source_count_ignores_blank_and_comment_only_lines(tmp_path: Path) -> None:
    """Count executable and declaration lines without comments or blanks."""
    path = tmp_path / "module.py"
    path.write_text("# comment\n\nvalue = 1  # inline comment\n", encoding="utf-8")

    assert significant_line_count(path) == 1


def test_length_check_accepts_files_at_limits(tmp_path: Path) -> None:
    """Allow source and test files at their respective limits."""
    source = tmp_path / "src" / "package" / "module.py"
    test = tmp_path / "tests" / "test_module.py"
    source.parent.mkdir(parents=True)
    test.parent.mkdir(parents=True)
    source.write_text("value = 1\n" * SOURCE_LIMIT, encoding="utf-8")
    test.write_text("# test line\n" * TEST_LIMIT, encoding="utf-8")

    assert find_violations(tmp_path)[0] == []
    assert main(tmp_path) == 0


def test_length_check_reports_source_and_test_violations(tmp_path: Path) -> None:
    """Report each class of over-limit Python file."""
    source = tmp_path / "scripts" / "tool.py"
    test = tmp_path / "tests" / "test_tool.py"
    source.parent.mkdir(parents=True)
    test.parent.mkdir(parents=True)
    source.write_text("value = 1\n" * (SOURCE_LIMIT + 1), encoding="utf-8")
    test.write_text("# physical line\n" * (TEST_LIMIT + 1), encoding="utf-8")

    violations, source_count, test_count = find_violations(tmp_path)

    assert source_count == 1
    assert test_count == 1
    assert len(violations) == 2
    assert "significant lines" in violations[0]
    assert "physical lines" in violations[1]
    assert main(tmp_path) == 1
