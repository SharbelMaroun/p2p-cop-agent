# ADR-004 — Shared JSON and Private TOML

Status: **PARTIALLY ACCEPTED — SHARED AUTHORITY DEFINED; MIRROR SCOPE OPEN**

## Context

Appendix B directly separates byte-identical agreed JSON from local per-peer TOML.
The peers must enforce the same game physics without exposing private settings or
sharing a runtime filesystem.

## Decision

- Use `config/game.json` as the single authoritative shared constitution, including
  timeouts and Gatekeeper limits.
- Keep `config/rate_limits.json` as a validated operational enforcement mirror. It
  cannot override the shared values; its cross-repository byte-parity status remains
  open.
- Put the guidelines-required configuration revision `version: "1.00"` at the root
  of each split shared JSON file and validate it independently of `schema_version`.
- Keep only Cop-local `config/game.toml.example`; never add Thief-private config here.
- Shared values override overlapping local defaults.
- Exclude secrets, ports, local opponent-URL storage, provider/model choices,
  credentials, tunnels, nonces, emails used as credentials, and strategy tuning
  from the shared bundle.

## Acceptance

- Config tests prove the shared/private boundary and exact operational mirror.
- Private TOML and `.env` are absent from the parity manifest.
- Cop and Thief accept identical shared bytes independently.
