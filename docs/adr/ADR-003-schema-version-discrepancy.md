# ADR-003 — Schema-Version Discrepancy

Status: **PROPOSED — UNACCEPTED**

## Context

Appendix B’s shared `config/game.json` example uses schema `1.2`. Four local
simulator-generated artifacts use `schema_version: "1.1"` but have
`NEEDS_MANUAL_REVIEW` provenance. The simulator runtime uses `1.3`. These
observations do not prove complete formal schemas or compatibility.
Professional Software Submission Guidelines v3.0 section 8.1 separately requires
configuration revision `version: "1.00"`; that field is not a schema-profile number.

## Proposed decision

- Proposed match `config/game.json` and `config/rate_limits.json`: accept only `1.2`.
- Root `version: "1.00"` in both files remains a proposed placement.
- Preserved generated-artifact key-set observations record `1.1` without validating
  artifact instances.
- Simulator `1.3` is not accepted as match input.
- Separate loaders/validators/version errors; never silently translate or normalize
  one version into the other.

## Acceptance

- Each fixture declares its contract family and version.
- Supported versions validate; unsupported/cross-family versions fail clearly.
- The distinction appears in shared rules, tests, and parity manifest.
- Thief accepts the same bytes and semantics.

This proposal does not claim an authoritative schema-version compatibility rule or
unproven required/optional/type/enum constraints.
