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
| SR-013 | Four artifact families use the official filename patterns; supplied examples expose 1.1 exemplar key sets but not complete formal schemas | Official JSON examples; book PDF p. 157, table 20 | Fixture/key-set tests only |
| SR-014 | Legal actions are N/S/E/W/STAY; barriers are disclosed; current-cell barrier and trapped-Thief states capture | Book Ch. 3; Appendix E rules 13–16/46/47 | Later movement/barrier/capture tests |
| SR-015 | SHA-256 commit-reveal is mandatory; nonces stay secret until final reveal; mismatch is a zero-point technical loss | Book Ch. 5; Appendix E rules 17–19 | ADR-006 plus later crypto tests |
| SR-016 | Played-game shared JSON is byte-identical and locked; per-peer TOML stays private | Appendix B, PDF pp. 126–130; Appendix E rules 11/12 | ADR-003/004; parity/config tests |
| SR-017 | Each local peer server is reachable through a public tunnel | Appendix E rule 10 | Provider-neutral later integration |
| SR-018 | Final result is a JSON attachment; no free-text final-report body | Book Ch. 9, PDF pp. 94–95; Appendix E rules 32–34 | ADR-010; reporting tests later |
| SR-019 | Scent update is multiplicative: `max(0,(1-ρ)τ+Δτ)` | Book Ch. 4, PDF pp. 43/47 | ADR-005; later scent tests |
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

The proposed contract is `0.1.0-proposed`, **UNFROZEN**. Formal schema constraints,
MCP/envelope fields, and crypto bytes remain in
[UNKNOWN_REQUIREMENTS.md](UNKNOWN_REQUIREMENTS.md) and the relevant ADRs.
