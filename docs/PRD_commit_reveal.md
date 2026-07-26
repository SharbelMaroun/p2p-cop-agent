# PRD — Commit-Reveal

Status: config hashing is defined; move-commit wire representation and byte
canonicalization are **not frozen**.

## Confirmed behavior

- Every turn follows Commit → Acknowledge → Reveal → Final Audit.
- SHA-256 commits bind the semantic state, move, intent, and nonce before reveal.
- Only the hash is sent during Commit.
- A fresh nonce remains secret until the end-of-game final reveal/audit.
- Both peers recompute every commitment. Any mismatch is a technical loss worth zero.
- Step 0 records the required hardware/LLM/code/group/game/commit declaration data.

Sources: book Ch. 5; Appendix E rules 17–19/24.

## Proposed decision boundary

The shared-config digest has its own accepted vector and does not define move
commitments. ADR-006 must still define move bytes and nonce length. A Python expression such as
`json.dumps(sort_keys=True, separators=(",", ":"))`, a delimiter, field spelling,
encoding, and comparison helper are implementation proposals—not Appendix E rules.
No cryptographic runtime behavior may depend on them until both peers accept ADR-006.

Known semantic components do not prove a formal wire payload schema. Sub-game/role
sealing, field names/types, error envelopes, and acknowledgement transport are linked
to ADR-001/002/006 and contract tests.

This milestone may provide fixtures and typed contract models only; it implements no
commit-reveal runtime.
