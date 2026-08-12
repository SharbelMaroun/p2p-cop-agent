"""Rebuild the belief from the opponent's published scent (M6-24).

Split out of `live_policy.py` under `G-04`. The seam is the one both sources already
draw. The **book** puts belief update inside the Decision Module rather than making it
a subsystem of its own -- rule 3's subsystems are the MCP connector, decision module,
log manager, deadline tracker and watchdog (Appendix E p.126/269, ch.8.4.2 p.68/163) --
and permits splitting the logic internally so long as it stays that module's
responsibility and the orchestrator still calls one entry point (p.62/152). `live_decide`
remains that entry point; this is a component behind it. The **reference** splits the
same way and further apart: it updates belief in `peer/turn_handler.py::TurnHandler.process`
(computation in `domain/belief.py::BeliefGrid.observe_smell`) while the move is chosen in
`domain/brains.py::BrainBase.decide` -- "completely separate", the inbound-message layer
divided from the decision layer (code notebook, 2026-08-12).

This module is the *wiring* half: it turns a wire `smell_grid` into a posterior. The
arithmetic stays in `strategy/`, which is the layer the M6-18 privacy guard protects.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.protocol.scent_wire import ScentWireError, decode_scent
from p2p_cop_agent.shared.config import JsonObject
from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.emitter_decoder import emitter_likelihood

Observation = tuple[int, dict]


def observe(
    board: Board,
    incoming: JsonObject | None,
    turn: int,
    previous: Observation | None,
) -> tuple[Belief, Observation] | None:
    """Return the new belief and this turn's observation, or `None` to keep the prior.

    `M6-24`: the residual against last turn's observation is the newest emission stamp
    under the locked physics, so matching it against the agreed profile localises the
    emitter where raw intensity lags on revisited cells. The belief is rebuilt **fresh
    per observation, never Bayes-recursive** -- recursion calcified, measured 40/40 ->
    0/40 -- so the prior survives only silent or malformed turns (M6-02c). The window is
    partial, so scoring trusts only cells both observations covered.

    Nothing here reads a true position `[AE-8]`.
    """
    if not isinstance(incoming, Mapping):
        return None
    try:
        observed = decode_scent(
            incoming.get("smell_grid"),
            min_index=board.min_index, max_index=board.max_index,
        )
    except ScentWireError:
        observed = {}  # a malformed observation is no observation, not a crash
    if not observed:
        return None
    before = previous[1] if previous and previous[0] == turn - 1 else None
    trusted = set(observed) & set(before) if before else None
    belief = Belief.uniform(board.grid_size, start=board.min_index).updated(
        emitter_likelihood(observed, before, grid_size=board.grid_size,
                           start=board.min_index, trusted=trusted))
    return belief, (turn, observed)
