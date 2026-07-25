# Active TODO

Only this table is executable. The archived 635-task document is historical coverage
and will not be restored.

| ID | Task | Owner | Status | Priority | Definition of Done | Requirement / ADR / test / artifact |
|---|---|---|---|---|---|---|
| M0-01 | Correct active documentation and record baseline parity | Cop docs owner | DONE | P0 | False parity, candidate-value, schema, source, simulator, and LLM claims are corrected | [requirements](REQUIREMENTS_LEDGER.md); [PARITY_REPORT](PARITY_REPORT.md) |
| M0-02 | Record the ten unresolved design decisions | Cop contract owner | DONE | P0 | ADR-001 through ADR-010 exist with source limits, proposal status, and acceptance conditions | [ADRs](adr/) |
| M1-01 | Build deterministic shared bundle `0.1.0-proposed` | Cop contract owner | DONE | P0 | Controlled files are source/ADR mapped and contain no private data | [ADRs](adr/); [contracts](contracts/); [shared config](../config/game.json); [rate config](../config/rate_limits.json) |
| M1-02 | Isolate shared-config 1.2 from artifact-fixture 1.1 | Cop contract owner | DONE | P0 | Separate validators/fixtures reject unsupported versions clearly | [ADR-003](adr/ADR-003-schema-version-discrepancy.md); [contract tests](../tests/contract/); [schemas](schemas/) |
| M1-03 | Create independent `p2p_cop_agent` package and SDK smoke path | Cop package owner | DONE | P0 | `uv` installs the package; version is `1.00`; SDK/import/help smoke tests pass | [PS requirements](REQUIREMENTS_LEDGER.md); [source](../src/); [unit tests](../tests/unit/) |
| M1-04 | Validate confirmed game/rate values and minimum semantics | Cop package owner | DONE | P0 | Confirmed fields load from files; below-minimum and unsupported values fail | [SR-011](REQUIREMENTS_LEDGER.md); [parameters](PARAMETERS_BASELINE.md); [contract tests](../tests/contract/) |
| M1-05 | Preserve official artifact exemplar key sets | Cop contract owner | DONE | P0 | All four 1.1 fixtures parse; negative tests assert only proven constraints | [SR-013](REQUIREMENTS_LEDGER.md); [artifact baseline](ARTIFACT_TEMPLATE_BASELINE.md); [fixtures](../tests/fixtures/contracts/) |
| M1-06 | Generate and verify parity manifest | Cop contract owner | DONE | P0 | Manifest is deterministic and detects changed, missing, and unexpected controlled files | [ADR-003/004](adr/); [manifest](contracts/PARITY_MANIFEST.json); [parity tests](../tests/contract/) |
| M1-07 | Run local quality and clean-room gates | Cop quality owner | DONE | P0 | Frozen sync, Ruff, branch coverage ≥85%, length, secret, and no-simulator-copy checks pass | [verification evidence](REPOSITORY_AUDIT.md); [quality scripts](../scripts/) |
| M1-08 | Obtain Thief acceptance and exact hash parity | Both contract owners | BLOCKED | P0 | Thief copies accepted files byte-for-byte and both manifests/checkers agree | [Gate G3](PLAN.md); [parity report](PARITY_REPORT.md); Thief evidence |
| M1-09 | Freeze contract version | Both teams | BLOCKED | P0 | All shared ADRs required by the bundle are accepted and version is no longer `-proposed` | [Gate G4](PLAN.md); [CONTRACT_VERSION](contracts/CONTRACT_VERSION) |
| M2-01 | Implement immutable coordinates/actions/grid | Cop runtime owner | DEFERRED | P1 | Unit tests prove immutability and vocabulary | [post-G4 unit tests](../tests/unit/) |
| M2-02 | Implement legal movement | Cop runtime owner | DEFERRED | P1 | N/S/E/W/STAY and boundary/barrier rules pass unit tests | [SR-014](REQUIREMENTS_LEDGER.md); [unit tests](../tests/unit/) |
| M2-03 | Implement Cop local state/history | Cop runtime owner | DEFERRED | P1 | State contains no Thief private truth and history is deterministic | [SR-004](REQUIREMENTS_LEDGER.md); [unit tests](../tests/unit/) |
| M2-04 | Implement barriers and capture | Cop runtime owner | DEFERRED | P1 | Inventory, legal placement, disclosure, barrier-on-cell, and trapped capture pass | [SR-015](REQUIREMENTS_LEDGER.md); [unit tests](../tests/unit/) |
| M2-05 | Implement deterministic baseline pursuit | Cop strategy owner | DEFERRED | P1 | Legal deterministic pursuit is SDK-reachable and unit-tested | [ADR-007](adr/ADR-007-llm-movement-policy.md); [unit tests](../tests/unit/) |

Open evidence questions remain in
[UNKNOWN_REQUIREMENTS.md](UNKNOWN_REQUIREMENTS.md); they block only their affected
runtime or freeze decision.
