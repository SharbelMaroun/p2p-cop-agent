# PRD — Cop Strategy

Status: strategy **shape `CONFIRMED`**; exact interfaces/weights blocked by `UNKNOWN`.

## Confirmed structure (cited — book Ch.6; Appendix E rule 25)

- **The move decision is always pure Python/algorithmic.** The LLM produces the **verbal layer
  only** (bluff/hint text) — it never chooses moves (rule 25; an illegal LLM move causes a
  technical loss).
- The strategy module runs **after hint-decode, before Commit**:
  `incoming hint + scent → belief update (Bayes) → move choice → LLM bluff text → commit pack`.
- Three permitted movement policies: (1) pure heuristics (Bayes + Manhattan, the default),
  (2) combined heuristics + look-ahead, (3) optional RL (Q-learning; if used, the README must
  show learning curves).
- **Cop objective:** minimize Manhattan distance to the `argmax` of the belief map; legally place
  **barriers** (one step away, truthfully declared — rules 15, 16); capture by landing on the
  Thief and declaring with cryptographic proof, or by blocking the Thief's cell / last legal move
  (rules 46, 47).
- Communication is **natural language only**; no coordinate/number protocols (rules 26, 27).

## Pending / UNKNOWN — numbers in PARAMETERS_BASELINE (pending)

- Exact move-set, barrier quota (14), step/survival limits (35), and clue word limit (15) —
  candidates in [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md), pending confirmation.
- Exact strategy interfaces, weights, fallback behavior, and LLM deadline — `U-014` / `U-008`.

Do not include Thief strategy in this repository.
