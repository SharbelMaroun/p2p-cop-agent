"""Command-line entry point for the Cop peer.

Three subcommands, each a thin adapter over code that already existed:

* ``serve`` -- launch a peer (inbound FastMCP mailbox plus outbound connector) and play one
  match over the wire against a live opponent (:mod:`p2p_cop_agent.adapters.serve`).
* ``replay`` -- re-verify a stored log and print its banner (:mod:`p2p_cop_agent.replay`).
* ``verify`` -- the gate form of ``replay``: a verdict and a **non-zero exit** on
  ``TAMPERED``, so it can sit in a pipeline.

**``replay`` and ``verify`` were added on 2026-08-08, and their absence was a real gap.**
Rule 20 makes the replay application a threshold condition for submission, and this peer's
verifier has satisfied it since M8 -- but only through `scripts/` and the Tk window, so a
grader with a log in hand and a shell had no way in. The pinned reference exposes exactly
``python -m police_thief replay --log <path>``, and the companion Thief settled on the same
shape independently, so ``--log`` is the interoperable spelling rather than our invention.

**``build_parser`` imports no transport.** Every runtime import sits inside the function that
needs it, so ``--version`` and ``--help`` work on a machine where FastMCP is not installed.
"""

import argparse
from collections.abc import Sequence
from pathlib import Path

from p2p_cop_agent.shared import __version__

_DESCRIPTION = (
    "Cop peer command line. `serve` launches a peer and plays one match over the wire "
    "against a live opponent; `replay` re-verifies a stored match log and prints its "
    "banner; `verify` is the same check with an exit code instead of output."
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
    serve.add_argument("--artifacts", help="directory for the declaration, config, and "
                       "revealed game log — a counted game must produce its evidence")
    serve.add_argument("--sub-game", type=int, default=1, dest="sub_game",
                       help="this sub-game's number in the six-game series")
    replay = sub.add_parser("replay", help="re-verify a stored log and print its banner")
    replay.add_argument("--log", required=True, type=Path, help="path to the JSON log file")
    verify = sub.add_parser("verify", help="re-verify a stored log; exit non-zero if tampered")
    verify.add_argument("--log", required=True, type=Path, help="path to the JSON log file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run a subcommand, or show help when none is given."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "serve":
        return _serve(args)
    if args.command in ("replay", "verify"):
        return _replay(args.log, quiet=args.command == "verify")
    parser.print_help()
    return 0


def _replay(log_path: Path, *, quiet: bool) -> int:
    """Re-verify a stored log. Returns 0 for `Verified OK`, 1 for `TAMPERED`.

    **The exit code is the point of `verify`.** Rule 19 is an iron rule with no appeal, so a
    tampered log must be distinguishable by a script and not only by a human reading a banner.
    An unreadable or malformed file is *not* reported as tampering: that is a different
    failure with a different sanction, and calling it forgery would be a false accusation.
    """
    from p2p_cop_agent.replay import Replay, load_log
    from p2p_cop_agent.replay.load import LogNotReplayableError

    try:
        replay = Replay(load_log(log_path))
    except (OSError, LogNotReplayableError) as exc:
        print(f"cannot replay {log_path}: {exc}")
        return 2
    if not quiet:
        print(replay.banner)
        print(replay.sequence.summary)
    return 0 if replay.verdict.first_bad is None else 1


def _serve(args: argparse.Namespace) -> int:
    """Assemble a peer from config and play one match (see adapters.serve)."""
    from pathlib import Path

    from p2p_cop_agent.adapters.serve import serve_match

    result = serve_match(
        root=args.root, match_config_path=args.match,
        rate_limits_path=args.rate_limits, private_config_path=args.private,
        artifacts_dir=Path(args.artifacts) if args.artifacts else None,
        sub_game=args.sub_game,
    )
    if not result.played:
        print("no match: the opponent did not come up or did not agree in time")
        return 1
    print(f"match outcome: {result.outcome.outcome.name} after {result.outcome.steps} step(s)")
    return 0
