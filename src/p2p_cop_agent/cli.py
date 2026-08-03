"""Command-line entry point for the Cop peer.

``serve`` launches a peer (its inbound FastMCP mailbox plus the outbound connector)
and plays one match over the wire against a live opponent -- the M5-07c launcher in
:mod:`p2p_cop_agent.adapters.serve`. With no subcommand, help is shown and no runtime
starts, so ``--version`` and ``build_parser`` never import a transport.
"""

import argparse
from collections.abc import Sequence

from p2p_cop_agent.shared import __version__

_DESCRIPTION = (
    "Cop peer command line. `serve` launches a peer and plays one match over the wire "
    "against a live opponent; with no subcommand, this help is shown."
)


def build_parser() -> argparse.ArgumentParser:
    """Build the Cop argument parser (no transport import at parse time)."""
    parser = argparse.ArgumentParser(prog="p2p-cop", description=_DESCRIPTION)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")
    serve = sub.add_parser("serve", help="launch a peer and play one match over the wire")
    serve.add_argument("--root", default=".", help="repository root holding the shared bundle")
    serve.add_argument("--match", required=True, help="path to the shared match config JSON")
    serve.add_argument("--rate-limits", required=True, help="path to the rate-limits JSON")
    serve.add_argument("--private", required=True, help="path to this peer's private game.toml")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run a subcommand, or show help when none is given."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "serve":
        return _serve(args)
    parser.print_help()
    return 0


def _serve(args: argparse.Namespace) -> int:
    """Assemble a peer from config and play one match (see adapters.serve)."""
    from p2p_cop_agent.adapters.serve import serve_match

    result = serve_match(
        root=args.root, match_config_path=args.match,
        rate_limits_path=args.rate_limits, private_config_path=args.private,
    )
    if not result.played:
        print("no match: the opponent did not come up or did not agree in time")
        return 1
    print(f"match outcome: {result.outcome.outcome.name} after {result.outcome.steps} step(s)")
    return 0
