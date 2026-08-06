# ADR-006 — Commit-Reveal Canonicalization

Status: **CONFIG HASH DEFINED; MOVE COMMIT ACCEPTED FOR THIS PROJECT — Option B, 2026-07-28**

## Context

SHA-256 commit-reveal, semantic state/move/intent/commitment-nonce binding,
commitment-nonce secrecy until final reveal, and zero-point mismatch loss are
confirmed. The book does not fully fix JSON encoding, field spellings/order,
delimiters, Unicode treatment, commitment-nonce length, or domain-separation data.

The owner-supplied lecturer direction dated 2026-07-27 resolves the separate
`config_sha256` algorithm. It hashes the complete parsed `config/game.json` object
with lexicographically sorted keys, compact `,`/`:` separators, unescaped Unicode,
UTF-8 encoding, and SHA-256. The claim is written into the emitted per-sub-game
config artifact, not the source object, so no self-hash field is excluded.

## Per-turn commitment decision (Option B)

Under the accepted [Option-B decision](../OPTION_B_DECISION.md), the per-turn
commitment is fixed for this project:

```python
canonical = json.dumps(
    payload,
    sort_keys=True,
    ensure_ascii=False,
    separators=(",", ":"),
    allow_nan=False,
)
commit = sha256((canonical + "|" + nonce).encode("utf-8")).hexdigest()
```

- The domain-separation delimiter is the single literal character `"|"`.
- The commitment nonce is 16 cryptographically random bytes rendered as 32
  lowercase hex characters, held outside the JSON payload and never disclosed
  before the final audit.
- The plaintext payload, move, position, intent/verdict, and commitment nonce are
  revealed only in the post-game `AuditPayload`; there is no separate live reveal
  tool.
- The public pre-play `negotiate.nonce` challenge is a different protocol value,
  not a commitment nonce. Its public lifecycle does not weaken commitment secrecy.

This is a documented project choice for interoperability, pinned to simulator
commit `960499fd5e8777b4929625f5d8fdcf2ab4677b54`, not a claim that simulator
serialization is a book requirement.

## Acceptance

- The config-hash vector is reproduced independently (WP5).
- Public per-turn commitment vectors reproduce identical hashes independently (WP5).
- Field mutation, byte mutation, wrong commitment nonce, wrong delimiter, and
  duplicate-key loading all fail (WP5).
- No per-turn commitment nonce appears before final reveal.
- Locked in the `0.2.8-proposed` bundle; contract freeze remains a later gate.
