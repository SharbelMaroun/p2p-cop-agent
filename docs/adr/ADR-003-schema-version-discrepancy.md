# ADR-003 — Schema-Version Discrepancy

Status: **PROPOSED — UNACCEPTED**

## Context

Appendix B’s shared `config/game.json` example uses schema `1.2`. The four inspected
official reporting-artifact examples use `schema_version: "1.1"`. They serve
different contracts, and available examples do not prove complete formal schemas.
Professional Software Submission Guidelines v3.0 section 8.1 separately requires
configuration revision `version: "1.00"`; that field is not a schema-profile number.

## Proposed decision

- Shared `config/game.json` and `config/rate_limits.json`: shared-config schema `1.2`.
- Both shared JSON files: independent configuration revision `version: "1.00"`.
- Preserved declaration/config/log/result exemplar key-set fixtures: artifact schema
  `1.1`.
- Separate loaders/validators/version errors; never silently translate or normalize
  one version into the other.

## Acceptance

- Each fixture declares its contract family and version.
- Supported versions validate; unsupported/cross-family versions fail clearly.
- The distinction appears in shared rules, tests, and parity manifest.
- Thief accepts the same bytes and semantics.

This proposal does not claim unproven required/optional/type/enum constraints.
