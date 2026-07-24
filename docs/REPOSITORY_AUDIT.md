# Repository Audit

Remediation date: 2026-07-24. No implementation or dependency files were added, and no teammate work was deleted.

## Status versus disposition

`CONFIRMED`, `CONFLICT`, and `UNKNOWN` describe the certainty of a requirement. `KEEP`, `QUARANTINE`, `ARCHIVE`, and `REMOVE LATER` describe what should happen to a file. A file’s disposition does not make its contents authoritative.

## Current disposition

| Path/scope | Purpose | Classification | Current state | Required action |
|---|---|---|---|---|
| `README.md` | Project entry point | KEEP | Verified-requirements phase | Keep synchronized with the ledger |
| `LICENSE` | Team code license | KEEP WITH WARNING | Retained; does not automatically relicense lecturer material | Complete licensing review later |
| `.env-example` | Secret-file template | KEEP | Neutral; contains no selected provider or credential variable | Add placeholders only after decisions are confirmed |
| `.gitignore` | Secret and generated-file exclusions | KEEP WITH WARNING | Existing exclusions retained | Recheck when integrations are confirmed |
| `config/README.md` | Configuration status | KEEP | Confirms there is no runtime configuration | Controlling config notice |
| `config/drafts/cop/*` | Historical Cop config drafts | QUARANTINE | Unverified drafts outside active-looking role paths | Never load |
| `archive/pre-audit/opposite-role-config/thief/*` | Opposite-role drafts | ARCHIVE | Preserved outside active config tree | Cop implementation must ignore |
| `archive/pre-audit/documentation/*` | Complete legacy PRD/PLAN/TODO/mechanism documents | ARCHIVE | Unsupported pre-verification plans preserved with history | History and idea recovery only |
| Active `docs/PRD.md`, `PLAN.md`, `TODO.md` | Current product/plan/task status | KEEP | Short verified-phase stubs | Update only from direct evidence |
| Active mechanism PRDs | Subsystem status | KEEP | Short blocked/unknown stubs | Add requirements only when confirmed |
| `docs/PROMPT_LOG.md` | Development provenance | KEEP WITH WARNING | Historical prompts retained; warning states they are nonauthoritative | Continue maintaining provenance |
| `docs/REQUIREMENTS_LEDGER.md` | Evidence ledger | KEEP | Canonical confirmed baseline and runtime unknowns | Direct evidence required for changes |
| `docs/SHARED_REQUIREMENT_BASELINE.md` | Cross-repository baseline | KEEP | Shared confirmed structural/professional requirements | Synchronize separately with Thief repository |
| `docs/UNKNOWN_REQUIREMENTS.md` | Blocker register | KEEP | Runtime details remain unknown | Resolve field by field |
| `docs/SPECIFICATION_CONFLICTS.md` | Conflict register | KEEP | Required conflicts/discrepancies preserved | Do not resolve silently |
| `docs/PARAMETERS_BASELINE.md`, `SUBMISSION_CHECKLIST.md`, `DOCS_COMPLETENESS.md` | Candidate parameters, submission and completeness records | KEEP | Candidates flagged pending official confirmation; numbers must not enter runtime config |
| `docs/PRD_gui.md`, `docs/PRD_replay.md` | Mandatory GUI + replay deliverable PRDs | KEEP | Confirmed structural shape; framework is a later implementation choice |
| `Material/` | Untracked source/reference material | KEEP WITH WARNING | Preserved; summaries/translations remain nonbinding | Do not stage as implementation |

## Remediation results

- Legacy PRD, PLAN, TODO, and mechanism documents are archived intact.
- Active planning documents are verified-phase stubs.
- The former 600-plus-task backlog is not active or executable-looking.
- `.env-example` is neutral and provider-independent.
- Active runtime configuration: **none**.
- No gameplay, FastMCP runtime, cryptography, strategy, Gmail, GUI, replay, reporting, package, or test implementation is authorized.
- No teammate work was deleted.
- Phase 1 remains blocked by the active TODO and unknown-requirements ledger.
