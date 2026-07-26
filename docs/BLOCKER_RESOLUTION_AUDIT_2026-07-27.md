# M1 Blocker-Resolution Audit — 2026-07-27

## Outcome

The second owner-supplied clarification resolves the shared/private rate-limit
boundary and the `links` placeholder behavior. It also confirms core artifact and
Step-0 responsibilities. It does not make every stated identity claim mutually
consistent, and it does not turn the repository's internal parity manifest into a
lecturer requirement.

M1 is technically ready for external coordinator and Thief review. Freeze remains
NO-GO only until that cross-repository review succeeds. Artifact-detail and Step-0
runtime questions are routed to their owning later phases rather than used to start
gameplay prematurely.

## Verified resolutions

| Topic | Resolution and direct evidence |
|---|---|
| Artifact source | The owner designates `SimulatorEXM-Repo/Json-examples/` as the course example location. Exact bytes/hashes are known; an original Moodle checksum remains unavailable. |
| Core artifact contract | Book table 20 and the simulator Phase-5/4-JSON upgrade plan establish declaration/config/log/result families and their roles. Exhaustive formal schema rules remain a later artifact-validation concern. |
| `links` | All four supplied files and `report/artifact_helpers.py` retain literal `g<NN>` in `links.config` and `links.log`; physical config/log filenames resolve to `g01`…`g06`. |
| Shared rate limits | Opponent-relevant Gatekeeper values are embedded in byte-identical `config/game.json`. Simulator `ConfigManager` loads `rate_limits.json` locally beside private `game.toml`; its exact file bytes are not match terms. |
| Step-0 | Book Chapter 5 requires signed hardware/model/code/group/game data and the exact running Git commit. Simulator `REQUIRED_TERMS`/`validate_agreement` is only a fail-fast presence check for nine normalized gameplay terms. |
| OAuth files | Book Appendix A requires local `credentials.json` and generated `token.json` for that Gmail flow and requires both to be ignored. This repository already ignores both names and wildcard variants. |

## Conflicts that must not be silently normalized

### Game UUID

The simulator upgrade plan says `game_uid=uuid4`, but the current pinned
implementation derives 16 bytes from SHA-256 of canonical terms and sorted group
IDs. The supplied example UUID reports no RFC UUID version and uses the NCS-reserved
variant; it is not UUIDv4. “Initiator proposes UUIDv4” and “both peers derive the
stable UUID” are different protocols.

No UUID algorithm is frozen in M1. M7 must select one accepted protocol and vector.

### Identifier syntax

The eight-character no-space value is the Moodle team-identification code. Neither
the book rule nor the supplied artifacts prove that every runtime `group_id` must be
exactly eight characters.

`S01R02-team07-vs-team13` is explicitly presented as an example in the supplied
artifacts' `_remark`. The actual artifacts use
`segal-police-team-vs-segal-thief-team`, and current simulator code derives
`<sorted-group-a>-vs-<sorted-group-b>`. M7 must not enforce the example as a regex
without a higher-authority rule.

### Step-0 Git commit

The book requires the exact Git commit. The supplied step-0 record contains
`code_version` but no Git commit, and its final result records both commits as
`"unknown"`. A simulator stub can pass its nine-term `validate_agreement` check while
still failing this book requirement. Passing a simulator stub is therefore useful
future interoperability evidence, not an M1 freeze proof.

### “20 controlled files”

Book table 20 lists four artifact filename variables, the sample repository, and two
lecturer addresses. It does not list twenty parity-controlled repository files.
Appendix H/E is the mandatory-rules mapping, not a controlled-path manifest.

The parity manifest in this repository is a Cop-authored internal coordination
mechanism required by the controlling cross-repository audit. Its file count is
derived from policy and can change; it must never be presented as a lecturer table.

## Phase routing

- M1: exact shared `game.json`, canonical and raw-byte identity, contract bundle,
  coordinator review, and Thief parity.
- M4: Step-0/commit-reveal wire protocol and cryptographic vectors.
- M7: final artifact schemas, game ID/UUID protocol, resolved physical filenames,
  Git-commit propagation, series emission, Gmail credentials/runtime, and stub/full
  series tests.

No external simulator run was performed by this audit. It would mutate simulator
logs and test the reference implementation rather than the current behavior-free
Cop package.
