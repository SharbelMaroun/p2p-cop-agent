# PRD — Gatekeeper and Reporting

Status: shape, Appendix F limits, and addresses **CONFIRMED**; schemas/send mode `UNKNOWN`.

## Confirmed structure (cited — book Ch.9; Appendix A; Appendix E rules 28–30, 32–34; `PS-008`)

- All external (Gmail) calls pass through a **centralized gatekeeper** with three gates in
  series, fail-fast: **Quota manager → token-bucket rate limiter → DOS detector** (rules 28, 29).
- The token bucket refills at a configured rate below the provider quota; limits come from
  **config, never hard-coded** (`PS-006`).
- Gmail uses **OAuth 2.0 scoped to `gmail.send` only** (least privilege; rule 30); `credentials.json`
  and `token.json` are secrets and are git-ignored.
- Results are reported at the end of every legal game as a **signed JSON attachment**; free-text
  reports are rejected (rules 32–34). Both sides report separately; conflicting reports → 0/0.
- Four JSON artifacts share a `game_uid`: **declaration, configuration, log, result** (the result
  file is the emailed report); mandatory fields include both teams' four repo links, every game's
  commit hash, and total tokens consumed (rules 49, 53, 54).

## Pending / UNKNOWN

- Rate-limit values (30 rpm, 2 concurrent, 5 s, 3 retries, queue 100) are directly confirmed in
  [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md).
- The four schema-version-1.1 exemplar structures and filename patterns are confirmed in
  [ARTIFACT_TEMPLATE_BASELINE.md](ARTIFACT_TEMPLATE_BASELINE.md). Formal required/optional,
  enum, conditional, and compatibility constraints remain `UNKNOWN` (`U-002`).
- Both addresses are confirmed in `SR-012`; exact draft/send mode remains `UNKNOWN`.

No gatekeeper or reporting code is authorized until schemas and limits are `CONFIRMED`.
