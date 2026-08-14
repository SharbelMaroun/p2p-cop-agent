"""The live Cop turn: belief-driven pursuit with barriers, on the wire (M6-21).

This module replaced the M5 placeholder that served a legal `STAY` every turn (a
guaranteed opponent survival): a policy that cannot win is a forfeit with extra steps.

It lives in `orchestration/`, not `adapters/`: the M6-18 privacy guard forbids the wire
layers from importing the inference modules (`test_belief_privacy`).

Each turn, in order:

1. **Observe.** `live_observation.observe` rebuilds the belief from a model-matched
   decode of the opponent's `smell_grid` (M6-24), fresh per observation and never
   Bayes-recursive; the prior survives only silent or malformed turns (M6-02c).
   Nothing there reads a true position `[AE-8]`.
1b. **Sweep while blind (M6-27).** A flat belief's argmax is the Cop's own start cell,
   answering `STAY` forever; blind and stale beliefs sweep a waypoint tour (`patrol`).
2. **Choose one legal intent** via the chooser `[strategy] name` selects — by default
   `strategy.denial.denial_turn_intent`, which denies the clearance core and then cuts
   each surviving orbit before handing over to the incumbent shrink stack: capture-move
   or trapping barrier, else squeeze, else the containment ratchet on the just-vacated
   cell in a locked endgame, else the M6-25 interception chase. `name = "engine"` selects
   the `M11-02` alpha-beta search; `name = "robust[_worst|_expected|_lcb]"` wraps the
   default in the plausible-set re-ranking (Phase B). One move *or* barrier (book §3.4).
3. **Declare and claim.** A placed barrier is disclosed truthfully in
   `barrier_placed` (rule: hiding one is forbidden), and landing on — or walling —
   the believed cell sends `capture_claim` for that cell: a claim is checked by the
   opponent, never believed, so an honest miss simply continues the game.
4. **Emit involuntarily.** The trail advances at the cell we now occupy — `STAY`,
   move, and barrier turns all deposit identically (M6-09a) — and the wire carries
   the agreed 5×5 window of it.
5. **Seal the truth.** The private payload now records the real move and the real
   position, because the audit is what makes a capture claim provable; a sealed
   record that hid the position would leave rule `[AE-21]`'s proof empty.
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import partial

from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move
from p2p_cop_agent.orchestration.live_observation import observe
from p2p_cop_agent.orchestration.turn_loop import Decide
from p2p_cop_agent.protocol.messages import now_iso
from p2p_cop_agent.protocol.scent_wire import encode_scent
from p2p_cop_agent.shared.config import JsonObject
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent
from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.denial import denial_turn_intent
from p2p_cop_agent.strategy.engine import engine_turn_intent
from p2p_cop_agent.strategy.hints import hint_max_words
from p2p_cop_agent.strategy.landmarks import place_for
from p2p_cop_agent.strategy.patrol import aim
from p2p_cop_agent.strategy.robust_pursuit import robust_turn_intent
from p2p_cop_agent.strategy.scent_field import ScentField
from p2p_cop_agent.strategy.verbal import generate_hint

ENGINE_STRATEGY = "engine"
ROBUST_PREFIX = "robust"
DEFAULT_HORIZON = 35


def chooser_for(name: str, game: JsonObject):
    """Return the turn chooser a `[strategy] name` selects, defaulting to the incumbent."""
    # An unknown name falls back rather than raising: a typo in a private config must
    # cost a worse strategy, never a technical loss at the top of a counted series.
    # The default is returned as a module global on purpose, so the M6-26 fail-safe stays
    # injectable -- `test_live_failsafe` poisons `denial_turn_intent` to prove a strategy
    # exception becomes a truthful STAY, and a chooser captured at import time would make
    # that test silently patch nothing.
    if name == ENGINE_STRATEGY:
        return partial(engine_turn_intent, horizon=_horizon(game))
    # `robust[_worst|_expected|_lcb]` wraps the default in the Phase-B plausible-set
    # re-ranking; it consumes the belief (`wants_belief` in `live_decide`) and degrades to
    # the incumbent when localization is exact, so the flag is safe to leave selectable.
    if name.startswith(ROBUST_PREFIX):
        return partial(robust_turn_intent, aggregation=name[len(ROBUST_PREFIX):].lstrip("_")
                       or "worst")
    return denial_turn_intent


def _horizon(game: JsonObject) -> int:
    """Return the sub-game length, so the search never plans past the final turn."""
    section = game.get("movement_and_barriers")
    threshold = section.get("survival_threshold") if isinstance(section, Mapping) else None
    return threshold if isinstance(threshold, int) and threshold > 0 else DEFAULT_HORIZON


def live_decide(board: Board, start: Coordinate, game: JsonObject,
                *, claim_every_turn: bool = False, strategy: str = "") -> Decide:
    """Return the turn-loop `decide` playing the measured belief-pursuit stack.

    State is closed over per call, so two matches in one process share nothing (rule 2)
    and identical message sequences reproduce identical games (M6-03d): every component is
    deterministic and the belief tie-break is row-major.
    """
    quota = int(game["movement_and_barriers"]["max_barriers"])  # type: ignore[index,call-overload]
    choose = chooser_for(strategy, game)
    wants_belief = strategy.startswith(ROBUST_PREFIX)
    trail = ScentField(board=board)
    state = {
        "cell": start,
        "previous": None,  # the cell just vacated — the containment ratchet's candidate
        "barriers": BarrierField(quota),
        "belief": Belief.uniform(board.grid_size, start=board.min_index),
        "count": 0,
        "seen": None,  # (turn, observed cells) — the decoder's previous observation
        "reachable": None,  # the robust arm's motion-constrained plausible set, carried
    }

    def decide(incoming: JsonObject | None) -> tuple[JsonObject, JsonObject]:
        state["count"] += 1
        count = state["count"]
        fresh = observe(board, incoming, count, state["seen"], state["cell"])
        if fresh is not None:
            state["belief"], state["seen"] = fresh
        # M6-27: a flat or stale belief aims at (0,0) — our own start — and that reads
        # as "already there", i.e. STAY forever. `aim` sweeps instead.
        seen_turn = state["seen"][0] if state["seen"] else None
        target = aim(board, state["belief"], seen_turn, count, state["cell"])

        claim, barrier_placed = None, None
        # Fail-safe (M6-26): a strategy exception must cost one imperfect turn, never
        # the match. An uncaught raise here propagates to the watchdog as a freeze and
        # scores the technical 0/0 — worse than any legal move. STAY is legal from
        # every on-board cell, keeps the sealed record truthful, and leaves all state
        # coherent, so the game continues and the audit still verifies.
        try:
            # The robust arm alone is handed the belief and carries its own
            # motion-constrained plausible set turn to turn; every other chooser sees only
            # the argmax `target` and returns a bare intent.
            extra = ({"belief": state["belief"], "reachable": state["reachable"]}
                     if wants_belief else {})
            chosen = choose(board, state["cell"], target, state["barriers"],
                            state["previous"], **extra)
            if wants_belief:
                chosen, state["reachable"] = chosen
            if isinstance(chosen, BarrierIntent):
                state["barriers"], state["previous"] = (
                    state["barriers"].place_adjacent(board, state["cell"], chosen.cell), None)
                barrier_placed = [chosen.cell.row, chosen.cell.col]
                move_label = f"BARRIER:{barrier_placed}"
                if chosen.cell == target:
                    claim = barrier_placed  # a barrier on the Thief's cell captures (§3.4)
            else:
                state["previous"], state["cell"] = state["cell"], apply_move(
                    board, state["cell"], chosen.action, state["barriers"].cells)
                move_label = f"MOVE:{chosen.action.name}"
                if state["cell"] == target:
                    claim = [target.row, target.col]
            # amireman profile: the claim is the Cop's own post-move cell EVERY turn,
            # ungated -- their thief evaluates co-location itself, and a gated claim
            # misses captures under their semantics. Off by default: an every-turn
            # claim broadcasts our true position, a gift no other profile demands.
            if claim_every_turn:
                claim = [state["cell"].row, state["cell"].col]
        except Exception:  # noqa: BLE001 - the match outlives any strategy bug
            state["previous"], move_label = None, "MOVE:STAY"

        trail.advance(state["cell"])
        hint = generate_hint(
            place_for(board, state["cell"], game),
            provider=None,  # zero-token template: the always-available floor
            bluff=count % 2 == 0, variant=count, max_words=hint_max_words(game),
        )
        # `state`/`verdict` mirror the Thief's sealed shape exactly (C-042): the book's
        # commit covers State||Move||Intent, and a peer's replay converter read
        # `payload["state"]` directly -- its absence here crashed their coordinator
        # after a completed, verified game. The Thief's format is field-proven across
        # every game it played, so it is copied verbatim, post-move, barriers sorted.
        barriers = sorted([c.row, c.col] for c in state["barriers"].placements)
        cell = [state["cell"].row, state["cell"].col]
        payload: JsonObject = {
            "step": count,
            "state": f"grid={board.grid_size}x{board.grid_size};self={cell};barriers={barriers}",
            "move": move_label,
            "position": cell,
            "barriers": barriers,
            "intent": hint.intent,
            "verdict": hint.intent,
            "hint": hint.text,
        }
        public: JsonObject = {
            "hint": hint.text,
            "smell_grid": encode_scent(trail.window(state["cell"])),
            "timestamp": now_iso(),
        }
        if barrier_placed is not None:
            public["barrier_placed"] = barrier_placed
        if claim is not None:
            public["capture_claim"] = claim
        return payload, public

    return decide
