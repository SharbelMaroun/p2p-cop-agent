# M0–M1 Plan

At baseline, runtime implementation had not begun. This plan authorizes only the
proposed contract and behavior-free `p2p_cop_agent` scaffold. A status of `BLOCKED`
applies to the named gate only, not to unrelated work.

| Gate/task | Owner | Status | Priority | Definition of Done | Traceability |
|---|---|---|---|---|---|
| G0 Evidence and contradiction audit | Cop docs owner | DONE | P0 | Primary-source limits, stale claims, conflicts, and baseline parity evidence are recorded | [requirements](REQUIREMENTS_LEDGER.md); [PARITY_REPORT](PARITY_REPORT.md); [conflicts](SPECIFICATION_CONFLICTS.md) |
| **G1 Proposed contract + package scaffold parity** | Cop implementation owner | DONE | P0 | `0.1.0-proposed` controlled files, manifest/checker, independent package, SDK smoke path, and contract fixtures exist; no behavior is added | [ADRs](adr/); [contract tests](../tests/contract/); [manifest](contracts/PARITY_MANIFEST.json); [checker](../scripts/check_shared_contracts.py) |
| G2 Local quality gate | Cop implementation owner | DONE | P0 | Frozen `uv` install, Ruff zero violations, pytest branch coverage ≥85%, length and secret checks all pass | [PS requirements](REQUIREMENTS_LEDGER.md); [verification evidence](REPOSITORY_AUDIT.md); [quality scripts](../scripts/) |
| G3 Thief acceptance and cross-repository parity | Cop + Thief contract owners | BLOCKED | P0 | Thief explicitly accepts and copies the controlled bundle byte-for-byte; both checkers report the same hashes | [ADRs](adr/); [manifest](contracts/PARITY_MANIFEST.json); Thief acceptance evidence |
| G4 Contract freeze | Both teams | BLOCKED | P0 | Version is promoted from `0.1.0-proposed` only after G3 and any unresolved shared-field ADRs are accepted | [CONTRACT_VERSION](contracts/CONTRACT_VERSION); [ADR statuses](adr/) |
| G5 Runtime implementation | Cop runtime owner | DEFERRED | P1 | Begins only after G4, starting with immutable coordinates/actions/grid and legal movement | [future unit tests](../tests/unit/); runtime artifacts |

## Gate 1 constraints

- Shared files contain no role-private values, secrets, ports, credentials, provider
  keys, tunnel details, or nonces.
- Shared game/rate JSON uses schema `1.2`. Official reporting-artifact key-set
  fixtures remain `1.1`; ADR-003 keeps the contracts separate.
- MCP names, envelope/idempotency fields, and commit byte canonicalization are
  proposals only until ADR-001, ADR-002, and ADR-006 are accepted.
- The archived T001–T635 backlog is historical coverage only; active work is tracked
  in [TODO.md](TODO.md).

## Post-parity order

Immutable coordinates/actions/grid → legal movement → Cop local state/history →
barrier inventory and legal placement → disclosed barrier events →
barrier-on-current-cell and trapped-Thief capture → deterministic baseline pursuit.
