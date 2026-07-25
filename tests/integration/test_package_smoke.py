"""Installed-package surface smoke test."""

from p2p_cop_agent import CopSDK, __version__
from p2p_cop_agent.cli import build_parser


def test_public_package_surface_imports() -> None:
    """Import the SDK, version, and CLI parser from public package paths."""
    assert CopSDK.__name__ == "CopSDK"
    assert __version__ == "1.00"
    assert build_parser().prog == "p2p-cop"
