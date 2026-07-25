# PRD — Cop Scent and Belief

Status: mechanism shape and Appendix F values **CONFIRMED**; equations/interfaces `UNKNOWN`.

## Confirmed structure (cited — book Ch.4 + Ch.6; Appendix E rule 23)

- Scent is **involuntary and symmetric**: each move emits a scent field centered on the agent;
  **you emit your own scent and read only the opponent's**. Scent **cannot be faked** — it is a
  byproduct of movement, which is how verbal lies are caught.
- The emission/decay model is **cryptographically locked (SHA-256) before the game** (rule 23);
  deviation cancels the game.
- The Cop maintains a **belief map** (probability matrix over the board) of the **Thief's**
  location, updated by **Bayes** with a per-hint **trust/reliability factor**; measured Thief
  scent that contradicts a verbal hint lowers that hint's trust.
- Cop role: consume **Thief-scent** observations; the pursuit policy targets the `argmax` of the
  belief map (see [PRD_strategy.md](PRD_strategy.md)).

## Confirmed values and remaining UNKNOWN details

- Scent constants (source 0.9, decay ρ 0.10, 5×5 field) are directly confirmed in
  [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md).
- Exact equation shape, normalization, trust math, observation timing, and tests remain UNKNOWN.

This repository implements Cop-side belief only; it never reads the Thief's private state.
