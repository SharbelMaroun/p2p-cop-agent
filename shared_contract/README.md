# Shared Contract Bundle — `0.2.5-proposed`

Status: **PROPOSED / UNFROZEN — role-neutral**

This directory is the single role-neutral, stable contract shared by both peers. It
can be copied into the Thief repository byte-for-byte. It contains **specifications,
schemas, fixtures, reproducible vectors, and read-only verification tooling only**.

## What it deliberately does not contain

- No active `game.json` for one permanent match. `fixtures/match_config.example.json`
  is an example **template**, not a runtime match.
- No neutral participants presented as runtime identities. Real match
  configurations are supplied at runtime through an explicit path outside this
  bundle.
- No Cop-specific runtime or package files, ports, URLs, credentials, models, or
  strategy settings, and no mutable per-match output.

Changing opponent IDs or game identity must never require changing any file in this
bundle or its manifest.

## Layout

| Path | Purpose |
|---|---|
| `CONTRACT_VERSION` | `0.2.5-proposed` |
| `PROTOCOL_PROFILE.md` | `simulator-v3.0.0` compatibility tools, messages, and commit-reveal |
| `MATCH_CONFIGURATION.md` | how a per-match config is supplied and the three hash domains |
| `SHARED_RULES.md` | book-authoritative gameplay rules |
| `schemas/` | JSON Schemas for the match config and every protocol message |
| `fixtures/` | positive/negative example messages and the example match template |
| `vectors/` | reproducible canonicalization and hash vectors |
| `fixtures/simulator-v3.0.0-wire.golden.json` | source-derived golden compatibility messages |
| `vectors/simulator-v3.0.0-commit.golden.json` | exact ASCII and unescaped-Unicode compatibility hashes |
| `verify.py` | role-neutral, read-only bundle verifier |
| `PARITY_MANIFEST.json` | recorded per-file SHA-256 manifest |

## Interoperability profile

This bundle carries the project's `simulator-v3.0.0 compatibility profile`,
source-derived from the pinned simulator snapshot at
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`. It is a compatibility target only,
not an authenticated course handoff, book requirement, or lecturer mandate.

## Verifying (read-only)

```text
python shared_contract/verify.py
python shared_contract/verify.py --compare-root <other-repo>/shared_contract
```

`verify.py` never writes files. The manifest is regenerated only by the
repository-owner tool `scripts/generate_shared_manifest.py`.
