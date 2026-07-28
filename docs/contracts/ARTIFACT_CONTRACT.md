# Artifact Identity and Series Contract

Contract version: `0.1.0-proposed`
Status: **COMMON LIFECYCLE DEFINED; COMPLETE FORMAL SCHEMAS OPEN**

## Four artifact families

A six-sub-game series produces four standardized artifact families per reporting
peer:

| Family | Cardinality | Filename |
|---|---:|---|
| Pre-game declaration | 1 per series | `declaration_<game_id>.json` |
| Agreed config | 1 per sub-game | `config_<game_id>_g<NN>.json` |
| Sealed game log | 1 per sub-game | `log_<game_id>_g<NN>.json` |
| Aggregate final result | 1 per series | `result_<game_id>.json` |

Thus “four JSON files” means four families. A complete six-game series has fourteen
physical artifacts per peer unless an accepted official schema defines shared-copy
storage differently.

## Common identity

Every artifact root must carry:

- `game_id`: the human-readable series identifier used in filenames;
- `game_uid`: a unique UUID join key for the series;
- `links`: names linking the declaration, config, log, and result families.

The same values bind the whole series. Config/log artifacts additionally carry a
one-based sub-game number from 1 through 6. The JSON `links.config` and `links.log`
values retain literal `g<NN>` logical patterns; physical artifact filenames resolve
the number as `g01` through `g06`.

Exact `game_id` characters and UUID generation remain open for M7. In particular,
the simulator's UUIDv4 upgrade-plan statement conflicts with its current
SHA-256-derived implementation and the non-v4 supplied example.

## Role schedule

For sub-games 1 through 6, a peer plays:

- its natural repository/config role on odd games 1, 3, and 5;
- the opposite role on even games 2, 4, and 6.

Roles change, but stable group identity and `game_uid` do not.

## Configuration lock

The emitted agreed-config artifact carries `config_sha256`, computed over the
complete source `config/game.json` object as defined in
`MATCH_CONFIGURATION.md`. The hash member and artifact wrapper are outside that
source object and are not part of its digest.

## Declaration and audit

Before play, Step-0 seals the host OS, CPU, RAM, GPU/VRAM, model, code/group/game
identity, and exact running Git commit. Static declaration data and per-sub-game
Step-0 evidence must refer to the same group and series.

The supplied example seals hardware and `code_version` but omits the required Git
commit and later reports `"unknown"` commits. M7 must correct that reference-example
gap; a passing simulator stub alone is insufficient evidence.

## Result agreement

Both teams must complete the mutual audit, agree on the aggregate result bytes, and
independently send their byte-identical `result_<game_id>.json` attachment to
`rmisegal+uoh26finalgame@gmail.com`. No free-text completion report substitutes for
the attachment.

The four supplied local files preserve observed profile-1.1 key sets, but their
official provenance and complete formal required/optional/type/conditional rules
remain `NEEDS_MANUAL_REVIEW`.
