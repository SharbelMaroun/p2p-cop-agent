# PRD — Cop Strategy

Status: deterministic M3 pursuit and move-or-barrier baseline implemented;
belief-aware optimization remains M6 work.

## Confirmed rules and recommendation

- Legal movement is `N`, `S`, `E`, `W`, or `STAY`; no diagonals.
- The Cop may place only legal barriers and must disclose every placement.
- Placing a barrier replaces the Police's movement for that turn: the Police gives
  up moving and instead places a barrier on either its own current cell or one
  orthogonally adjacent cell. Diagonal, more distant, off-board, duplicate, and
  over-quota targets are rejected.
- A barrier placed on the Thief’s current cell captures the Thief.
- A Thief with no legal move is captured.
- Communication is natural language only; direct numeric location protocols are
  prohibited.
- Book Ch. 6 presents algorithmic movement and a verbal LLM layer. Appendix E rule
  25 **recommends** not delegating movement to an LLM; it has no mandatory sanction
  and warns that unchecked spatial output can cause illegal moves/technical loss.

The graded mission is to replace the bundled simple baseline with a smarter
pure-Python strategy. Deterministic belief-aware pursuit/look-ahead and optional RL
are later alternatives. LLM movement remains disabled unless a future contract
revision is mutually agreed; optional low-token banter is separate. ADR-007 records
this project policy while preserving rule 25's recommendation status.

Confirmed configuration values are in
[PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md). M3 fixes barrier-aware BFS
tie-breaking and exposes both pursuit and exclusive move-or-barrier decisions through
the SDK. Belief weights, observation updates, verbal fallback behavior, and any
provider/model remain later choices. All later business logic must stay SDK-reachable.

This repository contains Cop strategy only; opponent behavior is caller-supplied in
the local rules harness and test stubs remain test-only.

## Evidence priority: what wins when scent and a hint disagree

Two sources specify this and they ask for different things. `:508` states the
obligation — a contradicted hint means the agent "**must reduce their trust level and
update their map**", two clauses joined by *and*. `:1020` states the behaviour, and its
verb matters: the pursuer "**ignores** the verbal claim and **continues** to track the
actual scent source". Not *redirects*. The pursuit does not bend at all, so the binding
test compares the target under a lie against the target having heard nothing.

The ordering is **lexicographic**, like every other policy in this repo (`M6-04`):

1. **Scent decides wherever it can.** A located peak concentrates likelihood on one
   cell; a bearing spreads it across half the board. Measured, a `0.04` trace — the
   faintest value in the book's table — outweighs a lie held at *complete* trust.
   The dominance is structural, not an effect of the trust score.
2. **The hint decides only what scent leaves open.** Given two equal peaks, scent
   cannot choose and the claim breaks the tie. Without this the verbal layer would be
   dead code; with the step above it can never overrule physical evidence.

Trust therefore does not arbitrate the contradiction — it modulates how far a claim
moves belief *within* the space scent leaves. It runs forward between turns, so a
repeated liar is believed less each time, and it is clamped to `[0, 1]`.

**Not in the sources, and not claimed as such.** There is no numbered Appendix E rule
with a sanction here — `:508` is body text, and the override falls out of the Bayesian
update rather than being decreed. Nothing defines a trust floor or an "ignore a liar
after N turns" rule. The decay schedule and the clamp are our engineering. A known
consequence we accept: because decay is multiplicative, trust approaches zero without
reaching it, so a distrusted peer can still break an exact tie. Inverting a liar's
claim would be worse — `M6-11b` holds that a liar's statement is evidence of nothing,
not evidence of the opposite, since it may still be true.

Nothing here could be adapted from the reference: it never applies a hint to belief at
all, has no trust coefficient, and logs and displays the hint without it entering the
belief update — though its own README describes a fusion it does not perform.

## Measuring the strategy: protocol and result (`M6-20`)

`inst/police_thief_p2p_Summary.md:3115` requires the report to present "the empirical
evidence for their success". It specifies **no** run count, seed policy, significance
test, or baseline — the "shipped heuristic" appears only as a config comment (`:3028`,
"else the shipped heuristic runs"), meaning the bundled default when you supply no
brain. The protocol below is therefore ours, stated in full so the number can be
reproduced or disputed. `scripts/compare_strategies.py` runs it.

**Protocol.** 7×7 at the negotiated `match_config.example.json`, survival threshold 35,
Cop and Thief started at opposite corners so the chase is not trivially short. Seeds
0–29. One opponent for every arm: a seeded random legal walk that **does not react to
the Cop**, so for a given seed every arm meets the *identical* Thief trajectory — making
this a **paired** comparison rather than two independent averages, which is a much
stronger claim and free given the design. Each actor gets its own RNG stream. The Cop
observes the real channel: the Thief's emission advances a `ScentField` and the Cop
reads the 5×5 window `M6-08` puts on the wire.

**Arms.** `blind` — a seeded random legal move, no scent and no belief. `belief` — what
we ship. `oracle` — `choose_action` against the Thief's true cell; **not a legal agent**,
included as the ceiling so a reader can see how much of the *available* gap belief
closes rather than only that it beat random.

| arm | capture rate | mean turns | mean Cop score |
| --- | --- | --- | --- |
| `blind` | 26.7% | 32.4 | 9.0 |
| **`belief`** | **96.7%** | **12.5** | **19.5** |
| `oracle` (ceiling, illegal) | 100% | 12.2 | 20.0 |

Paired: belief captured on **21** seeds the blind Cop lost, and lost **0** it won; 8 both,
1 neither. Belief closes **95.5%** of the blind→oracle gap. Stable across sample size —
belief 99.0% at n=100 and 99.7% at n=300, blind 24.0% at both.

**The caveat, stated because it changes how the number should be read.** Belief lands
near the oracle partly because the book's scent channel is generous: a 5×5 window peaks
at the emitter's own cell, so a fresh trail nearly identifies the Thief. The measurement
shows our pipeline exploits the available signal almost fully; it is *not* evidence that
the policy would hold up against a Thief that manages its trail deliberately. The
`oracle` arm is in the table precisely so this ceiling is visible rather than implied.

`test_strategy_quality.py` pins the claim — deliberately with loose bounds, so it fails
on a real regression rather than on any harmless retune. `M6-20`'s condition ("must beat
the blind baseline **or be reverted**") is only enforceable if something re-checks it.

## The tournament grid (M6-25, 2026-08-08)

The forty-seed arena above measures one opponent — a seeded random walk — and `M6-20b`'s
caveat said plainly that nothing there speaks to a Thief that manages its trail. The
opponent grid (`M9-30`) added the fleeing archetypes and found the boundary: every arm,
**oracle included**, captured the mobility-aware shapes 0/40. The tournament grid is the
protocol that measured the fix and now guards it:

- **Arms.** `barrier_stack` (the former live stack), `shrink_stack` (the live stack:
  decoded belief, trap → squeeze → containment → interception chase), `oracle_shrink`
  (the same stack aimed with referee truth — the structural ceiling, not a legal agent).
- **Archetypes.** `random` (reference floor), `flee_greedy` (reference shape),
  `flee_smart` (distance + mobility), `flee_deadend` (dead-end refusal first — the
  companion repository's shipped shape, i.e. the strong classmate), `flee_territory`
  (maximise the sooner-reached pocket — the strongest simple evader definable here).
- **Design.** Forty paired seeds, identical Thief trajectory per seed across arms,
  deterministic everything; run at the negotiated 7×7 and re-run at 9×9 because every
  board parameter is an Appendix-F *minimum*, not a constant.
- **Result** (`results/tournament_grid.json`, `results/tournament_grid_9x9.json`):
  `shrink_stack` **40/40 on every cell of both boards**, equal to `oracle_shrink`
  everywhere — the interception chase (sum of barrier-aware distances over the whole
  flight set, then the worst single one) is the entire difference; the wall layers are
  unchanged.
- **Guard.** `test_tournament_quality.py` binds it at ten seeds: ≥9/10 on both
  mobility-aware archetypes, no archetype the incumbent converts surrendered, decoded
  belief equal to the truth-fed stack on every cell, captures decisively inside the
  horizon, and the measurement reproducible.

A guarded territory-shrink wall layer was designed, built, and **measured off** on the
way (flee_greedy 10/10 → 0/10): fourteen walls that each shave one cell are fourteen
turns of not chasing. The dead design is recorded in `strategy/shrink.py`'s docstring so
it is not rediscovered.
