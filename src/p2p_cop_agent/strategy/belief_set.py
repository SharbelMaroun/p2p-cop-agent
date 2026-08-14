"""The plausible-Thief set: a motion-constrained belief support, not a single argmax.

The shipped pursuit reduces belief to one cell (`Belief.most_likely`) and plans against
it. When the decode is certain that is exactly right. When it is not -- a spread window,
a silent turn, two cells of equal scent -- committing to the argmax chases a guess, and a
strong evader that keeps the belief ambiguous is never cornered (the measured 78-85%
holdout captures against `flee_smart`/`flee_interior`, versus 100% against a walk).

This module answers a narrower question than a probability model: *which cells could the
Thief actually be in right now?* Two hard filters, no recursion (the reverted Bayes
variant calcified -- `experiment_opponents._believed`):

1. **High-probability support.** The smallest set of belief cells whose mass covers
   ``mass_threshold``, capped at ``cap`` and always including the argmax. A spike on one
   cell yields a singleton -- certainty stays certain.
2. **Motion reachability.** A cell survives only if it is reachable in one legal step
   (N/S/E/W/STAY, barriers removed) from the previous plausible set. Truth about where
   the Thief *was* constrains where it can *be*, and unlike a probability product this
   cannot slowly poison the estimate: an empty intersection discards the stale history
   and falls back to the fresh support rather than zeroing a live cell.

The returned set is never empty, so a caller can always fall back to argmax behaviour.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_cop_agent.domain.board import Board
from p2p_cop_agent.domain.coordinates import Coordinate
from p2p_cop_agent.domain.movement import apply_move, legal_moves
from p2p_cop_agent.strategy.belief import Belief

#: Belief mass a plausible set must cover, and the hard cap on its size. Both are private
#: tuning: belief never crosses the wire, so no opponent can disagree with these.
DEFAULT_MASS_THRESHOLD = 0.8
DEFAULT_CAP = 6


def high_probability_cells(
    belief: Belief,
    argmax: Coordinate,
    *,
    mass_threshold: float = DEFAULT_MASS_THRESHOLD,
    cap: int = DEFAULT_CAP,
) -> tuple[Coordinate, ...]:
    """The smallest high-mass cell set covering ``mass_threshold``, argmax always in it."""
    ranked = sorted(belief.probabilities.items(),
                    key=lambda kv: (-kv[1], kv[0][0], kv[0][1]))
    chosen: list[Coordinate] = []
    covered = 0.0
    for (row, col), mass in ranked:
        if len(chosen) >= cap or covered >= mass_threshold:
            break
        chosen.append(Coordinate(row, col))
        covered += mass
    if argmax not in chosen:
        chosen.append(argmax)
    return tuple(chosen)


def motion_reachable(
    previous: frozenset[Coordinate] | None,
    board: Board,
    blocked: frozenset[Coordinate],
    support: tuple[Coordinate, ...],
) -> frozenset[Coordinate]:
    """Support cells reachable in one legal step from ``previous``; ``support`` if none are.

    ``previous`` is the plausible set from the prior turn. Expanding it by every legal
    transition and intersecting with the fresh ``support`` keeps only cells consistent
    with both the motion rules and the new scent. A first turn (``previous is None``) or a
    contradictory intersection yields the raw support -- the constraint only ever *narrows*
    a live belief, never empties it.
    """
    seed = set(support)
    if previous is None:
        return frozenset(seed)
    expanded: set[Coordinate] = set()
    for cell in previous:
        if cell in blocked:
            continue
        expanded.add(cell)  # STAY is always legal and deposits scent identically
        for action in legal_moves(board, cell, blocked):
            expanded.add(apply_move(board, cell, action, blocked))
    constrained = (expanded - blocked) & seed
    return frozenset(constrained) if constrained else frozenset(seed)


def plausible_states(
    belief: Belief | None,
    argmax: Coordinate,
    board: Board,
    blocked: frozenset[Coordinate],
    previous: frozenset[Coordinate] | None,
    *,
    mass_threshold: float = DEFAULT_MASS_THRESHOLD,
    cap: int = DEFAULT_CAP,
) -> tuple[tuple[Coordinate, ...], frozenset[Coordinate]]:
    """Return the plausible Thief cells this turn and the reachable set to carry forward.

    With no distribution (``belief is None``) the set is the single argmax, so an exact
    localization is never diluted. Otherwise it is the motion-constrained high-mass
    support, sorted row-major for a deterministic downstream tie-break.
    """
    if belief is None:
        support: tuple[Coordinate, ...] = (argmax,)
    else:
        support = high_probability_cells(
            belief, argmax, mass_threshold=mass_threshold, cap=cap)
    reachable = motion_reachable(previous, board, blocked, support)
    plausible = tuple(sorted(reachable, key=lambda c: (c.row, c.col)))
    return plausible, reachable


def belief_from(probabilities: Mapping[tuple[int, int], float] | None) -> Belief | None:
    """Adapt a raw probability map to a ``Belief`` (or ``None``), for callers holding one."""
    return None if probabilities is None else Belief(dict(probabilities))
