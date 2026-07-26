# ADR-004 — Shared JSON and Private TOML

Status: **PROPOSED — UNACCEPTED**

## Context

Appendix B directly separates byte-identical agreed JSON from local per-peer TOML.
The peers must enforce the same game physics without exposing private settings or
sharing a runtime filesystem.

## Proposed decision

- Parity-control a neutral proposed match pair at `config/game.json` and
  `config/rate_limits.json`; the split remains unaccepted.
- Put the guidelines-required configuration revision `version: "1.00"` at the root
  of each split shared JSON file and validate it independently of `schema_version`.
- Keep only Cop-local `config/game.toml.example`; never add Thief-private config here.
- Shared values override overlapping local defaults.
- Exclude secrets, ports, local opponent-URL storage, provider/model choices,
  credentials, tunnels, nonces, emails used as credentials, and strategy tuning
  from the shared bundle.

## Acceptance

- Config tests prove the shared/private boundary and overlay behavior.
- Private TOML and `.env` are absent from the parity manifest.
- Cop and Thief accept identical shared bytes independently.
