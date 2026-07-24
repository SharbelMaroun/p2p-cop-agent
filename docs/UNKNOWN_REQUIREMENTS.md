# Unknown Requirements

Shared register, byte-identical in both repositories. Each item remains `UNKNOWN` and blocks
only its affected area. Candidate numeric values (grid, scent, rate limits, series counts) are
recorded in [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md) with a "pending confirmation" flag;
an item leaves this list only when confirmed against a direct authoritative source and recorded
in [REQUIREMENTS_LEDGER.md](REQUIREMENTS_LEDGER.md).

| ID | Unknown | Blocks | Evidence needed |
|---|---|---|---|
| U-001 | Exact confirmed game/series counts (candidates: series 6, min-to-pass 2, max 10 in PARAMETERS_BASELINE) | Series/scoring | Byte-confirm the Appendix F row against the original PDF |
| U-002 | Exact JSON schemas, ownership, filenames, signing, and byte-equality rules | Configuration/reporting | Official Moodle JSON templates and book text |
| U-003 | Exact MCP tool names and message fields | Networking | Official protocol evidence or centralized verified simulator export |
| U-004 | Exact Step-0 sequence and payload ordering | Handshake | Direct official section (mandatory content confirmed as `SR-009`) |
| U-005 | Exact commit payload field-set and nonce reveal time | Cryptography | Direct official protocol text/templates |
| U-006 | Exact confirmed timeouts (candidates in PARAMETERS_BASELINE); ports are local/private choices | Networking | Byte-confirm Appendix F; ports are per-peer TOML |
| U-007 | Exact confirmed rate-limit values (candidates in PARAMETERS_BASELINE) | Gatekeeper | Byte-confirm Appendix F Table 19 |
| U-008 | Exact model or provider | LLM integration | Team choice; no official mandate found (default template = 0 tokens) |
| U-009 | Exact Gmail draft/send mode, reporting attachments, and address spelling | Reporting | Official Appendix F/table or newer announcement (see `C-004`) |
| U-010 | Whether independently duplicated stateless shared packages are permitted | Shared contracts | Official rule or lecturer clarification (see `C-007`) |
| U-013 | Exact active configuration filenames and private TOML schema | Configuration | Appendix F and official templates |
| U-014 | Exact confirmed gameplay values and modes (grid, movement, barriers, scent, survival, capture, scoring, hints, league) | Gameplay/strategy | Byte-confirm Appendices E and F (candidates in PARAMETERS_BASELINE) |
| U-015 | Centralized lecturer-simulator reverse engineering | Simulator-dependent interpretation | Import a verified export from the planning repository when available |
| U-016 | Team/group/member identifiers and 8-character team code | Identity/reporting | Verified team input |
| U-017 | Newer Moodle instructions and lecturer announcements | Potentially all areas | Obtain dated official posts |
| U-018 | Exact official Ruff course configuration | Quality tooling | Obtain current official configuration |

Resolved and removed from this list: **U-011** (README section count → `SR-008`, see `C-002`);
**U-012** (submission tag requirement → `SR-007`; the exact literal `v1.0-submission` remains
the book's example only).

Simulator-dependent protocol details remain pending on verified exports from the central
planning repository. This repository will not duplicate simulator reverse engineering.
