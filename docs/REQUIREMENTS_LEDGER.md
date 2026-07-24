# Requirements Ledger

No project-book, Moodle-template, or professional-guideline requirement was promoted to `CONFIRMED` in this audit because direct readable evidence was unavailable. The rows below prevent secondary claims from being mistaken for requirements.

| ID | Requirement | Status | Mandatory/Recommended/Illustrative | Authoritative source | Exact location | Applies to | Repository impact | Test impact | Notes |
|---|---|---|---|---|---|---|---|---|---|
| REQ-REPO-001 | Two separate Cop and Thief repositories with cross-links | UNKNOWN | UNKNOWN | Official book v3.0.0 | Claimed as Ch. 9 §9.4–9.4.1; direct text unavailable | Both repos | Keep companion link; no runtime dependency | Architecture test later | Secondary planning notes only |
| REQ-ARCH-001 | Separate peers with no shared live state | UNKNOWN | UNKNOWN | Official book v3.0.0 | Claimed in project context; direct text unavailable | Both peers | Do not design shared runtime state yet | Process-isolation tests later | Simulator also behaves this way |
| REQ-CFG-001 | Exact shared/private configuration contract | UNKNOWN | UNKNOWN | Appendices/templates | Exact direct location unavailable | Both peers | Quarantine current config | No validation yet | Schema and signing process unresolved |
| REQ-NUM-001 | All board, scent, scoring, timing, rate, league, and barrier values | UNKNOWN | UNKNOWN | Appendix F | Direct table unavailable | Shared game | No values approved | Parameter tests blocked | Includes grid size and game count |
| REQ-PROTO-001 | MCP tools, messages, acknowledgements, commit/reveal fields, and capture proof | UNKNOWN | UNKNOWN | Book/templates | Direct location unavailable | Both peers | No protocol implementation | Protocol tests blocked | Simulator shapes are illustrative |
| REQ-REPORT-001 | JSON artifacts, filenames, schemas, ownership, signatures, and Gmail flow | UNKNOWN | UNKNOWN | Book/Moodle templates | Direct location unavailable | Both peers | No reporting implementation | Schema tests blocked | Recipient spelling and draft/send unresolved |
| REQ-README-001 | README academic-report sections and evidence | UNKNOWN | UNKNOWN | Book/guidelines v3.0 | Direct location unavailable | Both repos | Keep placeholders only | Documentation check blocked | Existing claim of six sections withdrawn |
| REQ-SUBMIT-001 | Package metadata, dependencies, Python version, tags, and submission procedure | UNKNOWN | UNKNOWN | Guidelines v3.0/book | Direct location unavailable | Both repos | No `pyproject.toml` or lockfile | Build gates blocked | Summary is insufficient |
| REQ-UI-001 | Live GUI and replay viewer scope | UNKNOWN | UNKNOWN | Book | Direct location unavailable | Each peer | No implementation | UI/replay tests blocked | Simulator may not be bundled |
| REQ-COP-001 | Cop pursuit, belief, scent use, barrier legality/budget, capture proof, and verbal policy | UNKNOWN | UNKNOWN | Book | Direct location unavailable | Cop repo | Preserve role-specific design placeholders | Strategy tests blocked | Task scope requires Cop-only treatment |
