# PRD — Cop Strategy

Status: strategy **shape `CONFIRMED`**; exact interfaces/weights blocked by `UNKNOWN`.

## Confirmed structure and recommendation

- Book chapter 6 describes movement decisions as algorithmic and the LLM as the verbal layer.
  Appendix E rule 25 **recommends** not delegating move decisions to the LLM and using it only
  for text processing and behavioral-profile generation. Rule 25 has no mandatory sanction; it
  warns that blind reliance can cause illegal moves and technical loss (original PDF p. 146 /
  printed p. 130).
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

## Confirmed values and remaining UNKNOWN details

- The move-set, barrier quota (14), step/survival limits (35), and clue word limit (15) are
  directly confirmed in [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md).
- Exact strategy interfaces, weights, fallback behavior, and provider/model choice remain UNKNOWN.

Do not include Thief strategy in this repository.
