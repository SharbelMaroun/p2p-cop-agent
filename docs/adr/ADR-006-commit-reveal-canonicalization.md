# ADR-006 — Commit-Reveal Canonicalization

Status: **PARTIALLY RESOLVED — CONFIG HASH DEFINED; MOVE COMMIT OPEN**

## Context

SHA-256 commit-reveal, semantic state/move/intent/nonce binding, nonce secrecy until
final reveal, and zero-point mismatch loss are confirmed. The book does not fully
fix JSON encoding, field spellings/order, delimiters, Unicode treatment, nonce
length, or domain-separation data.

The owner-supplied lecturer direction dated 2026-07-27 resolves the separate
`config_sha256` algorithm. It hashes the complete parsed `config/game.json` object
with lexicographically sorted keys, compact `,`/`:` separators, unescaped Unicode,
UTF-8 encoding, and SHA-256. The claim is written into the emitted per-sub-game
config artifact, not the source object, so no self-hash field is excluded.

This decision does not define move-commit bytes. Simulator commit serialization is
still not adopted as authority.

## Decision required

Define move-payload fields, deterministic bytes, delimiter/domain/version binding,
nonce generation/length, and comparison/test-vector rules.

## Acceptance

- The config-hash vector is reproduced independently by Cop and Thief.
- Public move-commit cross-language/independent vectors produce identical hashes.
- Field mutation, byte mutation, wrong nonce, and unsupported version fail.
- No nonce appears before final reveal.
- Cop and Thief accept the exact specification and hashes.

No commit-reveal runtime choice is frozen in `0.1.0-proposed`.
