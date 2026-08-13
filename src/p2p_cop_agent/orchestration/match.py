"""Compose the whole pre-play preamble and the sub-game into one match (M5-17f).

The book's order before the first move: **negotiate -> exchange & verify Step-0 ->
write and lock the declaration -> play**. The pieces exist (M5-17f-i/ii/iii, M5-17);
this runs them as one autonomous sequence, so a peer plays a match end to end with no
human in the loop -- the whole point of `M5-17f`.

Transport-agnostic in the same way the turn loop is: given a transport, the two mailbox
sources, and a clock, it runs in-memory in tests and over a socket in production, so the
sequencing is proven without a second machine.

**A match that never agrees never plays.** ``negotiate_match`` returning ``None`` (a
silent opponent) or raising ``NegotiationError`` (a refusal) both stop before the
declaration is even built -- a declaration locked for a game that will not happen would
be a lie, and the first move must never precede the lock.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from p2p_cop_agent.orchestration.delivery import DeliveryRetry
from p2p_cop_agent.orchestration.negotiation_handshake import Agreement, negotiate_match
from p2p_cop_agent.orchestration.phases import PhaseMachine
from p2p_cop_agent.orchestration.polling import DEFAULT_POLL_INTERVAL, Heartbeat, turn_receiver
from p2p_cop_agent.orchestration.sub_game import SubGameOutcome, run_sub_game_over_wire
from p2p_cop_agent.orchestration.turn_loop import Decide, Receive
from p2p_cop_agent.protocol.commit_reveal import TurnLedger
from p2p_cop_agent.protocol.declaration import build_declaration, lock_declaration
from p2p_cop_agent.protocol.negotiation import terms_from_config
from p2p_cop_agent.reporting import (
    MatchIdentity,
    build_config,
    config_filename,
    declaration_filename,
    league,
    provenance,
    validated_write,
    write_artifact,
)
from p2p_cop_agent.reporting.series_consensus import derive_game_uid
from p2p_cop_agent.shared.config import JsonObject

COP_ROLE = "police"


@dataclass(frozen=True, slots=True)
class MatchResult:
    """The whole match: what was agreed, the locked declaration, and how play ended.

    Every field is ``None`` when the peers never reached agreement, so a caller can
    tell "no game happened" from "a game happened and ended thus" without guessing.
    """

    agreement: Agreement | None
    declaration: JsonObject | None
    declaration_lock: str | None
    outcome: SubGameOutcome | None

    @property
    def played(self) -> bool:
        """Whether a sub-game actually ran (i.e. agreement was reached)."""
        return self.outcome is not None


def play_match(
    *,
    sdk: object,
    transport: object,
    take_offer: Callable[[], JsonObject | None],
    take_turn: Callable[[], JsonObject | None],
    decide: Decide,
    identity: Mapping[str, object],
    game_id: str,
    started_at: str,
    max_tokens_per_game: int,
    clock: Callable[[], float],
    sleep: Callable[[float], None],
    step_zero: Mapping[str, object] | None = None,
    artifacts_dir: Path | None = None,
    # Rule 37's history, supplied rather than defaulted. An empty default would declare
    # "this is the first counted game" on every call, and rule 38 makes a false declaration
    # absolute disqualification of the project — so the friction of passing it is the point.
    # `reporting.league.PlayedGame.from_result` builds this from the result artifacts.
    played_games: Sequence[league.PlayedGame] = (),
    sub_game: int = 1,
    opens: bool = False,
    heartbeat: Heartbeat | None = None,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    offer_timeout: float | None = None,
) -> MatchResult:
    """Negotiate, lock the declaration, then play -- or stop cleanly if never agreed."""
    game = dict(sdk.game_config)  # type: ignore[attr-defined]
    timeout = float(game["network_and_league"]["response_timeout_sec"])
    # The offer wait is PRE-game patience: at a role swap the opponent's runner may have
    # spent its negotiate on the previous sub-game's audit window and need minutes to come
    # back, so the caller passes its connect budget here. `response_timeout_sec` starts
    # governing once play does — capping the wait at 30s ended the amireman smoke twice.
    agreement = negotiate_match(
        game=game, identity=identity, transport=transport, take_offer=take_offer,
        clock=clock, sleep=sleep, timeout=max(timeout, offer_timeout or 0.0),
        poll_interval=poll_interval, heartbeat=heartbeat, step_zero=step_zero,
    )
    if agreement is None:
        return MatchResult(None, None, None, None)
    # Derived here, not passed in, because it cannot be known any earlier: the book says
    # the four artifacts "share a common identifier (game_uid)", and the shared derivation
    # takes the agreed terms **and both group ids** -- so the opponent's id must already be
    # on the table. Computing it after the handshake is what makes both peers arrive at the
    # same UUID without an extra round trip.
    #
    # It used to be `config_sha256[:32]`, a value only this side computed. That produced an
    # artifact set carrying two different uids: the logs said `5a7b4a6e58be4479...` while
    # the result report -- which already used this derivation -- said
    # `7b1d942e-5a9c-...`, the same UUID `uoh-ay26` independently computed for G005. The
    # report was right and the logs were the outlier, so the logs move.
    game_uid = derive_game_uid(
        terms_from_config(game),
        [str(identity.get("group_id") or ""),
         str(agreement.opponent_identity.get("group_id") or "")],
    )
    declaration = build_declaration(
        game_id=game_id, game_uid=game_uid, our_identity=identity,
        opponent_identity=agreement.opponent_identity,
        config_sha256=sdk.config_sha256,  # type: ignore[attr-defined]
        num_sub_games=int(game["network_and_league"]["num_games"]),
        max_tokens_per_game=max_tokens_per_game, started_at=started_at,
        # Rule 53: the commit of the code that is about to play, resolved rather than
        # assumed. `provenance.describe()` also reports whether the tree was clean, which a
        # counted game should check — a hash pointing at code that did not run identifies
        # the wrong thing while looking correct.
        github_commit=provenance.describe()["github_commit"],
        # Rule 37: the count declared at the start of each game. Derived from the result
        # artifacts already on disk, because rule 38 makes a false declaration absolute
        # disqualification of the project and does not distinguish a lie from a slip.
        games_played_declaration=league.declaration_block(
            played_games, agreement.opponent_identity.get("group_id", "")),
    )
    lock = lock_declaration(declaration)
    if artifacts_dir is not None:
        # `M7-22`: "the pre-game declaration is signed and fixed **before play begins**".
        # Written here rather than after the match on purpose -- a declaration emitted at
        # the end could have been edited to suit the result, which is the whole thing
        # locking it beforehand is meant to rule out.
        identity_for_files = MatchIdentity(game_id, game_uid)
        write_artifact(
            artifacts_dir, declaration_filename(identity_for_files),
            {**declaration, "declaration_lock": lock},
        )
        validated_write(
            artifacts_dir, config_filename(identity_for_files, sub_game),
            build_config(
                identity=identity_for_files, sub_game=sub_game, game=game,
                config_sha256=sdk.config_sha256,  # type: ignore[attr-defined]
            ),
        )
    receive = turn_receiver(
        take_turn, clock=clock, sleep=sleep, timeout=timeout,
        poll_interval=poll_interval, heartbeat=heartbeat,
    )
    outcome = _play(game, transport, receive, decide, opens, step_zero)
    return MatchResult(agreement, declaration, lock, outcome)


def _play(
    game: Mapping[str, object], transport: object, receive: Receive,
    decide: Decide, opens: bool, step_zero: Mapping[str, object] | None = None,
) -> SubGameOutcome:
    """Play one sub-game to a decided outcome, bounded by the negotiated horizon.

    The retry policy comes from the same signed match object both peers hold, so a
    dropped request over the tunnel costs a bounded re-send rather than the sub-game
    (M5-14b); its limits are Appendix F's, not ours to choose.
    """
    threshold = game["movement_and_barriers"]["survival_threshold"]  # type: ignore[index]
    return run_sub_game_over_wire(
        machine=PhaseMachine(), ledger=TurnLedger(COP_ROLE), transport=transport,
        receive=receive, decide=decide, survival_threshold=threshold, opens=opens,
        retry=DeliveryRetry.from_match(game),  # type: ignore[arg-type]
        step_zero=step_zero,
    )
