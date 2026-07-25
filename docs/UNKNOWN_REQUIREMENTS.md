# Unknown Requirements

Each item remains `UNKNOWN` and blocks only its affected area. Appendix F numerical values are
directly confirmed in [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md); schemas and protocol
details are separate and are not inferred from those values.

| ID | Unknown | Blocks | Evidence needed |
|---|---|---|---|
| U-002 | Formal JSON validation rules: required/optional fields, complete types/enums, conditional constraints, and compatibility behavior | Configuration/reporting | Referenced `artifact_schemas.py`, validation fixtures, or formal JSON Schema; exemplar key sets are confirmed |
| U-003 | Exact MCP tool names and message fields | Networking | Official protocol evidence or centralized verified simulator export |
| U-004 | Exact Step-0 sequence and payload ordering | Handshake | Direct official section (mandatory content confirmed as `SR-009`) |
| U-005 | Exact commit payload field-set and nonce reveal time | Cryptography | Direct official protocol text/templates |
| U-008 | Exact model or provider | LLM integration | Team choice; no official mandate found (default template = 0 tokens) |
| U-009 | Exact Gmail draft/send mode and reporting attachments | Reporting | Official templates or newer announcement; both addresses are confirmed |
| U-010 | Whether independently duplicated stateless shared packages are permitted | Shared contracts | Official rule or lecturer clarification (see `C-007`) |
| U-013 | Exact private TOML schema and mapping into the confirmed agreed-config artifact | Configuration | In-code schema/configuration evidence |
| U-015 | Centralized lecturer-simulator reverse engineering | Simulator-dependent interpretation | Import a verified export from the planning repository when available |
| U-016 | Team/group/member identifiers and 8-character team code | Identity/reporting | Verified team input |
| U-017 | Newer Moodle instructions and lecturer announcements | Potentially all areas | Obtain dated official posts |
| U-018 | Exact official Ruff course configuration | Quality tooling | Obtain current official configuration |

Resolved and removed from this list: **U-001**, **U-006**, **U-007**, and **U-014** (direct
Appendix F extraction); **U-011** (README section count → `SR-008`); **U-012** (submission tag
requirement → `SR-007`). The address portion of **U-009** is also resolved.

Simulator-dependent protocol details remain pending on verified exports from the central
planning repository. This repository will not duplicate simulator reverse engineering.
