# Deterministic Pursuit Baseline

Status: **IMPLEMENTED — CONTRACT-INDEPENDENT**

Scope: `src/p2p_cop_agent/strategy/pursuit.py`, reachable through
`CopSDK.choose_pursuit_action`.

This is the M3-05 movement policy, initially delivered as a narrowly scoped
contract-independent increment and now part of completed M3. It uses only public
domain APIs, defines no new game
rule, performs no I/O, and changes no shared-contract byte. It is independent of
the contract gate: nothing here waits on `0.2.8-proposed` review.

## What the policy does

Given the board, the Cop's cell, a presumed Thief cell, and the disclosed
barrier set, it returns the legal `Action` that most reduces the barrier-aware
distance to the target.

## Recorded decisions

| Decision | Choice | Why |
|---|---|---|
| Target input | An explicit `Coordinate` supplied by the caller | Scent and belief are later M6 work. The policy must not infer opponent position, so inference stays outside this layer. |
| Action space | Movement only | This API remains the movement primitive. Completed M3-06 composes it with exclusive barrier placement through `choose_turn_intent`. |
| Distance metric | Barrier-aware breadth-first step count | A plain row/column difference ignores barriers, so the Cop could prefer a route that is blocked. BFS uses the barrier-aware movement rules already implemented in M2. |
| Tie-breaking | Fixed `Action` declaration order (`N`, `S`, `E`, `W`, `STAY`) | Fully deterministic and independent of dictionary or set iteration order. Identical inputs always produce an identical action. |

## Edge cases

- **Already on the target.** `STAY` is strictly best and is returned.
- **Sealed off from the target.** When barriers or board edges make the target
  unreachable, the policy returns `STAY` rather than wandering. This is a
  documented choice, not a forced one: a future revision could prefer
  repositioning instead.
- **Off-board inputs** are rejected by `Board.require_on_board`.
- **Legality.** Every candidate comes from `legal_moves`, so the returned action
  is always legal. `STAY` is legal for any on-board cell, so an action always
  exists.

`STAY` is last in the tie-break order, but on a grid it never merely ties: the
cell graph is bipartite, so an adjacent cell's distance always differs from the
current cell's by exactly one. `STAY` therefore wins only in the two cases
above.

## What this is not

- Not a strategy for the full game: no scent, no belief, no opponent modelling,
  no series awareness.
- Not protocol- or transport-aware.
- Not a decision about capture-reason precedence or live-turn event ordering;
  both remain provisional.

## Verification

20 focused tests (`tests/unit/test_pursuit.py`, `tests/unit/test_sdk_pursuit.py`)
cover direction, tie-breaking, barrier-aware routing where a naive metric would
choose differently, the sealed-off fallback, legality of every returned action,
repeatability, and off-board rejection. `pursuit.py` holds 100% statement and
branch coverage.
