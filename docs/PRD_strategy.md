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
