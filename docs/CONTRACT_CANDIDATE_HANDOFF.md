# M1 Contract Candidate Handoff

Status: **REVIEWABLE COP CANDIDATE — UNFROZEN — NO-GO**

Source base: `84339c210c8e3293d972bccec5912abf519d502c`

Branch: `agent/cop-m1-contract-revision`

Contract version: `0.1.0-proposed`

This handoff is for coordinator review only. It does not authorize copying to Thief,
contract freeze, M2 gameplay, merge, push, or PR mutation.

## Controlled exact-byte inventory

`docs/contracts/PARITY_MANIFEST.json` is deliberately excluded from this table. Its
separately computed exact-byte SHA-256 is
`6e769ac49f4ffd064ada3a5486d7c5b2768feace2fced2b16e7de09e12c65689`.

| Controlled path | SHA-256 |
|---|---|
| `.gitattributes` | `f9eaec26456d492ccc58aec75ce3a8e6e7680fb158b23da3977bcfa02b22c1ba` |
| `config/game.json` | `a06fc6d316240f0f089a3d33966527082c5f6c229a1232b5d8e14987269472af` |
| `config/rate_limits.json` | `f2d173e9bf6c31ea30a14d6b4b81801c46fa155eaefa04548eeedf26107c7814` |
| `docs/contracts/CONTRACT_VERSION` | `9e061d4d08ca911d12915da01033a8a9f03cd0329a6ba33bbb953d6bba9edbda` |
| `docs/contracts/LEAGUE_CONTRACT.md` | `d808d743954f3fd09413860fe21d378728bb4b58171af0cf4c32fcede76ca1db` |
| `docs/contracts/MATCH_CONFIGURATION.md` | `b3df0b84a708c8ca44d6c608ba7dd7f49b35c68368304a1ced3f320677cc7c04` |
| `docs/contracts/PRIVATE_CONFIGURATION.md` | `32f8beb459c91942d44720d4b2151a05d26aebcfdef5aff62e90834113fed45b` |
| `docs/contracts/SHARED_RULES.md` | `4d73fa8a7a9e31cbf4243e9ea0b7858769db17854516a99be6c5fdf920f6d7d5` |
| `docs/schemas/artifact-keyset-fixture.schema.json` | `8e56b199fb6339a1d085422face33fac8313efd8b7d0d142774607b2febd7a3f` |
| `docs/schemas/game-config.schema.json` | `b4da34a2ffeb616bb36a3a3f18170b033818cb88632a5d154e44bd9f893b33ff` |
| `docs/schemas/rate-limits.schema.json` | `b4b837751e1a5ec75620cc877b511790c543d251c2ffd01fd0f0d81112418591` |
| `scripts/check_shared_contracts.py` | `b29bd3c978baf7b1b988e7a37c644cdc3b3e5fb548e852e0238fa95bac855b39` |
| `scripts/shared_contract_integrity.py` | `2a3d1dfcb532aaca4c38c5a9ba21f28045f130588626d9d2981ccce06dc1e06f` |
| `tests/fixtures/contracts/agreed_config.keyset.json` | `a82c0f98a9eccb35d13dffb5287f1c74f65918008de4c178c3565540cb1ec1bf` |
| `tests/fixtures/contracts/declaration.keyset.json` | `fa80c357f5b9b1266ca8b22f9a588d7644735ef948ff26744e0e1b4e0232eeb4` |
| `tests/fixtures/contracts/final_result.keyset.json` | `032da7375bb220a298858d89d214a8504946cfa783e815940474bd354deec479` |
| `tests/fixtures/contracts/game_log.keyset.json` | `d084554908c831f7924b8ce943470443f3ee82ef829e8f0b2b44dc0017c3639b` |

## Evidence-backed decisions

- Appendix F values retain `Fixed`, `Minimum`, or `Negotiated` semantics and explicit
  ownership.
- The book-defined artifact filename patterns and six-sub-game series are mandatory.
- Shared match values are mutually agreed and identical; private TOML remains local.
- Ports, local URL storage, models, credentials, strategies, secrets, and nonces do
  not enter the public bundle.

## Proposed decisions

- The Cop-authored 17-file controlled bundle and manifest format.
- A neutral two-participant ordered `agreed_between` array.
- A split `game.json`/`rate_limits.json` match fixture using profile 1.2.
- Root `version: "1.00"`, JSON field names, closed known fields, and explicit
  `extensions` objects.
- `game_id`, `sub_game_number`, and `config_name` as proposed match bindings.
- Structural match comparison before canonical match hashing is defined.

## P0 blockers

- Four local generated JSON artifacts lack authenticated official provenance.
- Formal schema compatibility among 1.1, 1.2, and 1.3 is unknown.
- Unified versus split config and exact field placement are unresolved.
- Participant identifier format and deterministic ordering are unresolved.
- Required identity/link fields and six-game artifact lifecycle are unresolved.
- `config_sha256` scope, self-hash exclusion, and canonical bytes are unresolved.
- Role assignment or alternation across six sub-games is unresolved.
- Thief has not consumed an accepted candidate and cross-repository parity is absent.

## Local validation snapshot

- `uv sync --frozen`: PASS
- Ruff: PASS
- Pytest: 69 PASS
- Branch coverage: 91.94%
- File lengths: PASS
- Secret scan: PASS
- Cop-local contract integrity: PASS, 17 controlled files
- `git diff --check`: PASS

These local results must be independently reproduced during coordinator and future
Thief review.
