# Product Requirements Document

## Milestone

Status: **M1.5 contract repair complete; M2/M3 local rules complete; M4 next**.

The product boundary is the Cop-only package `p2p_cop_agent` (`COP-001`). At the
current baseline includes an independently installable scaffold, a source-backed
proposed shared-contract bundle, and transport-free local gameplay rules. It does
not implement networking or external integrations.

Contract version: `0.2.7-proposed` — **UNFROZEN** pending coordinator acceptance,
independent peer consumption, and byte-for-byte proof.

## Goals

1. Make confirmed rules, values, source limits, conflicts, and ADR-owned choices
   internally consistent.
2. Separate stable league semantics, explicit per-match inputs, and private peer
   configuration without claiming unsupported formal-schema constraints.
3. Provide a `uv` package, public SDK smoke path, tests, and quality gates.
4. Produce deterministic SHA-256 evidence for every parity-controlled file.

## Non-goals

No game engine, peer runtime, FastMCP handlers, LLM calls, Gmail delivery, GUI,
replay, or league behavior is implemented in this milestone. No Thief-private
configuration or runtime code belongs in this repository.

## Requirements

- Confirmed shared and Cop requirements are in
  [REQUIREMENTS_LEDGER.md](REQUIREMENTS_LEDGER.md).
- Binding values and statuses are in
  [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md).
- Local generated-artifact key-set observations and provenance limits are in
  [ARTIFACT_TEMPLATE_BASELINE.md](ARTIFACT_TEMPLATE_BASELINE.md).
- Option B fixes the project MCP names and per-turn commitment bytes. ADR-002 and M4
  still own the remaining envelope/error semantics; `negotiate.nonce` is a distinct
  public challenge.
- Book example `1.2`, local-artifact observation `1.1`, and simulator runtime `1.3`
  stay isolated under ADR-003.
- Root configuration revision `1.00` remains a proposed placement distinct from
  schema profiles and the proposed contract version.

## Acceptance criteria

- The completed M1.5 gate in [PLAN.md](PLAN.md) establishes the corrected review
  candidate while keeping independent parity/freeze work explicit.
- Missing, unexpected, or byte-changed controlled files fail Cop-local integrity.
- Optional read-only comparison against another repository root reports missing,
  unexpected, and byte-different paths separately.
- `uv sync --frozen`, Ruff, pytest with branch coverage at least 85%, file-length
  checks, and secret scanning pass from a clean state.
- Private TOML and `.env` data are not parity-controlled.
- `config_sha256` is reproducible from the explicit complete match object; the
  contract remains `UNFROZEN` until independent review/parity gates succeed.

Historical pre-audit requirements remain non-authoritative under
[`archive/pre-audit/documentation/`](../archive/pre-audit/documentation/).
