# ADR-006 — Commit-Reveal Canonicalization

Status: **OPEN — NO CANONICAL BYTES FROZEN**

## Context

SHA-256 commit-reveal, semantic state/move/intent/nonce binding, nonce secrecy until
final reveal, and zero-point mismatch loss are confirmed. The book does not fully
fix JSON encoding, field spellings/order, delimiters, Unicode treatment, nonce
length, or domain-separation data.

## Decision required

Define deterministic bytes, encoding, domain/version binding, nonce generation and
length, and comparison/test-vector rules. A `json.dumps(...)` expression is only a
candidate until both peers accept exact vectors.

## Acceptance

- Public cross-language/independent test vectors produce identical SHA-256 values.
- Field mutation, byte mutation, wrong nonce, and unsupported version fail.
- No nonce appears before final reveal.
- Cop and Thief accept the exact specification and hashes.

No cryptographic runtime choice is frozen in `0.1.0-proposed`.
