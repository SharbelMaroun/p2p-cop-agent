# Shared Contract Bundle — `0.2.10-proposed`

Status: **PROPOSED / UNFROZEN — role-neutral**

This directory is the single role-neutral, stable contract this peer implements. It
contains **specifications, schemas, fixtures, reproducible vectors, and read-only
verification tooling only**.

**It may be offered to any opponent, and carries no live state.** The book recommends
sharing the *formula* — chapter 6 recommends publishing the scent model so both sides
run identical logic — while Appendix E rule 2 **prohibits** sharing memory or variables
between parties, on pain of "immediate disqualification due to data leakage", and the
same chapter extends that to importing "a shared module that maintains live state".
Nothing here holds state, so offering it is the recommended half, not the prohibited one.

**Copying it is not evidence that two agents can play.** The book's evidence of
interoperability is a replay screenshot showing **`Verified OK`** for a real match
(§7.4, and the submission requirements in Appendix C), which is why warm-up games are
explicitly permitted — Appendix E
rule 52: "warm-up games that do not count are permitted". Byte-parity with one peer is
evidence about that peer and nothing else; an opponent conforms by implementing
`PROTOCOL_PROFILE.md`, not by holding these bytes.

**This bundle is not copied into our companion Thief repository.** That model was
retired on 2026-07-28 under `THIEF-002`. The book names the exact hazard in the
"each agent runs its own server instance" section: the separation matters "specifically
during the development stage, when one team builds on the same machine both the Police
and the Thief" — which is our situation.

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
| `CONTRACT_VERSION` | `0.2.10-proposed` |
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
