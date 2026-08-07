"""The league evidence bundle for this repository (`M9-09`, `X-15`).

One place to answer what a submission turns on: for each counted game, do we still have the
artifacts, the commit that ran it, and evidence it was reported?

**`M9-09c` is worded as "record proof that each report was sent", and the obvious reading
overclaims.** The book's decisive layer is receipt at the lecturer's address (p.78/183):
"if a report is not received from one of the sides, that side will not be credited for the
game". A sender cannot observe receipt — only the recipient can. So what is stored here is a
`SendReceipt`, not a proof of delivery, and every record it writes says which of the two it
is. Overstating it in an artifact would be a claim the lecturer's own inbox could contradict.

The reference implementation stores nothing at all: its sender returns `{status, reason}`
for a CLI line that never reaches any of the four artifacts, so after a series the only
evidence a report went out is somebody's memory.

Gap-finding returns rather than raises. This is the pre-submission question and the useful
answer is the whole list; stopping at the first missing receipt turns one review into six.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

REQUIRED_KINDS = frozenset({"declaration", "config", "log", "result"})
MINIMUM_GAMES = 2
MINIMUM_OPPONENTS = 2


class EvidenceError(ValueError):
    """Raised when the bundle would claim more than it can support."""


@dataclass(frozen=True, slots=True)
class SendReceipt:
    """What this side observed when it sent one report. **Not proof of receipt.**"""

    game_id: str
    message_id: str
    sent_at: str
    recipient: str

    def __post_init__(self) -> None:
        for name in ("game_id", "message_id", "sent_at", "recipient"):
            if not getattr(self, name):
                raise EvidenceError(f"a send receipt needs a non-empty {name}")

    @classmethod
    def from_api_response(cls, response: Mapping[str, object], *, game_id: str,
                          sent_at: str, recipient: str) -> SendReceipt:
        """Read the id from a `users().messages().send` response.

        Refused when absent rather than stored empty: afterwards, a report that failed to
        send and one that sent without a receipt are indistinguishable, and only one of them
        costs the game's points.
        """
        message_id = response.get("id")
        if not isinstance(message_id, str) or not message_id:
            raise EvidenceError(
                f"the send response for {game_id!r} carries no message id, so nothing "
                "evidences the send; rule 32 makes reporting Mandatory [AE-32]")
        return cls(game_id=game_id, message_id=message_id, sent_at=sent_at,
                   recipient=recipient)

    def as_record(self) -> dict[str, str]:
        return {"game_id": self.game_id, "message_id": self.message_id,
                "sent_at": self.sent_at, "recipient": self.recipient,
                "evidences": "API acceptance, not receipt by the lecturer"}


@dataclass(frozen=True, slots=True)
class CountedGame:
    """One game as the bundle knows it."""

    game_id: str
    opponent_group_id: str
    counted: bool = True
    won: bool = False


@dataclass
class EvidenceBundle:
    """Every counted game's evidence, assembled for submission."""

    games: list[CountedGame] = field(default_factory=list)
    receipts: dict[str, SendReceipt] = field(default_factory=dict)
    provenance: dict[str, dict] = field(default_factory=dict)

    def add_game(self, game: CountedGame, *, provenance: Mapping[str, object]) -> None:
        """Record a game and the commit that ran it (`M9-09b`)."""
        if any(existing.game_id == game.game_id for existing in self.games):
            raise EvidenceError(f"{game.game_id!r} is already in the bundle")
        commit = provenance.get("github_commit")
        if not isinstance(commit, str) or len(commit) != 40:
            raise EvidenceError(
                f"{game.game_id!r} has no resolved commit; rule 53 requires the hash of the "
                "code that played, and 'unknown' identifies nothing [AE-53]")
        self.games.append(game)
        self.provenance[game.game_id] = dict(provenance)

    def add_receipt(self, receipt: SendReceipt) -> None:
        if receipt.game_id in self.receipts:
            raise EvidenceError(
                f"{receipt.game_id!r} already has a receipt; two sends for one game risks "
                "the rule 35 conflict verdict, which scores 0 for BOTH teams")
        self.receipts[receipt.game_id] = receipt

    def unreported(self) -> tuple[str, ...]:
        """Counted games with no receipt — each scores nothing (`AE-32`)."""
        return tuple(sorted(g.game_id for g in self.games
                            if g.counted and g.game_id not in self.receipts))

    def counted_against(self, opponent: str) -> int:
        return sum(1 for g in self.games if g.opponent_group_id == opponent and g.counted)

    def reconcile(self, declared: Mapping[str, int]) -> None:
        """Check every declared per-opponent count in one pass (`M9-09d`).

        Rule 38's sanction is absolute disqualification of the project, so every opponent is
        checked before anything raises — this is not a thing to discover one at a time.
        """
        problems = [
            f"declared {count} game(s) against {opponent!r} but the bundle holds "
            f"{self.counted_against(opponent)}; rule 38 disqualifies the project for a "
            "false declaration [AE-38]"
            for opponent, count in sorted(declared.items())
            if count != self.counted_against(opponent)
        ]
        if problems:
            raise EvidenceError("; ".join(problems))

    def summary(self) -> dict[str, object]:
        counted = [g for g in self.games if g.counted]
        return {
            "counted_games": len(counted),
            "opponents": sorted({g.opponent_group_id for g in counted}),
            "warm_ups": len(self.games) - len(counted),
            "receipts": [self.receipts[k].as_record() for k in sorted(self.receipts)],
            "unreported": list(self.unreported()),
            "commits": {k: v.get("github_commit") for k, v in sorted(self.provenance.items())},
        }


def archive_is_complete(files: Sequence[str]) -> bool:
    """Whether an archived set holds all four artifact kinds (`M9-09a`)."""
    return {name.split("_", 1)[0] for name in files} >= REQUIRED_KINDS


def missing_evidence(bundle: EvidenceBundle,
                     archives: Mapping[str, Sequence[str]]) -> dict[str, list[str]]:
    """Per counted game, everything still absent."""
    gaps: dict[str, list[str]] = {}
    for game in bundle.games:
        if not game.counted:
            continue
        missing = []
        if not archive_is_complete(archives.get(game.game_id) or ()):
            missing.append("archived artifact set")
        if game.game_id not in bundle.receipts:
            missing.append("send receipt")
        if missing:
            gaps[game.game_id] = missing
    return gaps


def minimums_met(bundle: EvidenceBundle) -> tuple[bool, str]:
    """Whether rule 31's minimum is met, with a reason that says which half is short."""
    counted = [g for g in bundle.games if g.counted]
    opponents = {g.opponent_group_id for g in counted}
    unreported = bundle.unreported()
    if unreported:
        return False, f"reported nothing for {', '.join(unreported)}; each scores 0 [AE-32]"
    if len(counted) < MINIMUM_GAMES:
        return False, f"{len(counted)} counted game(s), {MINIMUM_GAMES} required [AE-31]"
    if len(opponents) < MINIMUM_OPPONENTS:
        return False, (f"{len(opponents)} distinct opponent(s), {MINIMUM_OPPONENTS} required "
                       "— repeat games do not accumulate score [AE-52]")
    return True, f"{len(counted)} counted games against {len(opponents)} groups, all reported"
