# Coordinator Provisional Copy Authorization Request

Prepared by: Cop team (AmrSafadi)
For: Coordinator (`rmisegal@gmail.com`)
Purpose: Obtain the six provisional handoff values the Thief team requires
         before they may copy any controlled file.

## Background

The Thief repository `CONTRACT_HANDOFF_CHECKLIST.md` (Stage A) is fail-closed
and requires the coordinator to supply six exact values before the Thief team
copies a single byte. This document pre-assembles five of those six values from
the Cop-local manifest. The coordinator must supply the sixth: the provisional
verdict.

The Cop branch must be pushed to remote before the coordinator sends these
values, so that `PROVISIONAL_COP_COMMIT` is remotely accessible to the Thief.

## Cop prerequisite action

Push the Cop branch so the commit is remotely available:

```
git push origin agent/cop-m1-contract-revision
```

The commit the coordinator should supply as `PROVISIONAL_COP_COMMIT` is the
branch HEAD immediately after that push. Retrieve it with:

```
git rev-parse origin/agent/cop-m1-contract-revision
```

---

## Six provisional handoff values (for coordinator to forward to Thief)

### 1. `PROVISIONAL_COP_COMMIT`

```
[insert full 40-hex SHA returned by git rev-parse origin/agent/cop-m1-contract-revision after push]
```

All controlled-file bytes are identical from baseline commit
`e0df5ba530fd7c433d41a98c5976ca7e08cdfa53` through the pushed HEAD. Only
non-controlled handoff documentation changed after that baseline. The coordinator
may verify a conservative superset of the controlled paths with:

```
git diff --exit-code e0df5ba <pushed-HEAD> -- .gitattributes config/game.json docs/contracts docs/schemas scripts/check_shared_contracts.py scripts/shared_contract_integrity.py tests/fixtures/contracts
```

### 2. `PROVISIONAL_CONTRACT_VERSION`

```
0.1.0-proposed
```

The contract remains explicitly proposed and unfrozen. The coordinator may
accept it for provisional parity testing without freezing it.

### 3. `PROVISIONAL_MANIFEST_SHA256`

```
473982dc01594b1c7abee8fc7f20cf665a6b245e53114ed4a2732c115a35d86a
```

This is the SHA-256 of the exact bytes of
`docs/contracts/PARITY_MANIFEST.json` at the source commit. The Thief must
recompute this independently and confirm it matches.

### 4. `PROVISIONAL_CONTROLLED_PATHS` (complete ordered list, 18 paths)

```
.gitattributes
config/game.json
docs/contracts/ARTIFACT_CONTRACT.md
docs/contracts/CONTRACT_VERSION
docs/contracts/LEAGUE_CONTRACT.md
docs/contracts/MATCH_CONFIGURATION.md
docs/contracts/PRIVATE_CONFIGURATION.md
docs/contracts/SHARED_RULES.md
docs/schemas/artifact-keyset-fixture.schema.json
docs/schemas/config-hash-vector.schema.json
docs/schemas/game-config.schema.json
scripts/check_shared_contracts.py
scripts/shared_contract_integrity.py
tests/fixtures/contracts/agreed_config.keyset.json
tests/fixtures/contracts/declaration.keyset.json
tests/fixtures/contracts/final_result.keyset.json
tests/fixtures/contracts/game-config-sha256.vector.json
tests/fixtures/contracts/game_log.keyset.json
```

### 5. Per-file SHA-256 hashes (18 entries, same order)

| Path | SHA-256 |
|---|---|
| `.gitattributes` | `f9eaec26456d492ccc58aec75ce3a8e6e7680fb158b23da3977bcfa02b22c1ba` |
| `config/game.json` | `70758af55f178a049a438b81eb5f9acd389c568214cb3006358c66f8d10abd06` |
| `docs/contracts/ARTIFACT_CONTRACT.md` | `33d218b9d071ae40b7cd90f802c75a170cb30e9fd0c43eb61c2622140f034337` |
| `docs/contracts/CONTRACT_VERSION` | `9e061d4d08ca911d12915da01033a8a9f03cd0329a6ba33bbb953d6bba9edbda` |
| `docs/contracts/LEAGUE_CONTRACT.md` | `fac906032ac8a7138b177d2512940d84692ebec23f5377b8c0ccc0bb53b9af78` |
| `docs/contracts/MATCH_CONFIGURATION.md` | `e476ebafeed0d66522a7d96535d43dfc7f598413b0b1553d6d5e8c973afd2f23` |
| `docs/contracts/PRIVATE_CONFIGURATION.md` | `16b13bc8e8dd3cf17234a27e36623970153961d322b4895d3be9241931eeb745` |
| `docs/contracts/SHARED_RULES.md` | `ce080c2edc9b9965f0b2601144a425d22a25623f305af1a16a7c9aa39733a643` |
| `docs/schemas/artifact-keyset-fixture.schema.json` | `8e56b199fb6339a1d085422face33fac8313efd8b7d0d142774607b2febd7a3f` |
| `docs/schemas/config-hash-vector.schema.json` | `6477d028ac010cd5ae288f6d469ba8ca89055fe7681f8937fbcedc52f3878d86` |
| `docs/schemas/game-config.schema.json` | `fda84cf295788fda09e93e0e56d8876ae549ff7f1e99391d03552e86f04860d9` |
| `scripts/check_shared_contracts.py` | `b29bd3c978baf7b1b988e7a37c644cdc3b3e5fb548e852e0238fa95bac855b39` |
| `scripts/shared_contract_integrity.py` | `3f9dc0eb48a8ca9c5de83a287ffffb88bcc27aec7aeb6e64fe59140e6591b78b` |
| `tests/fixtures/contracts/agreed_config.keyset.json` | `a82c0f98a9eccb35d13dffb5287f1c74f65918008de4c178c3565540cb1ec1bf` |
| `tests/fixtures/contracts/declaration.keyset.json` | `fa80c357f5b9b1266ca8b22f9a588d7644735ef948ff26744e0e1b4e0232eeb4` |
| `tests/fixtures/contracts/final_result.keyset.json` | `032da7375bb220a298858d89d214a8504946cfa783e815940474bd354deec479` |
| `tests/fixtures/contracts/game-config-sha256.vector.json` | `116f790324b0bdfd28cc38926c2667ae6c9feabaea7b4e2e74662e5fc8dbea54` |
| `tests/fixtures/contracts/game_log.keyset.json` | `d084554908c831f7924b8ce943470443f3ee82ef829e8f0b2b44dc0017c3639b` |

### 6. Coordinator provisional verdict (coordinator fills this in)

```
ACCEPTED_FOR_PROVISIONAL_PARITY: [YES / NO — with rationale if NO]
```

If YES, the coordinator forwards items 1–6 to the Thief team. If NO, the
coordinator supplies the rationale and a revised candidate scope if applicable.

---

## What this authorization permits

Provisional copy authorization permits the Thief to:

- Copy the 18 controlled files from `PROVISIONAL_COP_COMMIT` exactly.
- Recompute and verify every per-file SHA-256 and the manifest self-hash.
- Run their own quality and contract gates against the copied bundle.
- Perform Stage B parity and conformance testing.

It does **not** authorize:

- Contract freeze (that is Stage C, requiring the coordinator's
  `CONTRACT_FREEZE: GO`).
- M2 gameplay on either side (that requires a separate `M2_GAMEPLAY: GO`).
- Editing, reformatting, or partially selecting any controlled file.
- Adding Thief-authored shared fields or competing schemas.

---

## Cop local validation snapshot (at time of this request)

All checks were run against branch `agent/cop-m1-contract-revision`:

- `uv sync --frozen`: PASS
- `ruff check .`: PASS
- `pytest --cov --cov-branch --cov-fail-under=85`: 79 PASS, 92.09% coverage
- `check_file_lengths.py`: PASS
- `check_secrets.py`: PASS
- `check_shared_contracts.py`: PASS — 18 files,
  manifest `473982dc01594b1c7abee8fc7f20cf665a6b245e53114ed4a2732c115a35d86a`
- `git diff --check`: PASS
- Cross-root Thief comparison: NO-GO (expected — Thief has not consumed the bundle)
