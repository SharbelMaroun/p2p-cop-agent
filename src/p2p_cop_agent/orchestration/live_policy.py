"""The live Cop turn: belief-driven pursuit with barriers, on the wire (M6-21).

**Until 2026-08-07 the served move was a documented M5 placeholder — a legal `STAY`
every turn**, so every served match was a guaranteed survival for the opponent while
the measured pursuit lived only in `scripts/`. This module is the seam `serve.py` said
would replace it (M6-21); the placeholder is gone rather than kept as an option,
because a policy that cannot win is a forfeit with extra steps.

It lives in `orchestration/`, not `adapters/`: the M6-18 privacy guard forbids the wire
layers from importing the inference modules (`test_belief_privacy`), so a belief-driven
policy in `adapters/` was refused structurally.

Each turn, in order:

1. **Observe.** The opponent's `smell_grid` is decoded model-matched (M6-24): the
   residual against last turn's observation is exactly the newest stamp under the
   locked physics, so the belief localises the emitter instead of lagging on raw
   intensity. Fresh per observation, never Bayes-recursive (measured: recursion
   calcified, 40/40 → 0/40); the prior survives only silent or malformed turns
   (M6-02c). Nothing here reads a true position `[AE-8]`.
1b. **Sweep while blind (M6-27).** A flat belief's row-major argmax is the Cop's own
   start cell, so aiming there answered `STAY` forever — 26 turns of it in the
   `amireman` friendly. Never-observed, evidence-free and stale beliefs all take a
   deterministic waypoint tour instead (`strategy.patrol`).
2. **Choose one legal intent** via `strategy.shrink.shrinking_turn_intent` —
   capture-move or trapping barrier, else squeeze, else the containment ratchet on
   the just-vacated cell in a locked endgame, else the interception chase (M6-25:
   the flight-centroid chase tied against edge oscillators and mirrored them to the
   horizon; the summed-distance rank breaks the tie and converts the mobility-aware
   archetypes 40/40 where every prior arm scored 0/40). One move *or* one barrier,
   never both (book §3.4). The same function the tournament grid measures, so the
   served number is the published number.
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

from p2p_cop_agent.domain.barriers import BarrierField
from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move
from p2p_cop_agent.orchestration.turn_loop import Decide
from p2p_cop_agent.protocol.scent_wire import ScentWireError, decode_scent, encode_scent
from p2p_cop_agent.shared.config import JsonObject
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent
from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.emitter_decoder import emitter_likelihood
from p2p_cop_agent.strategy.hints import hint_max_words
from p2p_cop_agent.strategy.landmarks import place_for
from p2p_cop_agent.strategy.patrol import aim
from p2p_cop_agent.strategy.scent_field import ScentField
from p2p_cop_agent.strategy.shrink import shrinking_turn_intent
from p2p_cop_agent.strategy.verbal import generate_hint


def live_decide(board: Board, start: Coordinate, game: JsonObject) -> Decide:
    """Return the turn-loop `decide` playing the measured belief-pursuit stack.

    State is closed over per call — position, barriers, belief, trail, and the turn
    counter — so two matches in one process share nothing (rule 2), and identical
    message sequences reproduce identical games (M6-03d): every component below is
    deterministic and the belief tie-break is row-major.
    """
    quota = int(game["movement_and_barriers"]["max_barriers"])  # type: ignore[index,call-overload]
    trail = ScentField(board=board)
    state = {
        "cell": start,
        "previous": None,  # the cell just vacated — the containment ratchet's candidate
        "barriers": BarrierField(quota),
        "belief": Belief.uniform(board.grid_size, start=board.min_index),
        "count": 0,
        "seen": None,  # (turn, observed cells) — the decoder's previous observation
    }

    def _observe(incoming: JsonObject | None, turn: int) -> None:
        """Rebuild belief from a model-matched decode of the freshest observation.

        `M6-24`: the residual against last turn's observation is the newest emission
        stamp under the locked physics, so matching it against the agreed profile
        localises the emitter where raw intensity lags on revisited cells. Fresh per
        observation, never Bayes-recursive (recursion calcified, 40/40 → 0/40); the
        prior survives only silent or malformed turns (M6-02c). The window is partial,
        so scoring trusts only cells both observations covered.
        """
        if not isinstance(incoming, Mapping):
            return
        try:
            observed = decode_scent(
                incoming.get("smell_grid"),
                min_index=board.min_index, max_index=board.max_index,
            )
        except ScentWireError:
            observed = {}  # a malformed observation is no observation, not a crash
        if observed:
            seen = state["seen"]
            before = seen[1] if seen and seen[0] == turn - 1 else None
            trusted = set(observed) & set(before) if before else None
            state["belief"] = Belief.uniform(board.grid_size, start=board.min_index).updated(
                emitter_likelihood(observed, before, grid_size=board.grid_size,
                                   start=board.min_index, trusted=trusted))
            state["seen"] = (turn, observed)

    def decide(incoming: JsonObject | None) -> tuple[JsonObject, JsonObject]:
        state["count"] += 1
        count = state["count"]
        _observe(incoming, count)
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
            chosen = shrinking_turn_intent(board, state["cell"], target,
                                           state["barriers"], state["previous"])
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
        except Exception:  # noqa: BLE001 - the match outlives any strategy bug
            state["previous"], move_label = None, "MOVE:STAY"

        trail.advance(state["cell"])
        hint = generate_hint(
            place_for(board, state["cell"], game),
            provider=None,  # zero-token template: the always-available floor
            bluff=count % 2 == 0, variant=count, max_words=hint_max_words(game),
        )
        payload: JsonObject = {
            "step": count,
            "move": move_label,
            "position": [state["cell"].row, state["cell"].col],
            "barriers": [[c.row, c.col] for c in state["barriers"].placements],
            "intent": hint.intent,
            "hint": hint.text,
        }
        public: JsonObject = {
            "hint": hint.text,
            "smell_grid": encode_scent(trail.window(state["cell"])),
            "timestamp": f"t{count}",
        }
        if barrier_placed is not None:
            public["barrier_placed"] = barrier_placed
        if claim is not None:
            public["capture_claim"] = claim
        return payload, public

    return decide
