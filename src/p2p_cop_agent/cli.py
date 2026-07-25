"""Behavior-free command-line entry point for the Cop package."""

import argparse
from collections.abc import Sequence

from p2p_cop_agent.shared import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the Cop scaffold argument parser."""
    parser = argparse.ArgumentParser(
        prog="p2p-cop",
        description="Cop peer package scaffold; runtime behavior is not implemented.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Show scaffold help without starting any peer behavior."""
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0
