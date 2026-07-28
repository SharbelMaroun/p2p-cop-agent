# Shared Contract Bundle — `0.2.1-proposed`

Status: **PROPOSED / UNFROZEN — role-neutral**

This directory is the single role-neutral, stable contract shared by both peers. It
can be copied into the Thief repository byte-for-byte. It contains **specifications,
schemas, fixtures, reproducible vectors, and read-only verification tooling only**.

## What it deliberately does not contain

- No active `game.json` for one permanent match. `fixtures/match_config.example.json`
  is an example **template**, not a runtime match.
- No neutral participants presented as runtime identities. Real match
  configurations are supplied at runtime through an explicit path or a validated
  object, outside this bundle.
- No Cop-specific runtime or package files, ports, URLs, credentials, models, or
  strategy settings, and no mutable per-match output.

Changing opponent IDs or game identity must never require changing any file in this
bundle or its manifest.

## Layout

| Path | Purpose |
|---|---|
| `CONTRACT_VERSION` | `0.2.1-proposed` |
| `PROTOCOL_PROFILE.md` | Option-B FastMCP tools, messages, and commit-reveal |
| `MATCH_CONFIGURATION.md` | how a per-match config is supplied and the three hash domains |
| `SHARED_RULES.md` | book-authoritative gameplay rules |
| `schemas/` | JSON Schemas for the match config and every protocol message |
| `fixtures/` | positive/negative example messages and the example match template |
| `vectors/` | reproducible canonicalization and hash vectors |
| `verify.py` | role-neutral, read-only bundle verifier |
| `PARITY_MANIFEST.json` | recorded per-file SHA-256 manifest |

## Interoperability profile

This bundle implements **Option B**, the documented academic-freedom project choice
pinned to lecturer simulator commit
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`. It is a wire-profile reference, not a
claim that the simulator outranks the book. See `../docs/OPTION_B_DECISION.md`.

## Verifying (read-only)

```text
python shared_contract/verify.py
python shared_contract/verify.py --compare-root <other-repo>/shared_contract
```

`verify.py` never writes files. The manifest is regenerated only by the
repository-owner tool `scripts/generate_shared_manifest.py`.
