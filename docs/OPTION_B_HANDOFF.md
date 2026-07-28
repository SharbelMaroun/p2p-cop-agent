# Option-B Contract Handoff — `0.2.1-proposed`

Status: **TECHNICALLY READY FOR COORDINATOR REVIEW — UNFROZEN — NOT COPIED, NOT FROZEN**

Branch: `agent/cop-contract-semantic-fixes`
Contract version: `0.2.1-proposed`
Interoperability profile: Option B, pinned to simulator commit
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`.

This handoff supersedes `0.2.0-proposed`, which in turn superseded the rejected
`0.1.0-proposed` bundle. It is for coordinator review only. It does **not**
self-issue `ACCEPTED_FOR_PROVISIONAL_PARITY`, copy the bundle into Thief, freeze the
contract, or authorize `M2_GAMEPLAY`.

## Changes since `0.2.0-proposed`

Two semantic corrections, both inside the controlled bundle:

1. **Barrier placement rule corrected.** `SHARED_RULES.md` previously required a
   barrier to occupy "one cell exactly one orthogonal step from the placing peer",
   which excluded the placing peer's own cell. The book (§3.4) permits the placing
   peer to give up its movement and place the barrier either on its own current cell
   **or** on a cell exactly one orthogonal step away. The rule now states this, and
   explicitly rejects diagonal and more distant targets. This removes a direct
   contradiction between the contract and the Cop domain implementation corrected at
   commit `0c20bf0`.

2. **Role alternation withdrawn from the contract.** The `## Role alternation`
   section was removed from `SHARED_RULES.md`. The six-sub-game count, stable group
   identity, and per-group score aggregation remain confirmed (Appendix F table 18),
   but the *schedule* (natural role on odd sub-games, opposite on even) is observed
   only in the pinned simulator. It is not stated by the book, and the recorded
   lecturer direction of 2026-07-27 is a transcription rather than an authenticated
   Moodle announcement or original lecturer message. It is now recorded as open
   `U-025` and demoted in ledger entry `OB-005`, and the bundle asserts no series
   role schedule at all.

The version string was bumped from `0.2.0-proposed` to `0.2.1-proposed` across all
carrying files so the earlier manifest hash remains unambiguously bound to the
earlier byte set. The controlled file count is unchanged at 32.

## Stable bundle location

The role-neutral, copy-into-Thief bundle is the top-level `shared_contract/`
directory. It contains specifications, schemas, fixtures, reproducible vectors, and
a read-only verifier only — no active match, no runtime identities, no Cop runtime
files, and no secrets.

## Manifest

`shared_contract/PARITY_MANIFEST.json` is excluded from its own file list. Its
separately computed exact-byte SHA-256 is:

`48664ac848f5422354919191ace0653db46697dc38a7250382d0449b540cfc9c`

The superseded `0.2.0-proposed` manifest hash was
`2b473b5394608973dd088a239ff0fb6b5c3b247a898e12a742674efddcf09642`. It must not be
used to authorize a copy of this revision.

## Controlled inventory (32 files, paths relative to `shared_contract/`)

| Path | SHA-256 |
|---|---|
| `CONTRACT_VERSION` | `4ae4093c947bf964d364a2337861707301014c9cd395ba3555a2a81ce360d89e` |
| `MATCH_CONFIGURATION.md` | `0446b1756f754246230d690dceabdda11d35b44d055019a4a1bed84a50949f2d` |
| `PROTOCOL_PROFILE.md` | `1ac855d441f4a0f657449724c3a3f4601b24a26501a7570d5d461afc49ca1b48` |
| `README.md` | `c2fba76e4a465fea259655272b0524e027bcf7c94163de2cacaa9c6af3aebbdc` |
| `SHARED_RULES.md` | `180e1205f9e4ae00f6e055eff73a219f1340e7dbbe7c4ad5788fdcbf2f4b7d82` |
| `fixtures/audit_payload.invalid.json` | `f7d71c22311509ea2bba2a490043a22fdf0e337b542b493bbc42e7d811c91a2a` |
| `fixtures/audit_payload.valid.json` | `fc5e5384bdc65d2d2163d8318e05c6ba524ea5e7c3d692765843d2958befa2d0` |
| `fixtures/audit_record.invalid.json` | `f87b3e3a0b71de113071e5e2e4f4965acadd73f99046f2e8a46c135d7b34f965` |
| `fixtures/audit_record.valid.json` | `554b7e9790ff29dfb5b945774eb5741df2b5721fde9b5f1e5c77ab4b3b588d80` |
| `fixtures/control_message.invalid.json` | `e31e2a2653db049de8b4fa4afc5fd18b8f5ddc0986fdb468088af8f64a7834f7` |
| `fixtures/control_message.valid.json` | `3e218c045b79688892486ac9fa8f924ef3e1216b60f6fd3899b0ba8a26f6ad10` |
| `fixtures/match_config.example.json` | `70758af55f178a049a438b81eb5f9acd389c568214cb3006358c66f8d10abd06` |
| `fixtures/negotiate.invalid.json` | `6247ae2cb1e469701713718d068716e4c3db19b51131661a660dca8bf00018f4` |
| `fixtures/negotiate.valid.json` | `f9ad3dcb751f30a63e34c0bf16512e9349e19c9dddbc93e2f80f5054f67569d9` |
| `fixtures/negotiation_terms.projection.json` | `d208a670bd9ef62190e60dae5cce470b44d3043ee388d5037fb11243cb4acd60` |
| `fixtures/per_subgame_config.invalid.json` | `4f747aaeb24f18105434abbe9e4f5dccb1480dbecf4f1e8638f16218115f9096` |
| `fixtures/per_subgame_config.valid.json` | `abee6cde6e7cd540c4e4a2efda7cfae650427547869f8f67bf2365f9e3ecfff0` |
| `fixtures/tool_response.invalid.json` | `467483ad4afd4d5551061cd22ed3e250721f60316ffab2f1b36c77b451e78135` |
| `fixtures/tool_response.valid.json` | `12b34da73b0c67a0319e6eddbd3582af66e3b558b4d44e4a6860e0cec20d726f` |
| `fixtures/turn_message.invalid.json` | `a04cdb2e2dd57bb5547b105abe999f0b54da3ae1d248dc3590c6c1ace720497a` |
| `fixtures/turn_message.valid.json` | `ff7bfd08efe44907da19fb3245c3ce9533299581590cb09e62eb63d3d6302a59` |
| `schemas/audit-payload.schema.json` | `c576e2d02656d1abdb9fdcbf5a9b9677788fcdd26c5d907dbbf095723f337991` |
| `schemas/audit-record.schema.json` | `b9e7da4e1ccd567cae7063fe705eb6246fd1865fcebe208409385ff5efe7b7cc` |
| `schemas/control-message.schema.json` | `10428efd316faff48f1767937c39c35d3634a2669a93291633459dff70da451c` |
| `schemas/match-config.schema.json` | `10c20c06da390cfce1f4b7be0a04d40799ed592e55ceb8b0960e07af84d2fe68` |
| `schemas/negotiate.schema.json` | `528bfa3bf6e89b437cdb323715e8963e3d77334653eeff244ea18a11daa3d4af` |
| `schemas/per-subgame-config.schema.json` | `41bae03d676e59a0107ab2fa14a1536282e5095e97856c5c003fa946ea2c76a0` |
| `schemas/tool-response.schema.json` | `86cf880aac650a33d4887b291563663659eb4d4bd559e8d893d29f1547e24bd5` |
| `schemas/turn-message.schema.json` | `2a6f96ae40c2a8b5ad0731ff2714e6fb996ded3b8147786d98e05faef27a614d` |
| `vectors/config-sha256.vectors.json` | `bf435553073cd7c10d69d873cbb86c92504e6c4ab1686c76fb7db0b261edcd38` |
| `vectors/move-commit.vectors.json` | `370136bd6019455dea5d7943afbc68747b00cf696d43ac0b6d5c38a580a85ebb` |
| `verify.py` | `1e6cb9521e418c8b7ff162d20e1f383af7490504f28f704492d415d48f4a84da` |

## Local validation snapshot

- `uv sync --frozen`: PASS (16 packages checked)
- `uv run ruff check .`: PASS (all checks passed)
- `uv run pytest --cov --cov-branch --cov-fail-under=85`: 245 passed, 98.23%
- `uv run python scripts/check_file_lengths.py`: PASS (26 source/script, 34 test files)
- `uv run python scripts/check_secrets.py`: PASS (165 files, 0 findings)
- `uv run python shared_contract/verify.py`: PASS, 32 controlled files
- `git diff --check`: PASS

A clean manifest proves only that the controlled bytes match the manifest. It does
not prove semantic correctness or interoperability.

## What remains for the coordinator

1. Review the `0.2.1-proposed` scope, the Option-B profile, and the two corrections
   above.
2. If accepted, authorize copying the `shared_contract/` bundle into Thief
   byte-for-byte and independent cross-bundle verification
   (`verify.py --compare-root`).
3. Only after independent parity and conformance evidence: issue
   `CONTRACT_FREEZE: GO` and, separately, `M2_GAMEPLAY: GO`.

## Still-open contract blockers

This revision addresses the barrier-rule and role-alternation items only. The
following remain open and unchanged, and none of them is resolved by a clean
manifest:

1. Separation of stable contract files from per-match identity and configuration.
2. Unsupported required root fields, including candidate fields such as `version`
   and `extensions`.
3. The relationship between nested rate-limit configuration and a separate
   `rate_limits.json`.
4. Exact configuration hashing and per-turn commitment canonicalization.
5. Universal FastMCP interoperability is not proven from the official book.
6. Cross-field coordinate, origin, direction, bounds, and starting-position
   validation.

## Open items routed to later phases

Exhaustive artifact schemas, exact `game_id`/UUID protocol, Step-0 Git/host
attestation, and six-sub-game runtime emission remain M7 work and do not expand
this bundle. The six-sub-game role schedule is now open `U-025` and must be
authenticated before any series orchestration depends on it.
