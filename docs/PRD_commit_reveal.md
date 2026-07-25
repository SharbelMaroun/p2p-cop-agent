# PRD — Commit-Reveal

Status: cryptographic **shape `CONFIRMED`**; exact payload schema blocked by `UNKNOWN`.

## Confirmed structure (cited — book Ch.5; Appendix E rules 17–19, 24)

- Every step runs four ordered phases: **Commit → Acknowledge → Reveal → Final Audit**.
- Commit sends **only** `H_commit = SHA-256(State ‖ Move ‖ Intent ‖ Nonce)` — never the content.
- A fresh random **Nonce** (via the `secrets` module, not `random`) is generated per commit and
  kept **secret until the end-of-game audit** (rule 18).
- Payloads use **canonical serialization** (`json.dumps(sort_keys=True, separators=(",",":"))`)
  so both peers hash identical bytes; comparison uses `secrets.compare_digest`.
- At end of game both sides reveal all nonces and **recompute every commit**; any mismatch is a
  **technical forfeit, score 0, no appeal** (rule 19).
- **Step-0** before the first move: each side signs its hardware/LLM spec, code version, group,
  game number, and the GitHub commit hash (rule 24) — reported in the declaration JSON.

## Pending / UNKNOWN

- Exact commit **payload field-set**, sub-game/role sealing, and wire schema — `U-005`.
- Exact **nonce reveal timing** relative to acknowledgement — `U-005`.

No cryptographic code is authorized until the exact payload schema is `CONFIRMED`.
