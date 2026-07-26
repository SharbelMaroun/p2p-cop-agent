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
`ed09244a6b05a4832b8f4d85bc5881ae9eaea139023cd0e946b2bf994b32ad2d`.

| Controlled path | SHA-256 |
|---|---|
| `.gitattributes` | `f9eaec26456d492ccc58aec75ce3a8e6e7680fb158b23da3977bcfa02b22c1ba` |
| `config/game.json` | `70758af55f178a049a438b81eb5f9acd389c568214cb3006358c66f8d10abd06` |
| `config/rate_limits.json` | `0445c96a1ea23ce9c79dcb1ae3151e5d02f5aa78f765bf5bc995d7ddbfbda3e2` |
| `docs/contracts/ARTIFACT_CONTRACT.md` | `12db7ed7a7aee26a9ebd2cc3e58abfff6a909fc330fad3eaafc8ced5b716f1e3` |
| `docs/contracts/CONTRACT_VERSION` | `9e061d4d08ca911d12915da01033a8a9f03cd0329a6ba33bbb953d6bba9edbda` |
| `docs/contracts/LEAGUE_CONTRACT.md` | `fac906032ac8a7138b177d2512940d84692ebec23f5377b8c0ccc0bb53b9af78` |
| `docs/contracts/MATCH_CONFIGURATION.md` | `a09ec11c1f0ce30593777fd93870c7781fc7d305689f4dacc2a988e23e0ed86d` |
| `docs/contracts/PRIVATE_CONFIGURATION.md` | `8d11cf5ed43c760c8d4adbdddb9066fb9b987911c8bc6a08f25624f17662dbf6` |
| `docs/contracts/SHARED_RULES.md` | `7860f208d582dd1a9a639c58f93dd43ca7b4f2e0548c22adac13b114e911813a` |
| `docs/schemas/artifact-keyset-fixture.schema.json` | `8e56b199fb6339a1d085422face33fac8313efd8b7d0d142774607b2febd7a3f` |
| `docs/schemas/config-hash-vector.schema.json` | `6477d028ac010cd5ae288f6d469ba8ca89055fe7681f8937fbcedc52f3878d86` |
| `docs/schemas/game-config.schema.json` | `fda84cf295788fda09e93e0e56d8876ae549ff7f1e99391d03552e86f04860d9` |
| `docs/schemas/rate-limits.schema.json` | `fb44c9c94dfaeedd146fbca47458503ee9bc4939bf8cda19512e719dece50078` |
| `scripts/check_shared_contracts.py` | `b29bd3c978baf7b1b988e7a37c644cdc3b3e5fb548e852e0238fa95bac855b39` |
| `scripts/shared_contract_integrity.py` | `2a3d1dfcb532aaca4c38c5a9ba21f28045f130588626d9d2981ccce06dc1e06f` |
| `tests/fixtures/contracts/agreed_config.keyset.json` | `a82c0f98a9eccb35d13dffb5287f1c74f65918008de4c178c3565540cb1ec1bf` |
| `tests/fixtures/contracts/declaration.keyset.json` | `fa80c357f5b9b1266ca8b22f9a588d7644735ef948ff26744e0e1b4e0232eeb4` |
| `tests/fixtures/contracts/final_result.keyset.json` | `032da7375bb220a298858d89d214a8504946cfa783e815940474bd354deec479` |
| `tests/fixtures/contracts/game-config-sha256.vector.json` | `116f790324b0bdfd28cc38926c2667ae6c9feabaea7b4e2e74662e5fc8dbea54` |
| `tests/fixtures/contracts/game_log.keyset.json` | `d084554908c831f7924b8ce943470443f3ee82ef829e8f0b2b44dc0017c3639b` |

## Evidence-backed decisions

- Appendix F values retain `Fixed`, `Minimum`, or `Negotiated` semantics and explicit
  ownership.
- The book-defined artifact filename patterns and six-sub-game series are mandatory.
- Shared match values are mutually agreed and identical; private TOML remains local.
- `agreed_between` is a byte-significant two-group list whose agreed order is
  preserved.
- Natural role is used on odd sub-games and the opposite role on even sub-games.
- All artifact families share `game_id`, UUID `game_uid`, and `links`; config/log are
  per sub-game while declaration/result are per series.
- The complete shared `game.json` object hashes to
  `adac9efe6d51b9487c400a04c2e185af9fb3622e1a7d74f18d400425656d82db`
  under the recorded sorted/compact/UTF-8 SHA-256 vector.
- Ports, local URL storage, models, credentials, strategies, secrets, and nonces do
  not enter the public bundle.

## Proposed decisions

- The Cop-authored 20-file controlled bundle and manifest format.
- Source-profile 1.2 acceptance without cross-profile normalization.
- `rate_limits.json` as an operational mirror; whether its exact bytes stay in
  cross-repository parity needs coordinator/Thief acceptance.
- Root `version: "1.00"`, JSON field names, closed known fields, and explicit
  `extensions` objects.

## P0 blockers

- Four local generated JSON artifacts lack authenticated official provenance.
- Formal schema compatibility among 1.1, 1.2, and 1.3 is unknown.
- Formal group/game identifier syntax, UUID version/derivation, and `links`
  resolution remain unknown.
- Complete artifact required/optional/type/conditional rules remain unknown.
- Operational-mirror parity scope has not been accepted.
- Thief has not consumed an accepted candidate and cross-repository parity is absent.

## Local validation snapshot

- `uv sync --frozen`: PASS
- Ruff: PASS
- Pytest: 77 PASS
- Branch coverage: 92.72%
- File lengths: PASS
- Secret scan: PASS
- Cop-local contract integrity: PASS, 20 controlled files
- `git diff --check`: PASS

These local results must be independently reproduced during coordinator and future
Thief review.
