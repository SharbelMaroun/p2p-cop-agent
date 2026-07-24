# Repository Audit

Audit basis: every non-`.git` file present at the start of the 2026-07-24 audit. `Material/` was already untracked teammate/reference work and was preserved.

| Path | Current purpose | Classification | Verified statements | Unsupported statements | Required action | Blocking evidence needed |
|---|---|---|---|---|---|---|
| `README.md` | Project front page | REVISE | Companion URLs | Architecture, six sections, commands, config contract | Rewritten as status page | Book/guidelines/templates |
| `LICENSE` | MIT license | KEEP WITH WARNING | MIT text exists | Compatibility with lecturer material | Keep; do not apply to lecturer sources | Rights/licensing guidance |
| `.env-example` | Secret placeholders | REVISE | None required | Providers/tunnel choices | Do not use as requirements | Confirm integrations |
| `.gitignore` | Ignore policy | KEEP WITH WARNING | Existing patterns | Mandatory pattern claims | Keep; recheck later | Guidelines/security rules |
| `.vscode/settings.json` | Editor colors | KEEP | Purely local UI settings | None material | No action | None |
| `config/police/game.json` | Draft shared terms | QUARANTINE | None | Entire schema, versions, values | Never load; replace only from official template | Appendix F/Moodle template |
| `config/police/game.toml` | Draft private settings | QUARANTINE | Repo URLs | Keys, ports, model, timeout, recipient/mode | Never load | Official allowed settings |
| `config/police/rate_limits.json` | Draft limits | QUARANTINE | None | Schema/version/values | Never load | Appendix F/template |
| `config/thief/game.json` | Thief draft copied into Cop repo | REMOVE LATER | None | Entire schema/values | Preserve now; do not load | Repo-boundary ruling |
| `config/thief/game.toml` | Thief private draft | REMOVE LATER | Companion URLs | All runtime settings | Preserve now; do not load | Repo-boundary ruling |
| `config/thief/rate_limits.json` | Thief limit draft | REMOVE LATER | None | Entire file | Preserve now; do not load | Repo-boundary ruling |
| `docs/PRD.md` | Broad product design | QUARANTINE | Cop/Thief topic | Numerous requirements and schemas | Navigation only | Direct official evidence |
| `docs/PRD_commit_reveal.md` | Crypto design | QUARANTINE | Topic only | Fields, algorithms, sizes, flow | Do not implement from it | Book/templates |
| `docs/PRD_gatekeeper_reporting.md` | Reliability/report design | QUARANTINE | Topic only | Gmail, limits, artifacts | Do not implement from it | Book/templates |
| `docs/PRD_p2p_mcp.md` | Network design | QUARANTINE | Topic only | Tools, messages, timeouts, ports | Do not implement from it | Book/protocol evidence |
| `docs/PRD_scent_belief.md` | Belief/scent design | QUARANTINE | Cop-relevant topic | Equations and numerical model | Do not implement from it | Appendix evidence |
| `docs/PRD_strategy.md` | Role strategies | REVISE | Cop pursuit topic | Includes Thief runtime plan and unverified policies | Use only as idea list | Book and Cop scope |
| `docs/PLAN.md` | Implementation plan | QUARANTINE | None as requirements | Phases, architecture, values | Do not start Phase 1 | Resolved ledger |
| `docs/TODO.md` | 600+ task backlog | QUARANTINE | None as requirements | Nearly all exact tasks/values | Do not execute | Resolved ledger |
| `docs/PROMPTS.md` | AI prompt log | KEEP WITH WARNING | Historical prompts | Any derived requirement | Preserve history only | Source verification |
| `Material/LECTURER_REPO_OVERVIEW.md` | Simulator summary | KEEP WITH WARNING | Upstream URL | Commitless behavior/test claims | Superseded by pinned baseline | Pinned checkout for tests |
| `Material/PROJECT_CONTEXT(1).md` | Planning context | KEEP WITH WARNING | Repo URLs | Requirements restated secondarily | Navigation only | Direct sources |
| `Material/SUBMISSION_CHECKLIST(1).md` | Submission checklist | KEEP WITH WARNING | None directly verified here | All mandatory claims | Navigation only | Book/guidelines |
| `Material/software_submission_guidelines-V3_Summary.md` | Guidelines summary | KEEP WITH WARNING | Summary exists | Exact professional requirements | Navigation only | Official v3.0 document |
| `Material/reference/police_thief_p2p.pdf` | Candidate official book | KEEP WITH WARNING | Binary/hash present | Identity/version/content unreadable here | Obtain readable verified copy | Official provenance/extraction |
| `Material/reference/police_thief_p2p_unverified_translation.md` | Automatic translation | QUARANTINE | Explicitly unverified | All translated claims | Navigation only | Original-page verification |

## Newly created audit controls

The ten audit documents created in this task are `KEEP`; they record evidence status rather than inventing implementation requirements.
