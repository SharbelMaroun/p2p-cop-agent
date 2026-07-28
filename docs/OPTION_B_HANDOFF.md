# Option-B Contract Handoff — `0.2.2-proposed`

Status: **TECHNICALLY READY FOR COORDINATOR REVIEW — UNFROZEN — NOT COPIED, NOT FROZEN**

Branch: `agent/cop-m1.5-blockers-v022`
Contract version: `0.2.2-proposed`
Interoperability profile: Option B, pinned to simulator commit
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`.

This handoff supersedes `0.2.1-proposed`, which superseded `0.2.0-proposed`, which
superseded the rejected `0.1.0-proposed` bundle. `0.2.0-proposed` is the last
revision that was externally visible; `0.2.1` and `0.2.2` follow it directly, so the
changes below are stated against `0.2.0-proposed`.

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

## Stable bundle location

The role-neutral, copy-into-Thief bundle is the top-level `shared_contract/`
directory. It contains specifications, schemas, fixtures, reproducible vectors, and
a read-only verifier only — no active match, no runtime identities, no Cop runtime
files, and no secrets.

## Manifest

`shared_contract/PARITY_MANIFEST.json` is excluded from its own file list. Its
separately computed exact-byte SHA-256 is:

`fb6b97ac1cc5c4f5d3a25ce6096593e7f08fb4e8fb4cb61dbc2c06946016167d`

Superseded manifest hashes, which must not be used to authorize a copy of this
revision:

| Revision | Manifest SHA-256 |
|---|---|
| `0.2.0-proposed` | `2b473b5394608973dd088a239ff0fb6b5c3b247a898e12a742674efddcf09642` |
| `0.2.1-proposed` | `48664ac848f5422354919191ace0653db46697dc38a7250382d0449b540cfc9c` |

## Controlled inventory (33 files, paths relative to `shared_contract/`)

| Path | SHA-256 |
|---|---|
| `CONTRACT_VERSION` | `72f304bcc6a58333ea83bf917cc52d98d50bc6db6bc1b97387a61c4a35348eab` |
| `MATCH_CONFIGURATION.md` | `7a476b551f51f4d580de9789b091b56611dc5b0079a593723dcd85c8c3cdda3c` |
| `PROTOCOL_PROFILE.md` | `b73b17065e2fc8e2dcccc4049bd69c25c87c19ac3340a69ece2538e27f10b107` |
| `README.md` | `3315e5c71f1baa9ca7eaf99765aeacf9edc0df2d9e70b3ea5189cc54dab429e4` |
| `SHARED_RULES.md` | `a1f7ac100dc93996f7ed584da1a722b7f7489f80b10fa65831d1778784bbfa76` |
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
| `fixtures/negotiation_terms.projection.json` | `ef85355c0fe8ad3db96870bad2bc6df6d4c252840c2999c5a5241fbad7938838` |
| `fixtures/per_subgame_config.invalid.json` | `4f747aaeb24f18105434abbe9e4f5dccb1480dbecf4f1e8638f16218115f9096` |
| `fixtures/per_subgame_config.valid.json` | `abee6cde6e7cd540c4e4a2efda7cfae650427547869f8f67bf2365f9e3ecfff0` |
| `fixtures/tool_response.invalid.json` | `467483ad4afd4d5551061cd22ed3e250721f60316ffab2f1b36c77b451e78135` |
| `fixtures/tool_response.valid.json` | `12b34da73b0c67a0319e6eddbd3582af66e3b558b4d44e4a6860e0cec20d726f` |
| `fixtures/turn_message.invalid.json` | `a04cdb2e2dd57bb5547b105abe999f0b54da3ae1d248dc3590c6c1ace720497a` |
| `fixtures/turn_message.valid.json` | `ff7bfd08efe44907da19fb3245c3ce9533299581590cb09e62eb63d3d6302a59` |
| `schemas/audit-payload.schema.json` | `b39315867f9d4548a0307af3b28963154d255bd7e5e1bf1c999d29a6c7548034` |
| `schemas/audit-record.schema.json` | `e1c60ef2b38f451b223330e6fd90b6769fb844456180fdb4f1f4b65c5a16c105` |
| `schemas/control-message.schema.json` | `34960eef60e610ab3f9adb45e7aab6ddc9987a54fd08cac5700f8527b81c3edf` |
| `schemas/match-config.schema.json` | `c125aea3df0badf1bf38c013aa829b3b3c27c2d73c13141b45df2caa804a1be9` |
| `schemas/negotiate.schema.json` | `9d17a4b8467d4e003a09ef9b8b9ca1ebe16c186d957677f5cd37102bd0c2bad3` |
| `schemas/per-subgame-config.schema.json` | `cd334259ba4b52cb3539d892bdff51d8133f93e9d14596a4ba9bbfb75bdff529` |
| `schemas/tool-response.schema.json` | `6e3ac9d95a77319553a161a9ddd09029f0296f76760343f9101cddaf5a5036a2` |
| `schemas/turn-message.schema.json` | `4582f85288bbc0973b48399a07d9a9f0954a1cb4e79510410695c2629c5929b9` |
| `vectors/config-sha256.vectors.json` | `0a5cc1c872be1cc3e3a8960d0a0176d379ea8d5ca6ec70890598d60af5b34118` |
| `vectors/move-commit.vectors.json` | `a9254ef27531fde5844b1462ed9696d6cecd33828ef9d86158395de67ab4506d` |
| `verify.py` | `1e6cb9521e418c8b7ff162d20e1f383af7490504f28f704492d415d48f4a84da` |

## Local validation snapshot

- `uv sync --frozen`: PASS (16 packages checked)
- `uv run ruff check .`: PASS (all checks passed)
- `uv run pytest --cov --cov-branch --cov-fail-under=85`: 279 passed, 98.40%
- `uv run python scripts/check_file_lengths.py`: PASS (27 source/script, 38 test files)
- `uv run python scripts/check_secrets.py`: PASS (172 files, 0 findings)
- `uv run python shared_contract/verify.py`: PASS, 33 controlled files
- `git diff --check`: PASS

A clean manifest proves only that the controlled bytes match the manifest. It does
not prove semantic correctness or interoperability.

## What remains for the coordinator

1. Review the `0.2.2-proposed` scope, the Option-B profile, and the four
   corrections above.
2. If accepted, authorize copying the `shared_contract/` bundle into Thief
   byte-for-byte and independent cross-bundle verification
   (`verify.py --compare-root`).
3. Only after independent parity and conformance evidence: issue
   `CONTRACT_FREEZE: GO` and, separately, `M2_GAMEPLAY: GO`.

## Decision reconciliation

Two original objections are closed by the accepted Option-B decision:

1. **Canonicalization profile — resolved.** Configuration hashing and per-turn
   commitments use the recorded sorted-key, compact, unescaped-Unicode, UTF-8
   profile. This is binding for the project without being claimed as a universal
   book rule.
2. **FastMCP profile — resolved.** The Option-B tool names and envelope are the
   project's selected interoperability profile. Universal or book-mandated naming
   is not an additional acceptance criterion.

Three owner confirmations remain:

3. **Stable contract versus per-match identity.** Confirm that the stable bundle
   contains no active match, and require every real configuration to be supplied
   explicitly outside the example fixtures.
4. **Rate-limit relationship.** Reconcile the implemented local exact-mirror design
   with the later request to treat `rate_limits.json` itself as shared match input.
5. **Negotiation challenge versus secret nonce.** The negotiate schema exposes a
   public `nonce`, while per-turn commitment nonces remain secret until final audit.
   Confirm that the negotiate value is a separate public challenge rather than a
   commitment nonce.

## Open items routed to later phases

Exhaustive artifact schemas, exact `game_id`/UUID protocol, Step-0 Git/host
attestation, and six-sub-game runtime emission remain M7 work and do not expand
this bundle. The six-sub-game role schedule is open `U-025` and must be
authenticated before any series orchestration depends on it.
