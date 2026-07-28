# Option-B Contract Handoff — `0.2.0-proposed`

Status: **TECHNICALLY READY FOR COORDINATOR REVIEW — UNFROZEN — NOT COPIED, NOT FROZEN**

Branch: `agent/cop-option-b-contract-v020`
Contract version: `0.2.0-proposed`
Interoperability profile: Option B, pinned to simulator commit
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`.

This handoff supersedes the rejected `0.1.0-proposed` bundle. It is for coordinator
review only. It does **not** self-issue `ACCEPTED_FOR_PROVISIONAL_PARITY`, copy the
bundle into Thief, freeze the contract, or authorize `M2_GAMEPLAY`.

## Stable bundle location

The role-neutral, copy-into-Thief bundle is the top-level `shared_contract/`
directory. It contains specifications, schemas, fixtures, reproducible vectors, and
a read-only verifier only — no active match, no runtime identities, no Cop runtime
files, and no secrets.

## Manifest

`shared_contract/PARITY_MANIFEST.json` is excluded from its own file list. Its
separately computed exact-byte SHA-256 is:

`2b473b5394608973dd088a239ff0fb6b5c3b247a898e12a742674efddcf09642`

## Controlled inventory (32 files, paths relative to `shared_contract/`)

| Path | SHA-256 |
|---|---|
| `CONTRACT_VERSION` | `24f07c6ba8013cb37ce947d2c35d023fa11e891482c45d4b3c5a7391c7c89993` |
| `MATCH_CONFIGURATION.md` | `dd511eeb1c6e0ae0cd5d1a9dce2ec8d9a0e9c386c13e9ba05e26918538035e30` |
| `PROTOCOL_PROFILE.md` | `639411ce150bcf874568e5f3ccb5405d547d86461000ae21064cf5294d68a411` |
| `README.md` | `3b2b38bf1e1147ed4309ff297dffce65b721b2f91a7e5f34fd64b9b4fec6b84e` |
| `SHARED_RULES.md` | `6941f1b1b33fcdec7d5e3107c5787c1a9498ead79e6a4c9bc17ca598ced78135` |
| `fixtures/audit_payload.invalid.json` | `f7d71c22311509ea2bba2a490043a22fdf0e337b542b493bbc42e7d811c91a2a` |
| `fixtures/audit_payload.valid.json` | `fc5e5384bdc65d2d2163d8318e05c6ba524ea5e7c3d692765843d2958befa2d0` |
| `fixtures/audit_record.invalid.json` | `f87b3e3a0b71de113071e5e2e4f4965acadd73f99046f2e8a46c135d7b34f965` |
| `fixtures/audit_record.valid.json` | `554b7e9790ff29dfb5b945774eb5741df2b5721fde9b5f1e5c77ab4b3b588d80` |
| `fixtures/control_message.invalid.json` | `e31e2a2653db049de8b4fa4afc5fd18b8f5ddc0986fdb468088af8f64a7834f7` |
| `fixtures/control_message.valid.json` | `3e218c045b79688892486ac9fa8f924ef3e1216b60f6fd3899b0ba8a26f6ad10` |
| `fixtures/match_config.example.json` | `70758af55f178a049a438b81eb5f9acd389c568214cb3006358c66f8d10abd06` |
| `fixtures/negotiate.invalid.json` | `6247ae2cb1e469701713718d068716e4c3db19b51131661a660dca8bf00018f4` |
| `fixtures/negotiate.valid.json` | `f9ad3dcb751f30a63e34c0bf16512e9349e19c9dddbc93e2f80f5054f67569d9` |
| `fixtures/negotiation_terms.projection.json` | `76d2949129aee6344722cde4997863e89d6641ea24f110f647e3bcd2d4822949` |
| `fixtures/per_subgame_config.invalid.json` | `4f747aaeb24f18105434abbe9e4f5dccb1480dbecf4f1e8638f16218115f9096` |
| `fixtures/per_subgame_config.valid.json` | `abee6cde6e7cd540c4e4a2efda7cfae650427547869f8f67bf2365f9e3ecfff0` |
| `fixtures/tool_response.invalid.json` | `467483ad4afd4d5551061cd22ed3e250721f60316ffab2f1b36c77b451e78135` |
| `fixtures/tool_response.valid.json` | `12b34da73b0c67a0319e6eddbd3582af66e3b558b4d44e4a6860e0cec20d726f` |
| `fixtures/turn_message.invalid.json` | `a04cdb2e2dd57bb5547b105abe999f0b54da3ae1d248dc3590c6c1ace720497a` |
| `fixtures/turn_message.valid.json` | `ff7bfd08efe44907da19fb3245c3ce9533299581590cb09e62eb63d3d6302a59` |
| `schemas/audit-payload.schema.json` | `e882ec96708a7eb1829a8a14c5bef709c299bd6dffbbb2351c301ee3911ee5d4` |
| `schemas/audit-record.schema.json` | `6ed8d450ec0b0c89cbe1403aa77147fa2f05b8f159349db590549676aa51339b` |
| `schemas/control-message.schema.json` | `2eeb5191ebf8c31d438bc70c986d88fb54a90f3a5f27f61abb4222e7ae1a6da6` |
| `schemas/match-config.schema.json` | `d22c536995b57559bce2eb350cace1a6814596c7de89f2cd548795efe7028fbb` |
| `schemas/negotiate.schema.json` | `fa8b5d8c174f9643ca97d381a4648debb5aa859146ac72ccf080ce97322bdf88` |
| `schemas/per-subgame-config.schema.json` | `0884e309358a923ef8e3801676cc3e5404342c8038fdadd640f0c49d65576a0e` |
| `schemas/tool-response.schema.json` | `d4a85d45ae3726df24442b364dce60df9fa6299f78b253725c63858a73366dc9` |
| `schemas/turn-message.schema.json` | `2984e2a44afb730eb73db422cb2cc0b35ebd36a6ed31e965b61fc576b8b30585` |
| `vectors/config-sha256.vectors.json` | `e2bb860b92c08a09408f856dcdf2b9af2fef43d13ed788b71e01161794c3ddd5` |
| `vectors/move-commit.vectors.json` | `d277392033c6eb4dbaa519462435139ecd435797fa4f0527a971a524cce55985` |
| `verify.py` | `1e6cb9521e418c8b7ff162d20e1f383af7490504f28f704492d415d48f4a84da` |

## Local validation snapshot

- `uv sync --frozen`: PASS
- `uv run ruff check .`: PASS
- `uv run pytest --cov --cov-branch --cov-fail-under=85`: 241 passed, 98.25%
- `uv run python scripts/check_file_lengths.py`: PASS
- `uv run python scripts/check_secrets.py`: PASS
- `uv run python shared_contract/verify.py`: PASS, 32 controlled files
- `git diff --check`: PASS

## What remains for the coordinator

1. Review the `0.2.0-proposed` scope and the Option-B profile.
2. If accepted, authorize copying the `shared_contract/` bundle into Thief
   byte-for-byte and independent cross-bundle verification
   (`verify.py --compare-root`).
3. Only after independent parity and conformance evidence: issue
   `CONTRACT_FREEZE: GO` and, separately, `M2_GAMEPLAY: GO`.

## Open items routed to later phases

Exhaustive artifact schemas, exact `game_id`/UUID protocol, Step-0 Git/host
attestation, and six-sub-game runtime emission remain M7 work and do not expand
this bundle.
