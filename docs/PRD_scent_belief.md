# PRD — Cop Scent and Belief

Status: scent physics and Cop-local truth boundary confirmed; belief algorithm/API
deferred.

## Confirmed behavior

- Both agents emit scent and observe only the opponent’s scent. Scent is involuntary
  and cannot be replaced by a verbal claim.
- The emission/decay model is agreed and cryptographically locked before play.
- Book Ch. 4 defines the multiplicative update
  `τᵢⱼ(t+1) = clamp(0, (1-ρ)·τᵢⱼ(t) + Δτᵢⱼ, 0.9)` — the printed `max(0, …)` plus the upper
  bound chapter 4 states separately when it declares τ continuous in `[0, 0.9]` (`C-048`).
- Fixed values are center intensity `0.9`, decay `ρ=0.10`, and a 5×5 field.
- The Cop maintains only its local belief about the Thief; it never reads Thief
  private state.

The lecturer simulator’s subtractive decay is a reference deviation and must not be
copied. ADR-005 records the source-backed multiplicative model.

## The emission profile and its lock (`M6-01a`, `M6-07`, added 2026-08-05)

Book Figure 4 names **six** radial classes covering all 25 cells, by squared distance
from the emitter: centre `0.90`, cross `0.62`, diagonal `0.42`, mid-side `0.20`, the
eight `(±1,±2)`/`(±2,±1)` cells `0.14`, corner `0.04`.

**This section was wrong until 2026-08-08 and the correction is worth reading.** It said
the figure named five classes covering 17 cells, with diagonal `0.20` and mid-side
`0.14`, and treated the remaining eight as a negotiated gap. Those numbers are the true
values of the *next two rings out*: the whole table was the correct curve **shifted
inward by one radial class**. That is why the endpoints (`0.90`, `0.62`, `0.04`) matched
the source exactly while the middle did not, and why eight cells appeared unnamed — the
shift had consumed the class that owns `0.14`.

The correction is confirmed three ways: the book PDF states it directly; a zero-parameter
fit of `τ = 0.9·exp(−k·d²)` through the two agreed values (centre `0.90`, cross `0.62`)
reproduces `0.427 / 0.203 / 0.140 / 0.046`, matching to two decimals; and a classmate team
reproduced the same kernel independently. `test_scent.py` now pins the curve as well as
the table, so a future shift fails without needing a source to argue with.

The source of the error was our own reading rule applied backwards. The old values came
from `inst/police_thief_p2p_Summary.md:947-955` — a **translation** — and the corrected
ones were rejected on 2026-08-05 because they arrived via a notebook. The notebook holds
the PDF. A restatement is not the source, whichever direction it points.

`DEFAULT_OUTER_RING_DELTA` (`0.14`) now carries book authority; the parameter remains
only so a peer insisting on a different ring can still be met and locked. Emitting all 25
is also required for interoperability: the reference emits 25 and asserts a snapshot
length of 25, so absent cells read to an opponent as zeros.

The whole model is canonicalised and SHA-256 locked (`strategy/scent_lock.py`):

```text
model                                = "multiplicative-decay"
update                               = "tau_next = min(max(0, (1 - decay_per_step) * tau + emission), center_intensity)"
center_intensity                     = 0.9
decay_per_step                       = 0.10
field_size                           = 5
emission_profile_by_squared_distance = {"0":0.90,"1":0.62,"2":0.42,"4":0.20,"5":0.14,"8":0.04}
```

Comparing the three Appendix F constants alone cannot catch this: two peers can hold
identical `smell_grid_size`/`decay_per_step`/`emit_intensity` and still emit different
fields, because the formula and the radial profile never cross the wire on their own.

The lock rides **beside** the signed terms, and is checked leniently in one direction:
an opponent publishing **no** lock is still played, one publishing a **different** lock
is refused. The reference publishes none — it folds pheromone terms into `config_sha256`
— so requiring one would refuse every simulator-built classmate over a message they
never send, and rule 23 sanctions a *deviation from the formula*, not a silence. This is
the same `U-029`/`C-031` rule already settled for `config_sha256`.

Its digest `c77a12609b9f1c3df90067ce166b6b0455c8343dba9d463b0e8e402f8469b34f` is
reproduced exactly by the independently written companion Thief peer, which is the only
real evidence that locking a model achieves anything.

## The belief update rule and its trust factor (`M6-14a`, added 2026-08-07)

Everything in this section is **PROJECT-PROPOSED**. The book fixes the *shape* — Bayes
with a reliability factor (`:1480`) — and the *evidence* — expected-versus-measured scent
where the claim points (`:1007-1022`). It states no starting trust, no step size, no
decay rate, no bound, and says outright that the translation into a numeric belief map is
the agent's own (`:1025`). Belief never crosses the wire (`M6-18`), so unlike the
hash-locked scent model above there is no opponent to disagree with these numbers, and
none of them is interop-critical.

**The update.** `posterior(c) ∝ prior(c) · likelihood(c)`, renormalised so the
distribution sums to 1. Three properties are deliberate and each exists because of a way
the naive version breaks:

| property | value | why |
| --- | --- | --- |
| zero total evidence | return the prior unchanged | an observation supporting no cell must not divide by zero and destroy a valid distribution (`M6-02c`) |
| negative likelihood | clipped to `0` | evidence cannot be less than absent |
| tie in `most_likely` | row-major order | the argmax must be deterministic, or two replays of one log disagree |

**The inputs.** Only the observed opponent scent field and, second, a decoded hint.
Never the Thief's true cell — `scent_likelihood` takes the observed mapping and the grid
size and has no parameter through which a position could enter (`M6-02d`).

**Normalisation, in two places that are easy to confuse.** The *likelihood* is not
normalised; it is `floor + observed(c)` with `DEFAULT_LIKELIHOOD_FLOOR = 0.01` on every
cell, so no cell the Thief could still occupy is ever hard-zeroed and no later evidence
can resurrect it. The *posterior* is normalised, by construction. A likelihood that
summed to 1 would make the floor meaningless, since scaling a likelihood by a constant
leaves the posterior identical.

**The trust factor.** `TrustScore` on `[0, 1]`, neutral prior, `TRUST_UPDATE_RATE = 0.25`.
Trust does **not** arbitrate a scent-versus-hint contradiction — `PRD_strategy.md` covers
that ordering. It scales how far a claim moves belief *within* what scent leaves open:

```text
support     = min(1, measured_at_favoured_cells / expected_fresh_scent)   # on [0, 1]
expected_fresh_scent = CENTER_INTENSITY * (1 - DECAY_RATE) = 0.9 * 0.9 = 0.81
strength    = |support - 0.5| / 0.5
trust_next  = reinforced(0.25 * strength)  if support > 0.5  else weakened(0.25 * strength)
L_eff(c)    = t * L(c) + (1 - t) * mean(L)
```

Four things in those five lines are chosen rather than derived, and are worth naming:

- `expected_fresh_scent` is **computed from the locked model's own constants**, not typed
  in as `0.81`. A negotiated change to centre intensity or decay carries it along instead
  of leaving it silently disagreeing with the field it is compared against.
- Support uses the **strongest** favoured cell, not the mean. A direction names a
  half-plane and the Thief is in one cell of it; averaging would dilute a real fresh trail
  to nothing on a large board, so a truthful hint would read as a lie.
- The step is **scaled by distance from neutral**, so the case study's absolute
  contradiction (`0.00` measured against `0.81`) moves trust at the full rate while a
  marginal disagreement barely moves it. A flat rate would treat those identically.
- `L_eff` tempers **toward uniform**, never toward the opposite. At `t = 0` the hint
  flattens to a constant, which Bayes treats as no evidence — the case study's "ignores
  the verbal claim", by arithmetic rather than a special case. Inverting a liar's claim
  would be wrong: it may still be true (`M6-11b`).

A consequence we accept rather than hide: `reinforced`/`weakened` are bounded steps that
approach `1.0` and `0.0` without arriving, so a repeat liar keeps a sliver of trust and
can still break an exact tie. Bluffing is legal in this game, and a peer condemned beyond
appeal could never rebuild.

Observation timing, interfaces, and pursuit weights are covered in
[PRD_strategy.md](PRD_strategy.md).

## The observation on the wire (`M6-08`, `M6-09`, added 2026-08-06)

**Shape.** A JSON object keyed `"row,col"` — row first, the same axis order as a
position — mapping to numbers. What travels is a **5×5 window of this peer's own
accumulated trail**, centred on its current cell and clipped to the board: not the bare
one-turn emission, and not the whole board. That is the reference's shape, confirmed
against its `SmellField.snapshot()`.

**Emission is involuntary by construction.** `ScentField.advance` takes a **cell** and
nothing else — no action, no flag, no provider. A `STAY` deposits exactly as a move
does, because there is no parameter a caller could set to stay silent. The book is
explicit (`inst/police_thief_p2p_Summary.md:895`): the scent "is emitted by the
**movement or the stay itself**, and no agent can plant a misleading trail — each side
emits its own scent, and each side reads the scent field of its opponent only."

**Order follows the book, not the reference.** The update is decay-then-add,
`τ(t+1) = max(0, (1−ρ)·τ(t) + Δτ)`; the reference deposits first and decays the whole
field afterwards, which yields `(τ + Δτ)(1−ρ)` and quietly attenuates the fresh deposit.
Per `C-009` the book governs, so a cell just stepped on reads the full `0.9` — which is
what the chapter 4.4 worked example assumes when it predicts `0.81` for a
**one-turn-old** trail.

**Precision.** Six decimal places on send. Repeated decay produces
`0.7290000000000001`, whose textual form is implementation-dependent. This is a
**send-side choice only** — parsing accepts any precision, because tightening what we
emit cannot break a peer while tightening what we accept can.

> **Correction.** The `M6-08c` DoD, and the companion Thief's `M6-006c` row, both claimed
> byte-identical serialisation is "the property the locked scent-model hash depends on".
> **It is not.** `scent_model_record()` contains exactly `model`, `update`,
> `center_intensity`, `decay_per_step`, `field_size`, and
> `emission_profile_by_squared_distance` — the *model*, never an emitted value. Verified
> by inspection on 2026-08-06. Rounding cannot invalidate a lock, and no interop property
> rests on it.

**Parsing is hostile-input handling.** The grid comes from an opponent, so eleven shapes
are refused by name: malformed keys, non-string keys, non-numeric and boolean values,
NaN, infinity, negatives, off-board cells, and values above the model's saturation
limit. A corrupt grid **raises** rather than degrading to empty — scent is the one
channel that cannot be faked, so silently reading a corrupt one as "no evidence" would
discard the strongest signal available.

**The saturation bound, and how this paragraph was wrong (`C-048`).** It used to argue that
capping intensity at `0.9` "is wrong and would have rejected *our own* emissions", citing a
two-turn trail reaching `1.458` and deriving a real ceiling of `Δτ/ρ = 9.0`. Every number in
that argument was correct and the conclusion was backwards: a peer refused us on 2026-08-15
for publishing `1.43` at exactly such a cell, and Appendix E rule 23 backs them — chapter 4
declares τ continuous in `[0, 0.9]`, so a value above the centre intensity contradicts the
model's own stated range. `U-031` is **CLOSED**: the update clamps.

What the old paragraph got right is worth keeping. An agent standing still *does* accumulate
under the printed formula, and unclamped it converges to `9.0`. That is the reason the clamp
is needed, not a reason to refuse it — the argument inverted itself by treating our own
emissions as the thing to protect rather than the thing to check. The **parser** stays
tolerant on receive: a peer that publishes above the ceiling is refused by its own declared
model, not by our reading of it.

**Cross-peer note (corrected `C-052`).** The Cop sends the whole accumulated trail, which is
what the reference transmits — `Trail.full_turn` decays the persistent field in place and
`snapshot()` returns every cell still carrying something. It sent a 5×5 *window* until
2026-08-16, described here as "matching the reference", which it did not: `smell_grid_size`
sizes the emission kernel, not the transmitted dict. The companion Thief sends a sparse map
with zeros omitted. Both peers parse
both forms — verified by round-tripping each encoder through the other's parser on
2026-08-06 — because an absent cell and a zero cell mean the same thing. The divergence
is stylistic and is recorded rather than churned.

