# Documentation Completeness

File presence and content readiness are separate. Every document in `docs/` is listed
below with its current content status.

**This table is checked, not maintained by hand.**
`scripts/check_ledger_consistency.py` (`G-10`) fails if a document exists without a row,
or a row claims a file that is not in the tree. It found **26 missing rows** on
2026-08-07: the table had stopped at M1 while the repository grew through M7, and every
row in it was individually accurate, which is why nobody noticed. That is the argument
for the check rather than for another careful pass.

Dated one-off records ג€” session handoffs, the blocker-resolution audit, the lecturer
direction note ג€” are deliberately excluded. They document a moment rather than a current
state, so a "current content status" for them would have to be re-dated forever.

| Document | Present | Current content status |
|---|---|---|
| `README.md` | Yes | The graded entry point: six-section academic report, quick start, quality gates, companion link |
| `docs/ACADEMIC_REPORT.md` | Yes | The long-form report ג€” formalism, architecture decisions and their cost, measured results, and three disclosed source contradictions |
| `docs/PRD.md` | Yes | Behaviour-free milestone goals, non-goals and acceptance |
| `docs/PLAN.md` | Yes | M0-M9 phases. M0-M4, M6, M7 DONE; M1.5 and M5 have one blocked row each; M8-M9 open. States are now held to `TODO.md` by `check_ledger_consistency.py` |
| `docs/TODO.md` | Yes | The single task ledger, Cop-owned M0-M9. Task counts are deliberately not pinned here ג€” they went stale three times before the ledger became the one place to read them |
| `docs/PRD_commit_reveal.md` | Yes | SHA-256 commit-reveal, canonical form, and the audit |
| `docs/PRD_scent_belief.md` | Yes | The locked multiplicative scent model with its digest, the wire observation, and the belief update rule with its trust factor (`M6-14a`) |
| `docs/PRD_strategy.md` | Yes | Pursuit, the scent-over-hint evidence ordering, and the measured belief-vs-blind-vs-oracle comparison |
| `docs/PRD_p2p_mcp.md` | Yes | FastMCP peer roles and the negotiated wire |
| `docs/PRD_gatekeeper_reporting.md` | Yes | Token bucket, report delivery, and the JSON attachment |
| `docs/PRD_gui.md` | Yes | Local-truth GUI boundary |
| `docs/PRD_replay.md` | Yes | Verified/tampered replay semantics and the mandatory banner |
| `docs/ADR-009-peer-launch.md` | Yes | Peer launch decision (sits beside `adr/` for historical reasons) |
| `docs/adr/ADR-001-mcp-contract.md` | Yes | MCP contract names. ACCEPTED for this project (Option B, simulator-v3 profile) |
| `docs/adr/ADR-002-message-envelope-idempotency.md` | Yes | Message envelope and idempotency. ACCEPTED for this project (Option B) |
| `docs/adr/ADR-003-schema-version-discrepancy.md` | Yes | Schema-version discrepancy `1.1` vs `1.2` (`C-008`). **PROPOSED ג€” UNACCEPTED**; the version is deliberately held rather than normalised |
| `docs/adr/ADR-004-shared-json-private-toml.md` | Yes | Shared JSON / private TOML boundary. ACCEPTED ג€” this is what keeps tunnel tokens out of negotiated files |
| `docs/adr/ADR-005-scent-model.md` | Yes | The multiplicative scent model, against the reference's subtractive decay. SOURCE-BACKED PROPOSAL ג€” UNACCEPTED |
| `docs/adr/ADR-006-commit-reveal-canonicalization.md` | Yes | Commit-reveal canonicalization. Config hash defined; move commit ACCEPTED for this project |
| `docs/adr/ADR-007-llm-movement-policy.md` | Yes | LLM movement stays disabled. ACCEPTED project baseline, with rule 25's recommendation status preserved rather than promoted |
| `docs/adr/ADR-008-simulator-reuse-license.md` | Yes | Simulator reuse and licence. PROPOSED ג€” no substantial copy |
| `docs/adr/ADR-009-gui-truth-model.md` | Yes | GUI truth model. SOURCE-BOUND PLACEHOLDER ג€” runtime deferred |
| `docs/adr/ADR-010-gmail-reporting.md` | Yes | Gmail reporting. SOURCE-BOUND PLACEHOLDER ג€” runtime deferred |
| `docs/SOURCE_OF_TRUTH.md` | Yes | The authority order every other document resolves against |
| `docs/SOURCE_INVENTORY.md` | Yes | What each source is and what it may be used for |
| `docs/SPECIFICATION_CONFLICTS.md` | Yes | `C-nnn` contradictions in the source and how each was resolved |
| `docs/UNKNOWN_REQUIREMENTS.md` | Yes | `U-nnn` open questions and what each blocks |
| `docs/REQUIREMENTS_LEDGER.md` | Yes | `SR`/`OB` requirements with their authority and test impact |
| `docs/PARAMETERS_BASELINE.md` | Yes | Appendix F values as Fixed / Minimum / Negotiable |
| `docs/PURSUIT_BASELINE.md` | Yes | The deterministic pursuit baseline the strategy is measured against |
| `docs/SIMULATOR_BASELINE.md` | Yes | What the reference does, separated from what the book requires |
| `docs/ARTIFACT_TEMPLATE_BASELINE.md` | Yes | Observed template shapes, with provenance stated as unresolved (`U-019`) |
| `docs/SHARED_CONTRACT_POLICY.md` | Yes | How the shared bundle may change and who may accept a change |
| `docs/SHARED_REQUIREMENT_BASELINE.md` | Yes | Requirements both peers must satisfy identically |
| `docs/CONTRACT_CANDIDATE_HANDOFF.md` | Yes | The published bundle revision, its hashes, and its freeze dependencies |
| `docs/OPTION_B_DECISION.md` | Yes | The 2026-07-28 academic-freedom decision |
| `docs/OPTION_B_HANDOFF.md` | Yes | What Option B changed for the companion peer |
| `docs/PARITY_REPORT.md` | Yes | Where the two peers differ and why each difference is deliberate |
| `docs/INTERFACE_REVIEW.md` | Yes | The SDK surface and its import boundaries |
| `docs/VERIFICATION_POLICY.md` | Yes | What counts as evidence, and what may never be claimed without it |
| `docs/QUALITY_EVIDENCE.md` | Yes | Gate-by-gate evidence: ruff, coverage, file lengths, secrets, history scan |
| `docs/SELF_ASSESSMENT.md` | Yes | Grade self-assessment against the published rubric |
| `docs/SHARED_MATERIAL_AND_AUTHORSHIP.md` | Yes | What is shared byte-for-byte with the companion repository, what is authored separately, and why run-time separation is the boundary the rules set |
| `docs/REPOSITORY_AUDIT.md` | Yes | Structure and content audit against the book's chapter 9 requirements |
| `docs/SUBMISSION_CHECKLIST.md` | Yes | What must be true before the annotated tag is made |
| `docs/USAGE.md` | Yes | How to run the peer, the replay verifier and the gates |
| `docs/RUNBOOK_reporting_setup.md` | Yes | Reporting setup, with credentials kept out of the repository |
| `docs/MATCH_RUNBOOK.md` | Yes | The one-page procedure for playing a real opponent: shared-file handshake, commands, the six-sub-game role schedule, post-game duties, and the rehearsal-earned troubleshooting list |
| `docs/TEAM_INFO.md` | Yes | Group identifier, team code and members |
| `docs/PROMPT_LOG.md` | Yes | Historical provenance and correction entries |
| `docs/RESEARCH-REPORT-Performance-Analysis.md` | Yes | Measured performance study |
| `docs/COORDINATOR_PROVISIONAL_AUTH_REQUEST.md` | Yes | A standing request to the coordinator, kept as the record of what was asked |
| `docs/DOCS_COMPLETENESS.md` | Yes | This table |

The archived T001-T635 file is historical coverage only. It will not be restored as the
active plan. This document makes no cross-repository parity claim; baseline differences
are in [PARITY_REPORT.md](PARITY_REPORT.md).
