# Shared Requirement Baseline

This is a source-backed baseline, not proof of cross-repository byte parity. The
current proposed contract is `0.2.9-proposed` and **UNFROZEN** until independent peer
acceptance and matching controlled hashes are demonstrated.

| ID | Confirmed shared requirement | Direct source |
|---|---|---|
| SR-001–003 | Separate Cop/Thief repositories, reciprocal README links, and lecturer access | Book Ch. 9 §9.4; Appendix C |
| SR-004 | Separate processes/configuration environments; no shared live state or opponent private truth | Book Ch. 2 §2.4.2 |
| SR-005 | Each peer is both a FastMCP server and client | Book Ch. 2 §2.3 |
| SR-006–008 | Required repository content, annotated submission tag, and six README report sections | Book Ch. 9; Appendix C; Appendix E rules 41/42/50 |
| SR-009 | Single Orchestrator gateway, explicit illegal-transition rejection, deadlines, and watchdog | Book Ch. 2/8; Appendix E rules 3–7 |
| SR-010 | Live local-truth GUI and replay/SHA-256 verification viewer | Book Ch. 7; Appendix E rules 8/9/20 |
| SR-011 | Binding values/statuses are those directly recorded in `PARAMETERS_BASELINE.md` | Appendix F tables 13–19 |
| SR-012 | Canonical general and automated-report addresses are distinct | Book PDF p. 157, table 20 |
| SR-013 | Four artifact families and book-defined filename patterns are known; local generated artifacts expose non-authoritative 1.1 key-set observations | Book table 20; local files classified `NEEDS_MANUAL_REVIEW` |
| SR-014 | Moves are N/S/E/W/STAY only; barriers are disclosed; current-cell barrier and trapped-Thief conditions capture | Appendix E rules 13–16/46/47; book Ch. 3 |
| SR-015 | SHA-256 commit-reveal is mandatory; each per-turn commitment nonce stays secret until final reveal; mismatch is a technical loss worth zero | Book Ch. 5; Appendix E rules 17–19 |
| SR-016 | Played-game shared JSON is byte-identical and locked; private per-peer TOML remains local | Appendix B; Appendix E rules 11/12 |
| SR-017 | Each local server is exposed through a public tunnel; no provider is mandated here | Appendix E rule 10 |
| SR-018 | Final report is a JSON attachment with no free-text final-report body | Book Ch. 9; Appendix E rules 32–34 |
| SR-019 | Scent update is multiplicative, not the simulator’s subtractive variant | Book Ch. 4, PDF pp. 43/47 |
| AE-025 | Algorithmic movement is the safe default; rule 25 is a recommendation without a mandatory sanction | Appendix E rule 25, PDF p. 146 |
| PS-001–010 | Mandatory docs; `uv`; line/TDD/coverage/Ruff/secrets/SDK/Gatekeeper/prompt-log/version gates | Professional Software Submission Guidelines v3.0 |

Option B fixes the project MCP names and per-turn commitment serialization/nonce
length; the public `negotiate.nonce` challenge is a separate domain. Remaining
envelope/error details and other non-obvious choices require their corresponding
ADR. Confirmed numeric values are not “candidates”; their mapping into the proposed
shared contract remains subject to parity and acceptance.
