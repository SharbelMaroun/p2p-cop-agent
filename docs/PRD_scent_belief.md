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

Belief normalization, trust math, observation timing, interfaces, and pursuit
weights are future Cop strategy decisions. This milestone adds configuration and
contract validation only, not scent or belief runtime behavior.
