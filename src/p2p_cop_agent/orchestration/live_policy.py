"""The live Cop turn: belief-driven pursuit with barriers, on the wire (M6-21).

**Until 2026-08-07 the served move was a documented M5 placeholder — a legal `STAY`
every turn.** A Cop that never leaves its start cell can never satisfy the capture
condition, so every served match was a guaranteed 5-point survival for the opponent
while the measured pursuit (96.7% capture over the forty-seed arena) existed only in
`scripts/experiment_arena.py`. This module is the seam `serve.py` said would replace
it (M6-21), and the placeholder is gone rather than kept as an option — a policy that
cannot win is not a fallback, it is a forfeit with extra steps.

It lives in `orchestration/`, not `adapters/`, and the M6-18 privacy guard is why:
the wire layers may never import the inference modules (`test_belief_privacy`), so a
belief-driven policy in `adapters/` was refused structurally. Wiring perception into
a decision the wire then carries is exactly what `orchestration/` is for — the same
homing the companion peer's live policy reached for the same reason.

Each turn, in order:

1. **Observe.** The opponent's `smell_grid` becomes a likelihood and the belief is
   rebuilt from it fresh each turn, the prior surviving only silent or malformed
   turns (M6-02c). Fresh-not-recursive is measured, not stylistic: recursion under a
   static likelihood has no motion model, calcifies on history, and scored 0/40
   where the fresh form scores 40/40. Nothing here reads a true position `[AE-8]`.
2. **Choose one legal intent** via `strategy.anticipation.predictive_turn_intent` —
   capture-move or trapping barrier, else squeeze, else the containment ratchet on
   the just-vacated cell in a locked endgame, else the flight-set chase. One move
   *or* one barrier, never both (book §3.4). The same function the opponent grid
   measures, so the served number is the published number.
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
from p2p_cop_agent.strategy.anticipation import predictive_turn_intent
from p2p_cop_agent.strategy.barrier_policy import BarrierIntent
from p2p_cop_agent.strategy.belief import Belief, scent_likelihood
from p2p_cop_agent.strategy.hints import hint_max_words
from p2p_cop_agent.strategy.landmarks import place_for
from p2p_cop_agent.strategy.scent_field import ScentField
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
    }

    def _observe(incoming: JsonObject | None) -> None:
        """Rebuild belief from the freshest observation; carry it only across silence.

        Not Bayes-recursive, and measurably so: carrying the prior under this static
        likelihood has no motion model, so history accumulates and the argmax
        calcifies on old trail — the opponent grid scored the recursive form 0/40
        against the very archetype the fresh form tracks 40/40. The prior survives
        only turns with nothing to see, where it beats resetting to a corner-tied
        uniform (M6-02c).
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
            state["belief"] = Belief.uniform(board.grid_size, start=board.min_index).updated(
                scent_likelihood(observed, board.grid_size, start=board.min_index))

    def decide(incoming: JsonObject | None) -> tuple[JsonObject, JsonObject]:
        state["count"] += 1
        count = state["count"]
        _observe(incoming)
        target = Coordinate.from_pair(state["belief"].most_likely())

        claim: list | None = None
        barrier_placed: list | None = None
        chosen = predictive_turn_intent(board, state["cell"], target,
                                        state["barriers"], state["previous"])
        if isinstance(chosen, BarrierIntent):
            state["barriers"] = state["barriers"].place_adjacent(board, state["cell"], chosen.cell)
            state["previous"] = None  # a wall turn vacates nothing
            barrier_placed = [chosen.cell.row, chosen.cell.col]
            move_label = f"BARRIER:{barrier_placed}"
            if chosen.cell == target:
                claim = barrier_placed  # a barrier on the Thief's cell captures (§3.4)
        else:
            state["previous"] = state["cell"]
            state["cell"] = apply_move(board, state["cell"], chosen.action, state["barriers"].cells)
            move_label = f"MOVE:{chosen.action.name}"
            if state["cell"] == target:
                claim = [target.row, target.col]

        trail.advance(state["cell"])
        hint = generate_hint(
            place_for(board, state["cell"], game),
            provider=None,  # zero-token template: the always-available floor
            bluff=count % 2 == 0, variant=count, max_words=hint_max_words(game),
        )
        payload: JsonObject = {
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
