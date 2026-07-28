# Requirements Ledger

`CONFIRMED` means directly supported by the cited authority. Confirmed requirements
do not make an unfrozen design choice mandatory; exact design choices require an
accepted ADR.

| ID | Confirmed requirement | Direct authority | Repository/test impact |
|---|---|---|---|
| SR-001 | One Cop repository and one Thief repository | Book Ch. 9 §9.4; Appendix C | Independent repository checks |
| SR-002 | Each README links to the companion repository | Book Ch. 9 §9.4; Appendix C | Link test/review |
| SR-003 | Both repositories are accessible to the lecturer | Appendix C §1 | Submission access check |
| SR-004 | Peers run as separate processes/configuration environments with no shared live state or opponent private truth | Book Ch. 2 §2.4.2 | Isolation and dependency tests |
| SR-005 | Each peer is both FastMCP server and client | Book Ch. 2 §2.3 | Later integration tests; names remain ADR-owned |
| SR-006 | Each repository has README, config, PRDs, PLAN, TODO, and code | Book Ch. 9 §9.4; Appendix E rule 50 | Structure check |
| SR-007 | Submission is marked with an annotated Git tag | Appendix E rule 41; Appendix C | Tag check; literal remains Moodle-sensitive |
| SR-008 | README academic report has six sections; section 6 is the companion link | Book Ch. 9 §9.4.2, PDF p. 97; Appendix E rule 42 | README section check |
| SR-009 | One Orchestrator gateway, explicit state machine/illegal-transition rejection, deadlines, and watchdog | Book Ch. 2/8; Appendix E rules 3–7 | Later state/watchdog tests |
| SR-010 | Live local-truth GUI and replay/SHA-256 verification viewer are mandatory | Book Ch. 7; Appendix E rules 8/9/20 | Later GUI/replay tests and screenshots |
| SR-011 | Confirmed game/scoring/league/Gatekeeper values and statuses are those in `PARAMETERS_BASELINE.md` | Appendix F tables 13–19, PDF pp. 152–155 | File-backed configuration validation |
| SR-012 | General/repository email is `rmisegal@gmail.com`; automated-report email is `rmisegal+uoh26finalgame@gmail.com` | Book PDF p. 157, table 20 | Address tests |
| SR-013 | Four artifact families use the book-defined filename patterns; local simulator-generated artifacts expose non-authoritative 1.1 key-set observations | Book PDF p. 157, table 20; local files classified `NEEDS_MANUAL_REVIEW` | Filename checks plus observation-fixture metadata only |
| SR-014 | Legal actions are N/S/E/W/STAY; barriers are disclosed; current-cell barrier and trapped-Thief states capture | Book Ch. 3; Appendix E rules 13–16/46/47 | Later movement/barrier/capture tests |
| SR-015 | SHA-256 commit-reveal is mandatory; per-turn commitment nonces stay secret until final reveal; mismatch is a zero-point technical loss | Book Ch. 5; Appendix E rules 17–19 | ADR-006 plus later crypto tests; public negotiation challenges are a separate domain |
| SR-016 | Played-game shared JSON is byte-identical and locked; per-peer TOML stays private | Appendix B, PDF pp. 126–130; Appendix E rules 11/12 | ADR-003/004; explicit per-match loading and parity/config tests |
| SR-017 | Each local peer server is reachable through a public tunnel | Appendix E rule 10 | Provider-neutral later integration |
| SR-018 | Final result is a JSON attachment; no free-text final-report body | Book Ch. 9, PDF pp. 94–95; Appendix E rules 32–34 | ADR-010; reporting tests later |
| SR-019 | Scent update is multiplicative: `max(0,(1-ρ)τ+Δτ)` | Book Ch. 4, PDF pp. 43/47 | ADR-005; later scent tests |
| SR-020 | A played series has six sub-games and scores aggregate per stable group identity | Appendix F table 18 | Runtime in M7; the within-series role schedule remains non-binding `U-025`/`OB-005` |
| SR-021 | `agreed_between` is an ordered JSON list of the two participating group IDs; its mutually agreed order is preserved exactly | Appendix B example, printed p. 113; supplied agreed config; owner-supplied lecturer direction dated 2026-07-27 | Source-config schema and mismatch tests |
| SR-022 | `config_sha256` hashes the complete shared per-match game object using sorted keys, compact separators, unescaped Unicode as UTF-8, and SHA-256; the claim lives in the generated config artifact, outside the hashed object | Appendix B canonical-JSON text; owner-supplied lecturer direction dated 2026-07-27; pinned simulator and supplied vector corroborate | Canonical config vector and explicit-path verification boundary |
| SR-023 | Every artifact family carries `game_id`, a UUID `game_uid`, and `links`; hardware is declared before play and sealed in the step-0 evidence | Owner-supplied lecturer direction dated 2026-07-27; all four supplied files and step-0 record directly observed | Artifact identity/lifecycle contract; complete formal schemas remain open |
| SR-024 | The graded strategy replaces the simple baseline with smarter pure-Python move logic; LLM movement stays disabled unless explicitly agreed in a future match-contract revision | Owner-supplied lecturer direction dated 2026-07-27; Appendix E rule 25 and pinned simulator strategy docs corroborate the safe default | Strategy work remains deferred to M6 |
| SR-025 | Step-0 seals host OS/CPU/RAM/GPU/VRAM, model, code/group/game identity, and the exact running Git commit before moves | Book Ch. 5 §5.5; Appendix E rule 53 | M4 wire contract and M7 artifact propagation |
| SR-026 | Gmail OAuth `credentials.json` and generated `token.json` stay runtime-local and ignored | Book Appendix A, printed pp. 105-109; Appendix E rules 39-40 | Ignore/secret checks now; runtime deferred |
| AE-025 | Not delegating movement to an LLM is a recommendation without a mandatory sanction | Appendix E rule 25, PDF p. 146 | ADR-007 deterministic default |
| COP-001 | This repository is Cop-only and never imports Thief private runtime code | Team role assignment plus SR-004 | Dependency/import scan |
| PS-001 | Maintain README, PRD, PLAN, TODO, and mechanism PRDs | Professional Guidelines v3.0, pp. 7–9 | Documentation checks |
| PS-002 | Use `uv`, `pyproject.toml`, and committed `uv.lock` | Professional Guidelines v3.0, pp. 19–20 | Frozen-install check |
| PS-003 | Code and tests stay within 150 nonblank/noncomment lines | Professional Guidelines v3.0, p. 10 | Length checker |
| PS-004 | Use TDD, failure-path tests/mocks, and at least 85% global coverage | Professional Guidelines v3.0, pp. 15–16 | Pytest branch-coverage gate |
| PS-005 | Ruff passes with zero violations under the controlling course configuration | Professional Guidelines v3.0, p. 17 | Ruff gate |
| PS-006 | Configurable values are file-backed and secrets never enter Git | Professional Guidelines v3.0, pp. 17–18 | Secret/config checks |
| PS-007 | CLI/GUI/MCP/integrations delegate business logic through SDK/service boundaries | Professional Guidelines v3.0, p. 11 | Boundary tests/review |
| PS-008 | External APIs use one Gatekeeper with limiting, FIFO, backpressure, retry, and monitoring | Professional Guidelines v3.0, pp. 13–14 | Gatekeeper tests later |
| PS-009 | Maintain `docs/PROMPT_LOG.md` | Professional Guidelines v3.0, p. 19 | Presence/provenance check |
| PS-010 | Code, shared JSON, and rate-limit configuration revisions begin at `1.00` and validate supported versions independently of schema profiles | Professional Guidelines v3.0 section 8.1, p. 19 | Version/config contract tests |
| OB-001 | The project selects Option B (simulator-v3 profile) as a documented academic-freedom interoperability choice where the book leaves wire details open | Coordinator project decision dated 2026-07-28; [OPTION_B_DECISION.md](OPTION_B_DECISION.md) | Current `0.2.3-proposed` bundle; conformance suite |
| OB-002 | Interoperability is pinned to simulator commit `960499fd5e8777b4929625f5d8fdcf2ab4677b54`; the simulator is a wire reference, not a source to copy | Coordinator project decision dated 2026-07-28; ADR-008 governs reuse | Behavioural parity target; import scan |
| OB-003 | Exposed FastMCP tools are `negotiate`, `receive_turn`, `submit_audit`, and optional `receive_control`; `exchange_audit` is only a client transport method, `receive_move` is excluded, and wire roles are `police`/`thief` | ADR-001 accepted under Option B | Protocol schemas and conformance tests |
| OB-004 | Per-turn commitment is `sha256(canonical_json(payload) + "\|" + nonce)` with a literal `\|` delimiter; the commitment nonce is 16 random bytes as 32 lowercase hex, outside the payload, revealed only in the post-game audit | ADR-006 per-turn commitment accepted under Option B | Canonicalization vectors (WP5) |
| OB-005 | **UNKNOWN — NOT BINDING.** A six-sub-game series and stable group identity are confirmed, but the *role schedule* within the series (natural role on odd games, opposite role on even games) is not. Series orchestration must stay role-agnostic until authenticated. | Appendix F table 18 confirms only the six-sub-game count and aggregation; the alternation schedule itself is simulator-observed and is **not** book-confirmed, nor supported by an authenticated Moodle announcement or original lecturer message. Tracks [U-025](UNKNOWN_REQUIREMENTS.md) | Removed from the contract bundle in `0.2.1-proposed`; no normative test until authenticated |
| OB-006 | `negotiate.nonce` is a public pre-play negotiation challenge, distinct from the secret per-turn commitment nonce even though both use 32 lowercase hexadecimal characters | Owner confirmation dated 2026-07-28; [OPTION_B_DECISION.md](OPTION_B_DECISION.md) | Schema purpose/visibility annotations and independent leak-rejection tests |

The previous `0.1.0-proposed` bundle was rejected. The active proposed contract is
`0.2.3-proposed`, **UNFROZEN**, built as the role-neutral top-level
`shared_contract/` subtree. It preserves the `0.2.1` barrier/role-schedule repairs
and the `0.2.2` schema/cross-field repairs, while fixing explicit runtime input and
nonce-domain semantics. It supersedes all earlier proposed byte sets. Remaining
formal artifact schema constraints stay in
[UNKNOWN_REQUIREMENTS.md](UNKNOWN_REQUIREMENTS.md) and the relevant ADRs. Freezing or
copying `0.1.0-proposed` is not authorized.
