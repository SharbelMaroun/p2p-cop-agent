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
