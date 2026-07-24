# Repository Audit

Remediation date: 2026-07-24. No implementation or dependency files were added, and teammate material was preserved.

## Current disposition

| Path/scope | Purpose | Classification | Verified state | Unsupported state | Required action |
|---|---|---|---|---|---|
| `README.md` | Project entry point | KEEP | Verified-requirements phase, companion link, structural baseline, Cop assignment | Runtime commands/mechanics | Keep synchronized with ledger |
| `LICENSE` | Team code license | KEEP WITH WARNING | License file remains | Application to lecturer material | MIT applies only to team-authored material where legally valid |
| `.env-example` and `.gitignore` | Secret hygiene | KEEP WITH WARNING | Required pattern confirmed by `PS-006` | Provider-specific variables | Revisit when integrations are confirmed |
| `config/README.md` | Configuration status | KEEP | Active runtime config is absent | None | Controlling config notice |
| `config/drafts/cop/*` | Historical Cop config drafts | QUARANTINE | Located outside active-looking role paths; valid draft syntax | All filenames, fields, versions, schemas, and values | Never load; replace only from official evidence |
| `archive/pre-audit/opposite-role-config/thief/*` | Preserved opposite-role drafts | ARCHIVE | Outside active config tree; teammate work retained | All runtime/schema claims | Cop implementation must ignore |
| `docs/REQUIREMENTS_LEDGER.md` | Evidence ledger | KEEP | Canonical `SR-*`, `PS-*`, and `COP-001` baseline | Runtime unknowns | Update only with direct evidence |
| `docs/SHARED_REQUIREMENT_BASELINE.md` | Cross-repository baseline | KEEP | Contains only shared confirmed structural/professional requirements | Gameplay/simulator details excluded | Synchronize wording with Thief repo |
| `docs/UNKNOWN_REQUIREMENTS.md` | Blocker register | KEEP | Runtime details remain UNKNOWN | None promoted indirectly | Resolve field by field |
| `docs/SPECIFICATION_CONFLICTS.md` | Conflict register | KEEP | Required conflicts/discrepancies preserved | No silent resolution | Import direct evidence |
| `docs/PROMPT_LOG.md` | Prompt engineering log | KEEP | Canonical path confirmed by `PS-009` | Historical entries are not requirements | Continue maintaining |
| Legacy `docs/PRD*`, `PLAN.md`, `TODO.md` | Historical planning | QUARANTINE | Quarantine notices present | Numerous premature mechanics/values | Do not implement from them |
| `docs/SIMULATOR_BASELINE.md` | Simulator dependency record | KEEP WITH WARNING | Pinned public commit recorded | No centralized reverse-engineering export | Await planning-repo export |
| `Material/` | Untracked source/reference material | KEEP WITH WARNING | Preserved and read | Summaries/translations are nonbinding | Do not stage as implementation |

## Remediation results

- Active runtime configuration: **none**.
- Cop drafts: `config/drafts/cop/`.
- Thief drafts: `archive/pre-audit/opposite-role-config/thief/`.
- Injected audit-only JSON fields: removed from all drafts.
- Old active-looking `config/police/` and `config/thief/` files: absent.
- README: corrected; no installation/run commands or section-count claim.
- Shared structural requirements: confirmed under canonical IDs.
- Runtime mechanics, schemas, values, and simulator-dependent details: still `UNKNOWN`.
