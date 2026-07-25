# Shared Requirement Baseline

This file contains only shared, directly confirmed structural and professional-software
requirements. It intentionally contains no gameplay values or simulator-specific names, and is
byte-identical in both repositories. Candidate numeric values live in
[PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md) (directly confirmed Appendix F values).

| ID | Status | Requirement | Direct source location |
|---|---|---|---|
| SR-001 | CONFIRMED | The final project uses one Cop repository and one Thief repository. | Project book v3.0.0, Ch. 9 §9.4; Appendix C |
| SR-002 | CONFIRMED | Each repository README links to the other team repository. | Project book v3.0.0, Ch. 9 §9.4; Appendix C checklist |
| SR-003 | CONFIRMED | Both repositories are public or otherwise accessible to the lecturer. | Project book v3.0.0, Appendix C §1, PDF p. 133 / printed p. 117 |
| SR-004 | CONFIRMED | Cop and Thief run in separate processes and configuration environments without shared live mutable state or access to private opponent truth. | Project book v3.0.0, Ch. 2 §2.4.2 |
| SR-005 | CONFIRMED | Each peer acts as a FastMCP server and FastMCP client. | Project book v3.0.0, Ch. 2 §2.3, PDF pp. 25–26 / printed pp. 9–10 |
| SR-006 | CONFIRMED | Each repository contains at minimum a root README, configuration directory, PRD documents, PLAN, TODO, and code. | Project book v3.0.0, Ch. 9 §9.4; Appendix E rule 50 |
| SR-007 | CONFIRMED | The submission version is marked with an annotated Git tag. | Project book v3.0.0, Appendix E rule 41; Ch. version control (exact literal is the book example only) |
| SR-008 | CONFIRMED | The README academic report has six mandatory sections; section 6 is the companion-repository link. | Project book v3.0.0, Ch. 9.4.2; Appendix E rule 42 |
| SR-009 | CONFIRMED | Runtime uses a single Orchestrator gateway, an explicit state machine that rejects illegal transitions, and a watchdog/deadline monitor. | Project book v3.0.0, Ch. 2 / Ch. 8; Appendix E rules 3–7 |
| SR-010 | CONFIRMED | The project ships a live GUI showing local information only and a mandatory replay + SHA-256 verification viewer. | Project book v3.0.0, Appendix E rules 8, 9, 20 |
| PS-001 | CONFIRMED | Maintain the root README, core PRD/PLAN/TODO documents, and dedicated mechanism PRDs. | Professional Guidelines v3.0, pp. 7–9 |
| PS-002 | CONFIRMED | Use `uv`, `pyproject.toml` as dependency source of truth, and commit `uv.lock`. | Professional Guidelines v3.0, pp. 19–20 |
| PS-003 | CONFIRMED | Code and test files stay within 150 code lines excluding blanks/comments. | Professional Guidelines v3.0, p. 10 |
| PS-004 | CONFIRMED | Follow TDD, test public and failure behavior, mock live services, and maintain at least 85% global coverage. | Professional Guidelines v3.0, pp. 15–16 |
| PS-005 | CONFIRMED | Ruff passes with zero violations under the controlling course configuration. | Professional Guidelines v3.0, p. 17 |
| PS-006 | CONFIRMED | Do not hard-code configurable values or commit secrets; maintain placeholders and ignores. | Professional Guidelines v3.0, pp. 17–18 |
| PS-007 | CONFIRMED | External entry points delegate business logic through an SDK/service boundary. | Professional Guidelines v3.0, p. 11 |
| PS-008 | CONFIRMED | External APIs use a centralized gatekeeper with limiting, FIFO queueing, backpressure, retries, and monitoring. | Professional Guidelines v3.0, pp. 13–14 |
| PS-009 | CONFIRMED | Maintain `docs/PROMPT_LOG.md`. | Professional Guidelines v3.0, p. 19 |
| PS-010 | CONFIRMED | Code and configuration carry explicit version tracking starting at 1.00, with runtime version validation. | Professional Guidelines v3.0, version-control section |
