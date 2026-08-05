# PRD — Cop Scent and Belief

Status: scent physics and Cop-local truth boundary confirmed; belief algorithm/API
deferred.

## Confirmed behavior

- Both agents emit scent and observe only the opponent’s scent. Scent is involuntary
  and cannot be replaced by a verbal claim.
- The emission/decay model is agreed and cryptographically locked before play.
- Book Ch. 4 defines the multiplicative update
  `τᵢⱼ(t+1) = max(0, (1-ρ)·τᵢⱼ(t) + Δτᵢⱼ)`.
- Fixed values are center intensity `0.9`, decay `ρ=0.10`, and a 5×5 field.
- The Cop maintains only its local belief about the Thief; it never reads Thief
  private state.

The lecturer simulator’s subtractive decay is a reference deviation and must not be
copied. ADR-005 records the source-backed multiplicative model.

## The emission profile and its lock (`M6-01a`, `M6-07`, added 2026-08-05)

Book Figure 4 (`inst/police_thief_p2p_Summary.md:947-955`) names five radial classes —
centre `0.90`, cross `0.62`, diagonal `0.20`, mid-side `0.14`, corner `0.04` — which
cover **17 of the 25** cells. The remaining eight, at offsets `(±1,±2)`/`(±2,±1)`, are
named by no source. `DOCUMENTED_EMISSION` holds the 17 and nothing else, so a value the
peers merely agreed can never be mistaken for one the book states.

Those eight are a **negotiated parameter**, not a private constant and not a gap.
`DEFAULT_OUTER_RING_DELTA` (`0.04`) carries **no book authority**; it is our opening
offer. Emitting them at all is required for interoperability: the reference emits all
25 and asserts a snapshot length of 25, so eight absent cells read to an opponent as
eight zeros.

The whole model is canonicalised and SHA-256 locked (`strategy/scent_lock.py`):

```text
model                                = "multiplicative-decay"
update                               = "tau_next = max(0, (1 - decay_per_step) * tau + emission)"
center_intensity                     = 0.9
decay_per_step                       = 0.10
field_size                           = 5
emission_profile_by_squared_distance = {"0":0.90,"1":0.62,"2":0.20,"4":0.14,"5":0.04,"8":0.04}
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

Its digest `416a57e17434ef21b3209052198a27a0d46e7a0e09fdaa5df3b61e4a8f2711ea` is
reproduced exactly by the independently written companion Thief peer, which is the only
real evidence that locking a model achieves anything.

Belief normalization, trust math, observation timing, interfaces, and pursuit
weights are future Cop strategy decisions.

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

**The saturation bound is derived, not chosen.** An earlier parser capped intensity at
the centre intensity `0.9`. That is wrong and would have rejected *our own* emissions:
the update is additive, so an agent standing still accumulates, and a two-turn trail
already reaches `1.458`. The real ceiling is the fixed point of `τ = (1−ρ)τ + Δτ`, i.e.
`Δτ/ρ = 9.0`. `U-031` — whether re-emission should instead clamp at `0.9` — remains
open, and the parser deliberately does **not** assume the clamp, because assuming it
would refuse a peer following the formula as written.

**Cross-peer note.** The Cop sends the full window including silent cells (matching the
reference); the companion Thief sends a sparse map with zeros omitted. Both peers parse
both forms — verified by round-tripping each encoder through the other's parser on
2026-08-06 — because an absent cell and a zero cell mean the same thing. The divergence
is stylistic and is recorded rather than churned.

