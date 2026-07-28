# M1 Contract Candidate Handoff

Status: **TECHNICALLY READY FOR EXTERNAL REVIEW — UNFROZEN — NO-GO UNTIL PARITY**

Controlled-byte baseline: `e0df5ba530fd7c433d41a98c5976ca7e08cdfa53`

No controlled file has changed after that baseline. The coordinator should use the
full pushed branch HEAD as `PROVISIONAL_COP_COMMIT`; the baseline remains the stable
reference for proving that later handoff-only documentation did not alter the
candidate bundle.

Branch: `agent/cop-m1-contract-revision`

Contract version: `0.1.0-proposed`

This handoff is for coordinator review. Cop-owned M1 checks pass, but it does not
authorize contract freeze or M2 gameplay. Copying the accepted controlled bundle to
Thief is the next external review step; merge, push, and PR mutation remain separate
repository-owner decisions.

## Controlled exact-byte inventory

`docs/contracts/PARITY_MANIFEST.json` is deliberately excluded from this table. Its
separately computed exact-byte SHA-256 is
`473982dc01594b1c7abee8fc7f20cf665a6b245e53114ed4a2732c115a35d86a`.

| Controlled path | SHA-256 |
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
- Logical artifact links retain `<NN>` while physical config/log names resolve
  `g01` through `g06`.
- The complete shared `game.json` object hashes to
  `adac9efe6d51b9487c400a04c2e185af9fb3622e1a7d74f18d400425656d82db`
  under the recorded sorted/compact/UTF-8 SHA-256 vector.
- The exact source bytes of `config/game.json` hash to
  `70758af55f178a049a438b81eb5f9acd389c568214cb3006358c66f8d10abd06`;
  both the semantic/canonical and exact-byte locks are checked.
- `config/rate_limits.json` is local enforcement, not a byte-identical peer term.
  Its shared Gatekeeper values may not weaken or contradict `game.json`.
- Ports, local URL storage, models, credentials, strategies, secrets, and nonces do
  not enter the public bundle.

## Proposed decisions

- The Cop-authored 18-file controlled bundle and manifest format. “18” is an
  internal review inventory, not a lecturer-defined file count.
- Source-profile 1.2 acceptance without cross-profile normalization.
- Root `version: "1.00"`, JSON field names, closed known fields, and explicit
  `extensions` objects.

## M1 freeze dependencies

1. Coordinator acceptance of this exact proposed scope.
2. Thief byte-for-byte consumption followed by independent local and cross-root
   verification, including the separate manifest hash.

The following remain explicit M4/M7 work rather than M1 blockers: complete artifact
schemas and compatibility, exact `game_id` syntax, the conflicting UUID creation
protocols, Step-0 Git/host attestation, resolved physical artifact emission, and a
complete six-sub-game stub audit. Original Moodle checksum provenance remains a
narrow source-label caveat and does not change the project owner's designation of
the sibling `Json-examples/` files as course examples.

## Local validation snapshot

- `uv sync --frozen`: PASS
- Ruff: PASS
- Pytest: 79 PASS
- Branch coverage: 92.09%
- File lengths: PASS
- Secret scan: PASS
- Cop-local contract integrity: PASS, 18 controlled files
- Read-only Thief comparison: expected NO-GO; 16 paths plus the manifest are
  missing and the two present controlled paths differ
- `git diff --check`: PASS

These local results must be independently reproduced during coordinator and future
Thief review.
