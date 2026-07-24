# PRD — Replay + Verification Viewer

Status: requirement `CONFIRMED` (`SR-010`; Appendix E rule 20); exact UI is an implementation choice.

## Confirmed structure (cited — book Ch.7; Appendix E rule 20)

- A **replay viewer is mandatory**. It loads the final game log (`log_<game_id>_g<NN>.json`),
  steps forward/back, and for **every step** recomputes the SHA-256 over the revealed fields and
  compares it to the stored commit.
- Match ⇒ **"Verified OK"**; any mismatch ⇒ **"TAMPERED"** and the match is **immediately
  disqualified** — a single tampered step voids the whole match (no appeal).
- A **screenshot of a "Verified OK" replay is a submission requirement** (README section 5, `SR-008`).

## Pending / UNKNOWN

- Exact log JSON field schema being verified — `U-002` (needs the official log template); the
  verification math itself is fixed by the commit-reveal contract
  (see [PRD_commit_reveal.md](PRD_commit_reveal.md)).
- Viewer framework and layout — team implementation choice.

No replay code is authorized during the requirements phase. This PRD tracks the mandatory
verification-viewer deliverable (guidelines §2.3).
