# Option-B Contract Handoff — `0.2.8-proposed`

Status: **TECHNICALLY READY FOR COORDINATOR REVIEW — UNFROZEN — NOT COPIED, NOT FROZEN**

Branch: `agent/cop-m1.5-blockers-v022`
Contract version: `0.2.8-proposed`
Interoperability profile: Option B, pinned to simulator commit
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`.

This handoff supersedes `0.2.4-proposed`, which superseded `0.2.3-proposed`,
`0.2.2-proposed`, `0.2.1-proposed`, `0.2.0-proposed`, and the rejected
`0.1.0-proposed` bundle. The changes below retain the complete repair history from
`0.2.0-proposed`.

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

### Closed in `0.2.4-proposed`

The wire schemas were pinned to the `simulator-v3.0.0` compatibility profile
(negotiate `terms`/`identity`, sparse `smell_grid` cell-map, typed claim objects,
enumerated `result_claim`) and two golden compatibility artifacts were added:
`fixtures/simulator-v3.0.0-wire.golden.json` and
`vectors/simulator-v3.0.0-commit.golden.json`. Where that profile **conflicted with
confirmed sources**, it was corrected toward the book and docs rather than the
simulator (authority #7 is a reference, not an override):

8. **`result_claim` restored to the Appendix F outcomes.** The enum is
   `capture`/`survival`/`tie`; the non-book `timeout` value was dropped and the
   confirmed **Tie** outcome (table 17) re-added. Technical loss is adjudicated from
   a commit-reveal mismatch (Appendix E rules 19/48), not self-claimed.

9. **`min_center_intensity` demoted to optional.** Appendix F table 16 fixes only
   center intensity `0.9`, decay `0.10`, and the 5×5 field, so the simulator floor
   is tolerated when present but never required.

10. **`receive_control` kept optional** per ADR-001, reversing an in-place flip to
    required that no book/Appendix-E source supports.

The controlled file count rises from 33 to **35** with the two golden artifacts.

### Revised in `0.2.6-proposed` (2026-08-06)

One change, and it is a **relaxation**, so a peer conformant to `0.2.5-proposed` remains
conformant here: the commitment-nonce pattern moved from `^[0-9a-f]{32}$` to
`^[0-9a-f]+$` in `audit-record`, `audit-payload`, and the `negotiate` challenge.

The old pattern imposed a length the book never requires. Appendix E rule 19 sanctions
"any mismatch between the recomputed hash and the hash declared during the commitment
phase" (`inst/police_thief_p2p_Summary.md:1270`) -- a *digest* mismatch. A peer revealing
a longer nonce whose digest reproduces exactly was being reported `TAMPERED`, which is an
iron-rule verdict with no appeal, so we were ending fairly played games and accusing
classmates of forgery. The book shows `secrets.token_hex(16)` in its own example code
but states no requirement, and the reference validates no nonce format at all. See
`C-033`.

Our own generation is unchanged and still emits exactly 32 lowercase hex; the relaxation
governs only what we accept from an opponent.

### Closed in `0.2.5-proposed`

11. **`result_claim` re-aligned to the simulator wire set.** After the
    interoperability specification confirmed the reference enum, `result_claim`
    returns to `capture`/`survival`/`timeout`, reversing item 8 above. It is a
    **wire** field: accepting exactly the values a conforming peer sends prevents a
    self-inflicted technical loss. The book's Tie outcome is a **scoring** result
    (Appendix F table 17), already modelled in `ScoringTable.Outcome.TIE`, so
    removing it from the wire enum loses nothing. `min_center_intensity` and
    `receive_control` stay optional (items 9-10); both agree with the spec.

The controlled file count remains **35** in this revision.

## Stable bundle location

The role-neutral, copy-into-Thief bundle is the top-level `shared_contract/`
directory. It contains specifications, schemas, fixtures, reproducible vectors, and
a read-only verifier only — no active match, no runtime identities, no Cop runtime
files, and no secrets.

## Manifest

`shared_contract/PARITY_MANIFEST.json` is excluded from its own file list. Its
separately computed exact-byte SHA-256 is:

`8f24a3b9daa05b5bc3c61b30ee98b7be6d731049ecb9345c63709e4189a7688b`

Superseded manifest hashes, which must not be used to authorize a copy of this
revision:

| Revision | Manifest SHA-256 |
|---|---|
| `0.2.0-proposed` | `2b473b5394608973dd088a239ff0fb6b5c3b247a898e12a742674efddcf09642` |
| `0.2.1-proposed` | `48664ac848f5422354919191ace0653db46697dc38a7250382d0449b540cfc9c` |
| `0.2.2-proposed` | `fb6b97ac1cc5c4f5d3a25ce6096593e7f08fb4e8fb4cb61dbc2c06946016167d` |
| `0.2.3-proposed` | `cf214a5e7562011072940e2153ece1d0032ab29eefcdfa104024a3d86502eecf` |
| `0.2.4-proposed` | `5159a9ad03d7a62922de19f0fef41f3b6999b552399e6361b504ed3b78b57851` |

## Controlled inventory (35 files, paths relative to `shared_contract/`)

| Path | SHA-256 |
|---|---|
| `CONTRACT_VERSION` | `b7f82fe0ddb67b9cb752b0c2788c3b356a544ddd0791d26cc6f9454adac34180` |
| `MATCH_CONFIGURATION.md` | `cd53e075ceb3341a2c0f811a59731cee5df125e4300cbd5100ff294f496c3ea8` |
| `PROTOCOL_PROFILE.md` | `fdbd5f85110df9b5a8f8770120d0a386007799b618e08f560179d36204ed852b` |
| `README.md` | `4b9c8a41a6d157d5d712fb92e756c9e123f3152fbf89387653578540f1664fe9` |
| `SHARED_RULES.md` | `13ce414e5264d986a2882b9ddef3d52c7f6ea707b98788664af0c889164124e0` |
| `fixtures/audit_payload.invalid.json` | `d7836f6fcc0071e8addf16f0b1700fa633bdfb6442f1d51f20bbe28ef38a8d9d` |
| `fixtures/audit_payload.valid.json` | `8736797d2cb2d312d5a52f96ccd22324eb7c099b89646d997530ce8549a92c98` |
| `fixtures/audit_record.invalid.json` | `f87b3e3a0b71de113071e5e2e4f4965acadd73f99046f2e8a46c135d7b34f965` |
| `fixtures/audit_record.valid.json` | `554b7e9790ff29dfb5b945774eb5741df2b5721fde9b5f1e5c77ab4b3b588d80` |
| `fixtures/control_message.invalid.json` | `e31e2a2653db049de8b4fa4afc5fd18b8f5ddc0986fdb468088af8f64a7834f7` |
| `fixtures/control_message.valid.json` | `3e218c045b79688892486ac9fa8f924ef3e1216b60f6fd3899b0ba8a26f6ad10` |
| `fixtures/match_config.appendix_b.json` | `2584d07627a44f7f27888c56e8c6beedc1e82532601e977774bf5858c538a711` |
| `fixtures/match_config.example.json` | `70758af55f178a049a438b81eb5f9acd389c568214cb3006358c66f8d10abd06` |
| `fixtures/negotiate.invalid.json` | `89a2056554d09f27cdb8bcfaa74ff3267ed9cfd37ff58f6e98eb45fd05ee8f9a` |
| `fixtures/negotiate.valid.json` | `757bb5b88b13895c22fbd859afea07f6438d08e13a2c976153cc615953d31a8b` |
| `fixtures/negotiation_terms.projection.json` | `bd6720bb908b3d5ee24bbeabea656fd8dda895194721a84d6a7cf1e050fd8408` |
| `fixtures/per_subgame_config.invalid.json` | `4f747aaeb24f18105434abbe9e4f5dccb1480dbecf4f1e8638f16218115f9096` |
| `fixtures/per_subgame_config.valid.json` | `abee6cde6e7cd540c4e4a2efda7cfae650427547869f8f67bf2365f9e3ecfff0` |
| `fixtures/simulator-v3.0.0-wire.golden.json` | `d7b95e4716766811fc79a5dc6bfb841e80cf1e04742094b9babbcb41f427667b` |
| `fixtures/tool_response.invalid.json` | `467483ad4afd4d5551061cd22ed3e250721f60316ffab2f1b36c77b451e78135` |
| `fixtures/tool_response.valid.json` | `12b34da73b0c67a0319e6eddbd3582af66e3b558b4d44e4a6860e0cec20d726f` |
| `fixtures/turn_message.invalid.json` | `782e1e1a88ed5f1bb08f8ed135705659b9550d4d741534f40731ce8065ee2ddc` |
| `fixtures/turn_message.valid.json` | `7116b7067c44598969e6bb4996921c5a25072c46527d86a7220755755b98e6ba` |
| `schemas/audit-payload.schema.json` | `7620b703686d75404e8a6f881ec099b5b4754e3d71da7daf056b5ca2ad79547c` |
| `schemas/audit-record.schema.json` | `3aa5bf05d2525f0f2b737b469ce7dd085b8a4226f876cddcc3be692db625a033` |
| `schemas/control-message.schema.json` | `d54f77f9e1cdc3e27c943c0869086b2988361251ea28e489bc7b603c361d4096` |
| `schemas/match-config.schema.json` | `997d3d26d3c0490e4fc5ff4dee685d6ff36b9d5aded5fa799c0845a055c41b4c` |
| `schemas/negotiate.schema.json` | `ac81f1ad3b1a41c50182ec839f775df7c70b62fc39bda3e77144257ef5a7450f` |
| `schemas/per-subgame-config.schema.json` | `99bc6e95bd77fe56453ba9c4a5cb004e10de59120aaa795186ed9f0170c52947` |
| `schemas/tool-response.schema.json` | `099cf29c4e7ff615238d87ddd76b22e35130bc8cacaa0f5a6a1e301d7a3e3309` |
| `schemas/turn-message.schema.json` | `8cc01a1e07018acdccc5e9b8e267363ef972426b3c604b74208d48b87af50ad0` |
| `vectors/config-sha256.vectors.json` | `e40490ab5f997e4f0c3469f0de31c8f7d742dc02c9b322be9fbc7f3c9886d464` |
| `vectors/move-commit.vectors.json` | `0bb194c7e8b599167a648218da7c9256dce731f68c05b238a3d6788b4ef66c68` |
| `vectors/simulator-v3.0.0-commit.golden.json` | `8667cd316cf5dff8ca0812993b168959c649736ef3ada00f68d8c777e01773bf` |
| `verify.py` | `1e6cb9521e418c8b7ff162d20e1f383af7490504f28f704492d415d48f4a84da` |

## Local validation snapshot

- `uv run ruff check .`: PASS (all checks passed)
- `uv run pytest --cov --cov-branch --cov-fail-under=85`: 480 passed, 99.24%
- `uv run python scripts/check_file_lengths.py`: PASS (38 source/script, 54 test files)
- `uv run python scripts/check_secrets.py`: PASS (201 files, 0 findings)
- `uv run python shared_contract/verify.py`: PASS, 35 controlled files
- `git diff --check`: PASS

A clean manifest proves only that the controlled bytes match the manifest. It does
not prove semantic correctness or interoperability.

## What remains for the coordinator

1. Review the `0.2.8-proposed` scope, the Option-B / simulator-v3.0.0 profile, and
   the eleven corrections above.
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
