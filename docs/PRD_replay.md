# PRD — Replay and Verification Viewer

Status: mandatory verification viewer confirmed; runtime UI deferred.

## Confirmed behavior

- The viewer loads `log_<game_id>_g<NN>.json`, moves through the history, and
  recomputes each SHA-256 commitment from revealed data.
- A match displays `Verified OK`; any mismatch displays `TAMPERED` and invalidates
  the match.
- The README submission report includes a `Verified OK` replay screenshot.

Sources: book Ch. 7; Appendix E rule 20; `SR-008`/`SR-010`.

The official log exemplar and observed key set have already been inspected. What
remains unresolved is its complete formal validation schema and the exact commit
byte canonicalization governed by ADR-006. SHA-256 and mismatch consequences are
fixed; a particular JSON serialization is not.

This milestone may validate the 1.1 fixture but adds no replay/UI behavior.
