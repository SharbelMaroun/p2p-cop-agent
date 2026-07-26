"""Tests for the public code version."""

from p2p_cop_agent import __version__


def test_code_version_starts_at_required_value() -> None:
    """Expose the course-required initial code version."""
    assert __version__ == "1.00"
