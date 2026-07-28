# Per-Match Configuration and Hash Domains

Contract version: `0.2.2-proposed`
Status: **PROPOSED / UNFROZEN**

The stable bundle does not contain an active match. A per-match shared game object
is supplied at runtime through an explicit path or a validated in-memory object and
is checked against `schemas/match-config.schema.json`. `fixtures/match_config.example.json`
is only an example template; changing opponent IDs or game identity for a real match
never edits any file in this bundle.

## Three distinct hash domains

These three values are independent and must never be conflated with each other or
with the parity-manifest self-hash.

### 1. Move / negotiation commitment

Binds a hidden payload to a secret nonce (see `PROTOCOL_PROFILE.md`):

```text
commit = SHA256( canonical_json(payload) + "|" + nonce )
```

`canonical_json` uses sorted keys, `ensure_ascii=False`, compact `,`/`:`
separators, and `allow_nan=False`. Vectors live in `vectors/move-commit.vectors.json`.

### 2. `config_sha256`

SHA-256 of the **complete parsed per-match shared game object**, serialized with
sorted keys, compact separators, unescaped Unicode, and UTF-8. It must include the
actual agreed `agreed_between` values. The claim is stored **outside** the hashed
object (in the emitted config artifact), so there is no self-hash field to remove.
Vectors live in `vectors/config-sha256.vectors.json`.

### 3. `config_file_sha256`

SHA-256 of the **exact bytes** of the on-disk match `game.json`, used separately for
the byte-identical rule. Two peers must hold identical source bytes, not merely
objects that canonicalize equally.

## Negotiation-terms projection

The `negotiate` message carries a **projection** of the full per-match game object,
not the whole object. The projection is documented and fixtured separately so the
two are never confused: `fixtures/negotiation_terms.projection.json` maps one game
object to its exact negotiation terms. The `config_sha256` in domain 2 is always
computed over the complete game object, never over the projection.

## Agreement comparison

Before play, a received offer must match on the negotiated game object, its
`config_sha256`, and its `config_file_sha256`. Any participant, negotiated value,
timeout, Gatekeeper, hash, or source-byte mismatch rejects the offer.
