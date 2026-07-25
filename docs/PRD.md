# Product Requirements Document

## Milestone

Status: **M0–M1 contract and behavior-free scaffold**.

The product boundary is the Cop-only package `p2p_cop_agent` (`COP-001`). At the
inspected baseline, runtime implementation had not begun. This milestone creates an
independently installable scaffold and a source-backed proposed shared-contract
bundle; it does not implement gameplay or integrations.

Contract version: `0.1.0-proposed` — **UNFROZEN** pending Thief acceptance and
byte-for-byte parity.

## Goals

1. Make confirmed rules, values, source limits, conflicts, and ADR-owned choices
   internally consistent.
2. Establish shared game/rate configuration and artifact key-set fixtures without
   claiming unsupported formal-schema constraints.
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
- Known template key sets and their formal limits are in
  [ARTIFACT_TEMPLATE_BASELINE.md](ARTIFACT_TEMPLATE_BASELINE.md).
- Exact MCP names, envelope fields, crypto byte canonicalization, and nonce length
  are not book-mandated; ADR-001, ADR-002, and ADR-006 govern any proposal.
- Shared schema `1.2` and reporting-artifact fixture schema `1.1` stay isolated under
  ADR-003.
- Guidelines-required code and configuration revisions start at `1.00` and remain
  distinct from both schema profiles and the proposed contract version.

## Acceptance criteria

- Gate 1 in [PLAN.md](PLAN.md) establishes a deterministic proposed bundle and
  behavior-free package scaffold.
- Missing, unexpected, or byte-changed parity files fail the parity checker.
- `uv sync --frozen`, Ruff, pytest with branch coverage at least 85%, file-length
  checks, and secret scanning pass from a clean state.
- Private TOML and `.env` data are not parity-controlled.
- The contract remains visibly `UNFROZEN` until independent Thief review and parity
  succeed.

Historical pre-audit requirements remain non-authoritative under
[`archive/pre-audit/documentation/`](../archive/pre-audit/documentation/).
