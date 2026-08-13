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
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.protocol.scent_wire import ScentWireError, decode_scent
from p2p_cop_agent.shared.config import JsonObject
from p2p_cop_agent.strategy.belief import Belief
from p2p_cop_agent.strategy.emitter_decoder import emitter_likelihood
from p2p_cop_agent.strategy.window_geometry import certainty_likelihood, window_centre

Observation = tuple[int, dict]


def observe(
    board: Board,
    incoming: JsonObject | None,
    turn: int,
    previous: Observation | None,
    self_cell: Coordinate | None = None,
) -> tuple[Belief, Observation] | None:
    """Return the new belief and this turn's observation, or `None` to keep the prior.

    Two readings are tried, strongest first.

    **Geometry (M11-01), when the window's shape determines its centre.** The published
    window is centred on the emitter, so its *key set* fixes the emitter exactly and
    without assuming anything about the peer's physics. This is checked first because it
    is a verified fix rather than an inference, and because the alternative failed
    silently in play: through the counted `G008` series and the `uoh-ay26` friendlies the
    belief never localised at all, `patrol.needs_sweep` stayed true every turn, and the
    Cop toured fixed waypoints -- the same move sequence in every sub-game against
    opponents doing different things. A window of honest zeros is *no evidence* to a
    likelihood and a *complete fix* to geometry.

    **Likelihood (M6-24), for any window whose shape does not.** The residual against
    last turn's observation is the newest emission stamp under the locked physics, so
    matching it against the agreed profile localises the emitter where raw intensity
    lags on revisited cells. The belief is rebuilt **fresh per observation, never
    Bayes-recursive** -- recursion calcified, measured 40/40 -> 0/40 -- so the prior
    survives only silent or malformed turns (M6-02c). The window is partial, so scoring
    trusts only cells both observations covered.

    ``self_cell`` is our own cell, and it removes exactly one cell from the answer. The
    Thief cannot be standing where we stand -- that is the capture condition, and the
    sub-game would already be over -- so a reading that puts it there is wrong however it
    was reached. It can be reached: a peer that publishes what it *observes* rather than
    what it emits sends a window centred on us, and both readings then agree on the one
    impossible cell. Aiming there is also the old "I am already on my target, so STAY"
    freeze by a new route. Zeroing the cell keeps the rest of the evidence rather than
    discarding the turn.

    Nothing here reads a true position `[AE-8]`; both readings consume only what the
    opponent published, and this last step uses only where *we* are.
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
    prior = Belief.uniform(board.grid_size, start=board.min_index)
    located = window_centre(observed, min_index=board.min_index, max_index=board.max_index)
    if self_cell is not None and located == self_cell.as_pair():
        located = None
    if located is not None:
        likelihood = certainty_likelihood(
            located, grid_size=board.grid_size, start=board.min_index)
    else:
        before = previous[1] if previous and previous[0] == turn - 1 else None
        trusted = set(observed) & set(before) if before else None
        likelihood = emitter_likelihood(observed, before, grid_size=board.grid_size,
                                        start=board.min_index, trusted=trusted)
    if self_cell is not None:
        likelihood = {**likelihood, self_cell.as_pair(): 0.0}
    return prior.updated(likelihood), (turn, observed)
