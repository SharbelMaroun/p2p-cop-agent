# PRD — Commit-Reveal

Status: config hashing and the Option-B move-commit profile are accepted project
decisions; the M4 runtime state machine and audit binding remain unimplemented.

## Confirmed behavior

- Every live turn sends a commitment and receives transport acknowledgement.
- Hidden payloads and per-turn commitment nonces are revealed only in the post-game
  final audit; the Option-B profile has no live reveal tool.
- SHA-256 commits bind the semantic state, move, intent, and commitment nonce before
  reveal.
- Only the hash is sent during Commit.
- A fresh commitment nonce remains secret until the end-of-game final reveal/audit.
- The separate `negotiate.nonce` field is a public pre-play challenge, not a
  commitment nonce.
- Both peers recompute every commitment. Any mismatch is a technical loss worth zero.
- Step 0 records and seals the required hardware/LLM/code/group/game declaration
  data plus the exact Git commit of the running code before moves begin.

Sources: book Ch. 5; Appendix E rules 17–19/24.

## Proposed decision boundary

The shared-config digest has its own accepted vector and does not define move
commitments. ADR-006 fixes the project move-commit bytes: sorted keys, compact
separators, unescaped Unicode, UTF-8, a literal `"|"` delimiter, and a 16-byte
commitment nonce rendered as 32 lowercase hexadecimal characters. This is an
accepted Option-B project choice, not an Appendix E serialization rule.

Known semantic components do not prove a formal wire payload schema. Sub-game/role
sealing, field names/types, error envelopes, and acknowledgement transport are linked
to ADR-001/002/006 and contract tests.

The simulator's `validate_agreement` presence check for nine normalized gameplay
terms is not the Step-0 attestation gate and cannot substitute for it. M4 must define
the signed payload and independent verification vector.

M4 implements the transport-neutral state machine, private pending-record storage,
duplicate/conflict handling, final audit verification, and Step-0 gate through the
SDK. FastMCP adapters remain M5.
