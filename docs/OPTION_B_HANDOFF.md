# Option-B Contract Handoff — `0.2.3-proposed`

Status: **TECHNICALLY READY FOR COORDINATOR REVIEW — UNFROZEN — NOT COPIED, NOT FROZEN**

Branch: `agent/cop-m1.5-blockers-v022`
Contract version: `0.2.3-proposed`
Interoperability profile: Option B, pinned to simulator commit
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`.

This handoff supersedes `0.2.2-proposed`, which superseded `0.2.1-proposed`,
`0.2.0-proposed`, and the rejected `0.1.0-proposed` bundle. The changes below retain
the complete repair history from `0.2.0-proposed`.

It is for coordinator review only. It does **not** self-issue
`ACCEPTED_FOR_PROVISIONAL_PARITY`, copy the bundle into Thief, freeze the contract,
or authorize `M2_GAMEPLAY`.

## Changes since `0.2.0-proposed`

### Closed in `0.2.1-proposed`

1. **Barrier placement rule corrected.** `SHARED_RULES.md` previously required a
   barrier to occupy "one cell exactly one orthogonal step from the placing peer",
   which excluded the placing peer's own cell. The book (§3.4) permits the placing
   peer to give up its movement and place the barrier either on its own current cell
   **or** on a cell exactly one orthogonal step away. The rule now states this and
   explicitly rejects diagonal and more distant targets. This removed a direct
   contradiction between the contract and the Cop domain implementation corrected at
   commit `0c20bf0`.

2. **Role alternation withdrawn.** The `## Role alternation` section was removed
   from `SHARED_RULES.md`. The six-sub-game count, stable group identity, and
   per-group score aggregation remain confirmed (Appendix F table 18), but the
   *schedule* is observed only in the pinned simulator, is not stated by the book,
   and the recorded lecturer direction of 2026-07-27 is a transcription rather than
   an authenticated announcement. It is now open `U-025`, demoted in `OB-005`, and
   the bundle asserts no series role schedule.

### Closed in `0.2.2-proposed`

3. **Unsupported required root fields removed** (coordinator blocker 2). The match
   schema required root `version` and `extensions` under
   `additionalProperties: false`, so a peer whose `game.json` follows Appendix B's
   structure — which carries neither field — was rejected outright. Both are now
   optional and still accepted when present. The internal contract version lives in
   `CONTRACT_VERSION`, not in the played configuration. New controlled fixture
   `fixtures/match_config.appendix_b.json` carries the Appendix B structure with
   neither field, and `tests/contract/test_appendix_b_conformance.py` proves it is
   accepted while unknown root fields and genuinely missing sections are still
   rejected.

4. **Cross-field configuration validation added** (coordinator blocker 7).
   Coordinates were accepted as any well-formed integer pair without checking them
   against the negotiated board. JSON Schema cannot express this, because validity
   depends on `grid_size` and `axis_start_index` in a sibling object. Contract
   loading now applies `validate_start_coordinates` after schema validation, so both
   starts must lie inside the negotiated board and must differ. `axis_start_index`
   also gains a `minimum: 0` bound, annotated `PROJECT-PROPOSED`: Appendix F states
   no bound, but a negative start index has no defined meaning for a board addressed
   by inclusive non-negative indices. `tests/contract/test_cross_field_validation.py`
   proves off-board, negative, identical, and shifted-origin starts are rejected.

The controlled file count rises from 32 to **33** with the new Appendix B fixture.

### Closed in `0.2.3-proposed`

5. **Stable bundle and active match separated completely.** Runtime loaders now
   require an explicit match path and never default to the stable example fixture.
   The match file is read once so the parsed object and `config_file_sha256` always
   describe the same bytes.

6. **Rate-limit authority made explicit.** Every run supplies a local enforcement
   mirror path. The signed match object's Gatekeeper block is authoritative and the
   mirror must equal it exactly; mirror bytes and local extensions remain outside
   parity. The local schema is version-profile checked.

7. **Nonce domains disambiguated.** `negotiate.nonce` is a public pre-play
   challenge, not a commitment nonce. Per-turn commitment nonces alone remain
   secret until post-game audit and must be generated independently rather than
   reused or derived from the challenge. Schema annotations document both domains;
   independent tests reject commitment-nonce disclosure in a live `TurnMessage`.
   M4 owns runtime lifecycle enforcement.

The controlled file count remains **33** in this revision.

## Stable bundle location

The role-neutral, copy-into-Thief bundle is the top-level `shared_contract/`
directory. It contains specifications, schemas, fixtures, reproducible vectors, and
a read-only verifier only — no active match, no runtime identities, no Cop runtime
files, and no secrets.

## Manifest

`shared_contract/PARITY_MANIFEST.json` is excluded from its own file list. Its
separately computed exact-byte SHA-256 is:

`cf214a5e7562011072940e2153ece1d0032ab29eefcdfa104024a3d86502eecf`

Superseded manifest hashes, which must not be used to authorize a copy of this
revision:

| Revision | Manifest SHA-256 |
|---|---|
| `0.2.0-proposed` | `2b473b5394608973dd088a239ff0fb6b5c3b247a898e12a742674efddcf09642` |
| `0.2.1-proposed` | `48664ac848f5422354919191ace0653db46697dc38a7250382d0449b540cfc9c` |
| `0.2.2-proposed` | `fb6b97ac1cc5c4f5d3a25ce6096593e7f08fb4e8fb4cb61dbc2c06946016167d` |

## Controlled inventory (33 files, paths relative to `shared_contract/`)

| Path | SHA-256 |
|---|---|
| `CONTRACT_VERSION` | `7bf70109b5fc620c87d476998f277d7fcaf16bb54ec1e550e965902878c4230f` |
| `MATCH_CONFIGURATION.md` | `774bc225a583dcf8b7918296c3b3edee2767d4af07604f4062ac2100fa0160c3` |
| `PROTOCOL_PROFILE.md` | `b13522a457d97c34f752b6ad03ccd1877a93357b723c62ffbea6d2b6e8053548` |
| `README.md` | `47cba741f052c05ce9da6a359027cf941e3a8e8d50b4824509fded2284a4f33f` |
| `SHARED_RULES.md` | `be9dc76efc90d3e01212a88d9a8a9509d2e6b3b29b3ca9cb5132b36d365152a7` |
| `fixtures/audit_payload.invalid.json` | `f7d71c22311509ea2bba2a490043a22fdf0e337b542b493bbc42e7d811c91a2a` |
| `fixtures/audit_payload.valid.json` | `fc5e5384bdc65d2d2163d8318e05c6ba524ea5e7c3d692765843d2958befa2d0` |
| `fixtures/audit_record.invalid.json` | `f87b3e3a0b71de113071e5e2e4f4965acadd73f99046f2e8a46c135d7b34f965` |
| `fixtures/audit_record.valid.json` | `554b7e9790ff29dfb5b945774eb5741df2b5721fde9b5f1e5c77ab4b3b588d80` |
| `fixtures/control_message.invalid.json` | `e31e2a2653db049de8b4fa4afc5fd18b8f5ddc0986fdb468088af8f64a7834f7` |
| `fixtures/control_message.valid.json` | `3e218c045b79688892486ac9fa8f924ef3e1216b60f6fd3899b0ba8a26f6ad10` |
| `fixtures/match_config.appendix_b.json` | `2584d07627a44f7f27888c56e8c6beedc1e82532601e977774bf5858c538a711` |
| `fixtures/match_config.example.json` | `70758af55f178a049a438b81eb5f9acd389c568214cb3006358c66f8d10abd06` |
| `fixtures/negotiate.invalid.json` | `6247ae2cb1e469701713718d068716e4c3db19b51131661a660dca8bf00018f4` |
| `fixtures/negotiate.valid.json` | `f9ad3dcb751f30a63e34c0bf16512e9349e19c9dddbc93e2f80f5054f67569d9` |
| `fixtures/negotiation_terms.projection.json` | `153fdbdd487ea426300a935eeb851834d0108e250804a4f62ae31712408ae5de` |
| `fixtures/per_subgame_config.invalid.json` | `4f747aaeb24f18105434abbe9e4f5dccb1480dbecf4f1e8638f16218115f9096` |
| `fixtures/per_subgame_config.valid.json` | `abee6cde6e7cd540c4e4a2efda7cfae650427547869f8f67bf2365f9e3ecfff0` |
| `fixtures/tool_response.invalid.json` | `467483ad4afd4d5551061cd22ed3e250721f60316ffab2f1b36c77b451e78135` |
| `fixtures/tool_response.valid.json` | `12b34da73b0c67a0319e6eddbd3582af66e3b558b4d44e4a6860e0cec20d726f` |
| `fixtures/turn_message.invalid.json` | `a04cdb2e2dd57bb5547b105abe999f0b54da3ae1d248dc3590c6c1ace720497a` |
| `fixtures/turn_message.valid.json` | `ff7bfd08efe44907da19fb3245c3ce9533299581590cb09e62eb63d3d6302a59` |
| `schemas/audit-payload.schema.json` | `7f78cbc667c37dfe0c223744a60b84e79df5898ad85f796123c31aca026259f1` |
| `schemas/audit-record.schema.json` | `f065ed6514d56c17414dc95b4975dbff611f9fa79f7761f3b018213bb265c894` |
| `schemas/control-message.schema.json` | `e82f8dda27896148ccab9c1f5d1fe8a9e26e6ff078f4e93e1f20454c60f36acb` |
| `schemas/match-config.schema.json` | `442ae8defb05f1f6a7a10741d57447a9ddd6d3d18e087d332a4115eeb508aa30` |
| `schemas/negotiate.schema.json` | `d132afcee171f582510eb1d888e47f1cbd3b6fa366050c3c7ab9c3b2ddf682cf` |
| `schemas/per-subgame-config.schema.json` | `38c165fd1fa94de8cf3e2611c06524e893fd0b7611e965070d9cf2922ce40888` |
| `schemas/tool-response.schema.json` | `891a430b682344e652db91adabbbf7d795e76e5ad74c67f854c1d1af5c7ffe14` |
| `schemas/turn-message.schema.json` | `f0faf1881bc19edebc07979fece14c95558153c7789f7c6bb7d89cf4f1e330c3` |
| `vectors/config-sha256.vectors.json` | `1deb487e2c96385df18569e9e8436bada8a3c853200e39e7143963ceac5052a8` |
| `vectors/move-commit.vectors.json` | `8ad6d13ea1a77add0a6f42c9463aaccb2a149345bc25206b6031fc90f58aa37d` |
| `verify.py` | `1e6cb9521e418c8b7ff162d20e1f383af7490504f28f704492d415d48f4a84da` |

## Local validation snapshot

- `uv sync --frozen`: PASS (16 packages checked)
- `uv run ruff check .`: PASS (all checks passed)
- `uv run pytest --cov --cov-branch --cov-fail-under=85`: 369 passed, 98.98%
- `uv run python scripts/check_file_lengths.py`: PASS (32 source/script, 46 test files)
- `uv run python scripts/check_secrets.py`: PASS (185 files, 0 findings)
- `uv run python shared_contract/verify.py`: PASS, 33 controlled files
- `git diff --check`: PASS

A clean manifest proves only that the controlled bytes match the manifest. It does
not prove semantic correctness or interoperability.

## What remains for the coordinator

1. Review the `0.2.3-proposed` scope, the Option-B profile, and the seven
   corrections above.
2. If accepted, authorize copying the `shared_contract/` bundle into Thief
   byte-for-byte and independent cross-bundle verification
   (`verify.py --compare-root`).
3. Only after independent parity and conformance evidence: issue
   `CONTRACT_FREEZE: GO` and, separately, `M2_GAMEPLAY: GO`.

## Decision reconciliation

All five M1.5 semantic decisions are closed:

1. **Canonicalization profile — resolved.** Configuration hashing and per-turn
   commitments use the recorded sorted-key, compact, unescaped-Unicode, UTF-8
   profile. This is binding for the project without being claimed as a universal
   book rule.
2. **FastMCP profile — resolved.** The Option-B tool names and envelope are the
   project's selected interoperability profile. Universal or book-mandated naming
   is not an additional acceptance criterion.

3. **Stable contract versus per-match identity — resolved.** The stable bundle has
   no active match; every real match is supplied explicitly.
4. **Rate-limit relationship — resolved.** The signed Gatekeeper terms are
   authoritative; an explicitly supplied local exact mirror enforces them without
   becoming a parity-controlled file.
5. **Negotiation challenge versus commitment nonce — resolved.** The public
   `negotiate.nonce` challenge is distinct from the secret per-turn commitment
   nonce.

No Cop-owned M1.5 semantic decision remains pending. Independent review, controlled
copy/parity, and freeze authorization remain external later gates.

## Open items routed to later phases

Exhaustive artifact schemas, exact `game_id`/UUID protocol, Step-0 Git/host
attestation, and six-sub-game runtime emission remain M7 work and do not expand
this bundle. The six-sub-game role schedule is open `U-025` and must be
authenticated before any series orchestration depends on it.
