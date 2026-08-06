# Active Cop TODO

Only Cop-owned work is decomposed here. `DONE` means implemented and locally
verified; it does not imply cross-repository acceptance. `BLOCKED` names an external
evidence/review dependency; `PENDING` names a concrete owner decision. The 2026-07-28 coordinator decision authorized
contract-independent M2 domain work and an Option-B contract revision, so M2 and the
new M1.5 gate became active. M1.5, M2, and M4 are complete; M3 is complete except the
`M3-07` boundary decision; M5 is next and M6–M9 remain ordered future work until their
preceding phase is complete.

**2026-07-30 spec-coverage reconciliation.** `M3-07`, `M5-08`, `M6-07`, `M7-08`, `M7-09`,
`M7-10`, and `M9-06`…`M9-08` were added after an audit of this ledger against the book's
Appendix E/F and the course submission guidelines found mandatory requirements with no
owning task: the Orchestrator gateway (rule 3), the pre-game scent-model hash lock
(rule 23), the Quota Manager and DOS Detector gates (rules 28/29), the game-count
declaration (rules 37/38), per-game config retention (Appendix F.2), and the guidelines'
research, standards, and extensibility sections. No existing status was changed.

**2026-07-31 decomposition.** Every milestone task is now broken into executable
sub-tasks with letter suffixes (`M5-03a`, `M5-03b`, …). Parent rows keep their original
ID, status, and Definition of Done verbatim and now act as the milestone gate; a parent
may only be marked `DONE` when all of its sub-tasks are `DONE`. No existing status was
changed by the decomposition.

## Conventions

- **Priority.** `P0` blocks the milestone · `P1` core deliverable · `P2` polish.
- **Authority tags** in the Definition of Done cite the governing source, in the order
  fixed by `SOURCE_OF_TRUTH.md`: `[book §]` · `[AE-nn]` Appendix E rule · `[AF-tn]`
  Appendix F table · `[G§n]` submission guidelines · `[PRD-x]` local PRD · `[ADR-nnn]`.
- **Sub-task rows** are indented by ID suffix only; the table shape is unchanged so the
  file stays greppable by ID.
- A task whose authority is an open unknown carries the `U-nnn` marker and must not be
  implemented as binding until the coordinator rules.

## How to use this ledger

1. Find the lowest-numbered milestone that is still open and work its tasks in ID order.
   Phases are sequential by design; the book's chapter 10 warning about skipping ahead is
   the reason `M5-10` exists.
2. A sub-task is the unit of work. Complete it, run every continuous gate, then commit
   with a focused message naming the sub-task ID.
3. Never mark a parent `DONE` while any of its sub-tasks is open.
4. If a task requires a value nobody has confirmed, stop and register a `U-nnn` rather
   than choosing one silently. Silent choices are the defect this ledger exists to catch.
5. Never claim cross-repository acceptance from local evidence. Local green means local
   green.

---

## Milestone exit gates

A milestone closes only when every task under it is `DONE` **and** its exit gate is
observed running end to end, not merely written. Book chapter 10 is explicit that a
milestone is "the behaviour is observed", never "the code is written".

| Milestone | Exit gate | State |
|---|---|---|
| M0 | Authority order, provenance, conflicts, and unknowns are evidence-backed | closed |
| M1 | Superseded by the M1.5 Option-B gate | superseded |
| M1.5 | Green conformance suite and a published proposed handoff | closed locally; cross-repo acceptance open (`M1.5-13`) |
| M2 | Complete hardened domain suite: barrier-aware moves, adjacency, capture | closed |
| M3 | A full local sub-game runs to capture or survival with no transport | closed except `M3-07` |
| M4 | Independent vectors and tamper/failure tests pass | closed |
| M5 | Two independent local processes complete a resilient game | **open — the current milestone** |
| M6 | Legal deterministic behaviour under observation and fallback tests | open |
| M7 | One complete local series produces accepted audit artifacts | open |
| M8 | Remote rehearsal and evidence screenshots pass | open |
| M9 | Submission checklist and current Moodle instructions satisfied | open |

---

## Continuous gates

These run before every commit and in CI; they are not milestone-scoped.

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| G-01 | Keep `uv sync --frozen` reproducible | DONE | P0 | Clean clone installs from `uv.lock` with no network drift `[G§8.4]` |
| G-02 | Keep `ruff check .` at zero findings | DONE | P0 | Zero violations under the pinned `select` set `[G§7.1]` |
| G-03 | Keep branch coverage at or above 85% | DONE | P0 | `pytest` fails under the configured `fail_under` `[G§6.2]` |
| G-04 | Keep every source file at or under 150 lines | DONE | P0 | `scripts/check_file_lengths.py` passes for source and tests `[G§3.2]` |
| G-05 | Keep the secret scanner clean | DONE | P0 | `scripts/check_secrets.py` reports zero findings `[AE-39]` `[AE-40]` `[G§7.4]` |
| G-06 | Keep the shared-contract manifest self-consistent | DONE | P0 | `shared_contract/verify.py` matches every controlled file hash |
| G-07 | Keep the working tree whitespace-clean | DONE | P1 | `git diff --check` reports nothing |
| G-08 | Keep the prompt-engineering log current | DONE | P1 | `PROMPT_LOG.md` records each significant prompt and outcome `[G§8.3]` |
| G-09 | Keep CI running every gate on every push | DONE | P0 | `.github/workflows/ci.yml` runs G-01…G-07 |
| G-10 | Keep `docs/DOCS_COMPLETENESS.md` reconciled after each milestone | DEFERRED | P2 | Every doc listed has a current owner and status |
| G-11 | Keep `PLAN.md` milestone states consistent with this ledger | DEFERRED | P1 | A milestone cannot read `DONE` in one file and open in the other |
| G-12 | Keep `REQUIREMENTS_LEDGER.md` in step with implemented behaviour | DEFERRED | P1 | An `SR`/`OB` row marked satisfied has a test to point at |
| G-13 | Keep `UNKNOWN_REQUIREMENTS.md` in step with blocking tasks | DEFERRED | P1 | Every `U-nnn` names the tasks it blocks, and every blocked task cites its `U-nnn` |
| G-14 | Keep ADRs current when a decision changes | DEFERRED | P1 | A superseded decision is marked superseded, never silently edited |
| G-15 | Keep every commit message in Why/Changes/Tests form | DONE | P2 | Focused, single-purpose commits `[G§8.2]` |
| G-16 | Never push, merge, or open a PR without the coordinator | DONE | P0 | Repository policy; local green is not acceptance |
| G-17 | Never modify the companion repository or read-only material | DONE | P0 | Repository policy; isolation is a Zero-Trust requirement `[AE-2]` |
| G-18 | Keep the contract bundle version and manifest in lockstep | DONE | P0 | A changed controlled file forces a bump and a regenerated manifest |
| G-19 | Keep `.env-example` present with dummy values only | DONE | P0 | `[G§7.4]`; no real provider name or key |
| G-20 | Keep dependencies pinned through `uv.lock` | DONE | P0 | No unpinned or floating requirement `[G§8.4]` |

---

## M0 — Evidence and source reconciliation

*Gate: authority order, provenance, conflicts, and unknowns are evidence-backed.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M0-01 | Audit requirements, contradictions, and historical parity claims | DONE | P0 | Evidence ledger and baseline differences are recorded |
| M0-01a | Extract every Appendix F parameter with status and locator | DONE | P0 | `PARAMETERS_BASELINE.md` lists value, status, and table for each `[AF-t13..t19]` |
| M0-01b | Extract the 55 Appendix E rules with sanctions | DONE | P0 | `REQUIREMENTS_LEDGER.md` carries one row per rule `[AE-1..55]` |
| M0-01c | Record specification conflicts found across sources | DONE | P0 | `SPECIFICATION_CONFLICTS.md` names each conflict and its resolution status |
| M0-02 | Correct authority order and local JSON provenance | DONE | P0 | All affected claims use the coordinator hierarchy and `NEEDS_MANUAL_REVIEW` |
| M0-02a | Publish the seven-level source hierarchy | DONE | P0 | `SOURCE_OF_TRUTH.md` ranks book → F → E → templates → Moodle → guidelines → simulator |
| M0-02b | Pin the simulator reference commit | DONE | P0 | `SIMULATOR_BASELINE.md` records `960499fd…` as a reference, never an override `[ADR-008]` |
| M0-03 | Maintain conflicts, unknowns, and proposal boundaries | DONE | P0 | P0 uncertainties remain explicit and no simulator behavior is promoted |
| M0-03a | Maintain the open-unknown register | DONE | P0 | `UNKNOWN_REQUIREMENTS.md` carries every `U-nnn` with its blocking effect |
| M0-04 | Record the book's internal contradictions the report must disclose | DEFERRED | P1 | Book p. 5 grants freedom to resolve contradictions **if** the report states where, what, and why. One entry per contradiction actually relied on: capture-proof party (p. 38 vs p. 39), barrier adjacency wording (p. 37), step/survival boundary (`M3-07`), scent-decay arithmetic (`M6-07`), replay-hash sketch (`M8-02d`) |
| M0-04a | Record the appendix-lettering inconsistency | DEFERRED | P2 | The parameters table is called E, F, V, I, and "1" in different places; the rules table E and H |
| M0-04b | Record the board-size illustration inconsistency | DEFERRED | P2 | Binding value 7×7; illustrations use 10×10, 6×6, 5×5, and 3×3 |
| M0-04c | Record the `[Number of Agents]` name collision | DEFERRED | P2 | Table 13 means players (2); Table 18 means games in a series (6) |
| M0-04d | Record the series-of-six versus one-scoring-game tension | DEFERRED | P1 | Table 18 fixes six; rule 52 counts one. Resolved here as six sub-games inside one counted meeting |
| M0-04e | Record the missing technical-loss row in Table 17 | DEFERRED | P2 | The scoring table omits a value the config schema requires |
| M0-05 | Keep the source inventory current | DONE | P1 | Every external source has a provenance note and access date |
| M0-05a | Record which sources are authoritative and which are reference | DONE | P0 | The simulator is reference; the book is authority `[ADR-008]` |
| M0-06 | Keep the repository audit reproducible | DONE | P1 | The provenance comparison can be re-run and gives the same answer |

---

## M1 — Public contract, match configuration, parity and freeze

*Gate superseded by M1.5; rows retained so the change of approach stays visible.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M1-01 | Maintain installable behavior-free Cop package/SDK | DONE | P0 | Frozen install, version, import, CLI, and SDK smoke paths pass |
| M1-01a | Expose a version, CLI entry point, and importable SDK | DONE | P0 | `p2p-cop --version` and a bare SDK import both succeed `[G§14]` |
| M1-01b | Place every public symbol behind the SDK boundary | DONE | P0 | Adapters never import internal modules `[G§4.1]` |
| M1-02 | Define stable public league semantics | DONE | P0 | Appendix F status and ownership are separate from match values |
| M1-02a | Separate `Fixed`, `Minimum`, and `Negotiation` statuses | DONE | P0 | Each parameter carries its Appendix F status `[AF-§1]` |
| M1-03 | Define public-match/private-peer boundaries | DONE | P0 | Ports, URL storage, models, credentials, strategies, secrets, and per-turn commitment nonces stay private; the negotiation challenge is public wire data |
| M1-03a | Keep private values out of the shared JSON | DONE | P0 | Ports, model choice, credentials, and strategy class stay in the private TOML `[ADR-004]` |
| M1-03b | Distinguish the public challenge nonce from secret commit nonces | DONE | P0 | Separate domains; neither derives from the other |
| M1-04 | Model neutral participant and match binding | DONE | P0 | `agreed_between`, game/sub-game identity, and neutral identifiers validate |
| M1-04a | Canonicalise participant ordering | DONE | P0 | Ordering is stable and independent of who proposes |
| M1-05 | Validate fixed, minimum, and negotiated match values | DONE | P0 | Fixed changes and below-minimum values reject; negotiated values load from files |
| M1-05a | Reject any change to a `Fixed` value | DONE | P0 | `[AE-12]`; deviation disqualifies |
| M1-05b | Reject a `Minimum` value below its floor | DONE | P0 | Raising is legal, lowering is not `[AF-§1]` |
| M1-05c | Accept any agreed `Negotiation` value with a documented default | DONE | P1 | The Appendix F example is the default when unagreed |
| M1-06 | Isolate 1.1, 1.2, and 1.3 observations | DONE | P0 | Unsupported versions reject without translation or normalization |
| M1-06a | Refuse to normalise an unsupported schema version | DONE | P0 | No silent translation between versions `[ADR-003]` |
| M1-07 | Enforce match mismatch/private leakage failures | DONE | P0 | Participant, value, hash-shape, duplicate-key, and private-field vectors reject |
| M1-07a | Reject duplicate JSON keys | DONE | P0 | A duplicate key changes canonical bytes and must not be tolerated |
| M1-07b | Reject any private field appearing in shared config | DONE | P0 | Leakage vector per private field class |
| M1-08 | Distinguish local integrity from cross-root comparison | DONE | P0 | Checker reports local manifest result and optional exact-byte comparison separately |
| M1-09 | Add reproducible CI | DONE | P0 | Required frozen sync, lint, tests, length, secret, integrity, and diff gates run |
| M1-09a | Run every gate on every push and pull request | DONE | P0 | No gate is manual-only |
| M1-09b | Fail the build on any gate failure | DONE | P0 | No warn-and-continue path |
| M1-09c | Pin the CI Python and `uv` versions | DONE | P1 | CI reproduces the local environment `[G§8.4]` |
| M1-16 | Keep the parameters baseline reconciled with Appendix F | DONE | P0 | Every value carries its table locator and status |
| M1-16a | Flag any value the book leaves ambiguous | DONE | P0 | Ambiguity becomes a `U-nnn`, never a silent default |
| M1-17 | Keep the requirements ledger traceable | DONE | P0 | Every `SR`/`OB` row cites a source locator |
| M1-17a | Distinguish confirmed from proposed rows | DONE | P0 | A proposal never reads as confirmed |
| M1-18 | Keep the verification policy explicit | DONE | P1 | What counts as evidence, and what does not, is written down |
| M1-18a | Require the pinned commit for any simulator observation | DONE | P0 | An unpinned observation is not evidence |
| M1-19 | Keep team identity confirmed and current | DONE | P0 | Team name, group id, member names, and the eight-character code recorded in `TEAM_INFO.md` from verified team input dated 2026-07-28; `U-016` closed 2026-07-31 |
| M1-19a | Record the confirmed eight-character team code | DONE | P0 | `sharNamr`, exactly eight characters, no spaces `[AE-45]` |
| M1-19b | Record both lecturer addresses | DONE | P0 | `rmisegal@gmail.com` and `rmisegal+uoh26finalgame@gmail.com` are recorded and correct |
| M1-19c | Correct the address provenance citation | DONE | P1 | Both addresses now cite lecturer answer `AF-020`. `TEAM_INFO.md` records why the book's Appendix F table 20 spelling (`rimesegal`) is treated as a source typo |
| M1-20 | Maintain the submission checklist against the book's Appendix C | DONE | P1 | Every checklist row maps to a task in this ledger |
| M1-10 | Classify the four designated JSON course examples without overclaiming provenance | DONE | P0 | Owner designation, exact hashes, observed key sets, and the remaining narrow provenance caveat are recorded |
| M1-11 | Specify participant order and match canonicalization | DONE | P0 | Ordered IDs, complete-object scope, canonical UTF-8 bytes, and external hash claim are tested |
| M1-12 | Reconcile config split, identity fields, and role schedule | DONE | P0 | Shared authority, artifact lifecycle, and identities are documented; the unresolved role schedule is excluded and tracked as `U-025` |
| M1-13 | Incorporate accepted M1 answers and vectors | DONE | P0 | Candidate hash `adac9efe…82db` and rejection vectors pass |
| M1-14 | Produce candidate handoff | DONE | P0 | Controlled paths/hashes, manifest self-hash, gates, and blockers are recorded |
| M1-15 | Promote contract version after acceptance evidence | SUPERSEDED | P0 | `0.1.0-proposed` rejected; superseded by the M1.5 Option-B `0.2.0-proposed` gate |

---

## M1.5 — Option-B contract repair and conformance gate

*Gate: role-neutral bundle, explicit per-run config, separated hash domains, neutral conformance.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M1.5-01 | Record the Option-B interoperability decision | DONE | P0 | Ledger, conflicts, ADR-001/006, TODO, and PLAN record the accepted profile and pinned commit |
| M1.5-02 | Harden barrier-aware M2 semantics | DONE | P1 | Police-adjacency placement, impassability, barrier-aware moves, and start-coordinate validation pass tests |
| M1.5-03 | Separate stable contract from per-match configuration | DONE | P0 | Stable fixtures are never active defaults; every match and local exact rate-limit mirror is supplied by explicit path |
| M1.5-04 | Define Option-B protocol and message schemas | DONE | P0 | negotiate/turn/audit/control/tool-response/config schemas and pos/neg fixtures validate |
| M1.5-04a | Publish the negotiate schema and fixtures | DONE | P0 | Valid and invalid fixtures both asserted |
| M1.5-04b | Publish the turn-message schema and fixtures | DONE | P0 | Valid and invalid fixtures both asserted |
| M1.5-04c | Publish the audit payload and record schemas | DONE | P0 | Valid and invalid fixtures both asserted |
| M1.5-04d | Publish the control-message and tool-response schemas | DONE | P0 | Valid and invalid fixtures both asserted |
| M1.5-04e | Publish the match-config and per-subgame-config schemas | DONE | P0 | Appendix B conformance fixture accepted |
| M1.5-05 | Separate hash domains and add canonicalization vectors | DONE | P0 | Per-turn commitment, `config_sha256`, and `config_file_sha256` are distinct and vector-tested |
| M1.5-05a | Publish `config-sha256` vectors | DONE | P0 | `shared_contract/vectors/config-sha256.vectors.json` |
| M1.5-05b | Publish move-commit vectors | DONE | P0 | `shared_contract/vectors/move-commit.vectors.json` |
| M1.5-05c | Publish the simulator-v3.0.0 golden commit vector | DONE | P0 | Reproduced by reimplementation, never by copying |
| M1.5-06 | Prove unknown-opponent conformance and LF safety | DONE | P0 | Neutral stub proves tool/argument names and rejections; controlled files are LF; verifier is read-only |
| M1.5-06a | Assert exact tool and argument names | DONE | P0 | A renamed tool or argument fails the suite |
| M1.5-06b | Enforce LF line endings on controlled files | DONE | P0 | `.gitattributes` plus a byte check; CRLF would change every hash |
| M1.5-06c | Keep the verifier read-only | DONE | P1 | `verify.py` never writes to the bundle |
| M1.5-07 | Publish the `0.2.0-proposed` handoff | DONE | P0 | Handoff records controlled paths, per-file hashes, manifest hash, gates, and blockers |
| M1.5-08 | Correct contract semantics and republish as `0.2.1-proposed` | DONE | P0 | Barrier rule allows the placing peer's own cell; the unauthenticated role-alternation schedule is removed from the bundle and recorded as `U-025`/`OB-005`; version, manifest, and handoff are regenerated |
| M1.5-09 | Close the fixable semantic blockers and republish as `0.2.2-proposed` | DONE | P0 | Root `version`/`extensions` are optional and an Appendix B conformance fixture proves the official structure is accepted; cross-field start validation runs after schema validation and `axis_start_index` is bounded; 33 controlled files, manifest and handoff regenerated |
| M1.5-10 | Reconcile the remaining semantic decisions and publish `0.2.3-proposed` | DONE | P0 | Explicit match and exact local-mirror paths have no fallback; `negotiate.nonce` is public and distinct from secret per-turn commitment nonces; controlled bundle and handoff are regenerated |
| M1.5-11 | Republish `0.2.4-proposed` reconciling the simulator profile with Appendix F | DONE | P0 | Wire schemas match the pinned `simulator-v3.0.0` profile without contradicting the book's fixed values |
| M1.5-12 | Republish `0.2.5-proposed` aligning `result_claim` to the simulator wire set | DONE | P0 | Wire carries `capture`/`survival`/`timeout`; the book's Tie outcome stays in the scoring layer, never on the wire `[AF-t17]` |
| M1.5-13 | Obtain cross-repository acceptance of the current bundle | BLOCKED | P0 | The companion peer records acceptance of an exact revision. Blocked on the coordinator; the bundle remains `UNFROZEN` and no freeze may be claimed without it |
| M1.5-14 | Keep the manifest regenerated on every bundle change | DONE | P0 | `scripts/generate_shared_manifest.py` runs whenever a controlled file changes |
| M1.5-14a | Refuse two byte-sets under one version label | DONE | P0 | A changed file forces a version bump |
| M1.5-14b | Republish the handoff alongside each bump | DONE | P0 | `OPTION_B_HANDOFF.md` records the per-revision change log |
| M1.5-15 | Keep the bundle role-neutral | DONE | P0 | Nothing in the shared bundle assumes which peer is Cop |
| M1.5-15a | Exclude the unauthenticated role schedule | DONE | P0 | Recorded as `U-025`/`OB-005` rather than asserted |
| M1.5-16 | Keep every controlled path explicitly enumerated | DONE | P0 | No glob; a new file must be added deliberately |
| M1.5-17 | Keep the bundle importable by a peer written in another language | DONE | P1 | JSON Schema and vectors only; no Python-specific artifact is normative |
| M1.5-18 | Record the Appendix B conformance evidence | DONE | P0 | The official structure is accepted, not merely the local shape |
| M1.5-19 | Separate stable contract files from per-match inputs | DONE | P0 | A fixture is never silently used as a live default |
| M1.5-19a | Require an explicit path for every per-run input | DONE | P0 | No fallback path exists to mask a missing file |

---

## M2 — Core domain rules

*Gate: immutable board/actions, legal moves, barriers, and capture through the SDK.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M2-01 | Implement immutable coordinate and action types | DONE | P1 | SDK-visible unit tests prove immutability and vocabulary |
| M2-01a | Model `Coordinate` as a frozen value type | DONE | P1 | Hashable, equality-by-value, no in-place mutation |
| M2-01b | Model the five-member action vocabulary | DONE | P1 | `N`/`S`/`E`/`W`/`STAY` only; no diagonal member exists `[AE-13]` `[AE-14]` `[AF-t15]` |
| M2-02 | Implement board geometry and boundary validation | DONE | P1 | Negotiated board/origin semantics pass boundary tests; start-coordinate validation added in M1.5-02 |
| M2-02a | Read `grid_size`, origin corner, and start index from config | DONE | P1 | No hard-coded 7; the value comes from the negotiated match `[AF-t13]` |
| M2-02b | Reject off-board coordinates on every boundary | DONE | P1 | All four edges and both corners covered by tests |
| M2-03 | Implement legal orthogonal movement and `STAY` | DONE | P1 | Deterministic transitions; barrier-aware legality added in M1.5-02 |
| M2-03a | Reject diagonal movement structurally | DONE | P0 | A diagonal cannot be expressed, not merely rejected `[AE-14]` |
| M2-04 | Implement barrier inventory, placement, and disclosure rules | DONE | P1 | Quota, board legality, and disclosed events pass; police-adjacency and impassability added in M1.5-02 |
| M2-04a | Enforce the `max_barriers` quota | DONE | P1 | Placement beyond quota rejects `[AF-t15]` |
| M2-04b | Make a placed barrier permanently impassable | DONE | P1 | The cell stays blocked for the remainder of the sub-game |
| M2-04c | Emit a truthful disclosure event per placement | DONE | P0 | Every placement is disclosed with its exact cell; concealment is impossible `[AE-15]` `[AE-16]` |
| M2-05 | Implement capture conditions | DONE | P1 | Cop-on-thief, current-cell barrier, and trapped-Thief (STAY does not save) rules pass tests |
| M2-05a | Capture by co-location with a declared claim | DONE | P1 | `[AE-21]` requires the claim be provable at audit |
| M2-05b | Capture by barrier on the Thief's current cell | DONE | P1 | `[AE-46]` |
| M2-05c | Capture by no-legal-move (trapped) | DONE | P1 | `[AE-47]`; `STAY` does not rescue a trapped Thief |
| M2-05d | Define precedence when two capture conditions coincide | DONE | P1 | Deterministic single reason is reported |
| M2-06 | Expose the domain layer through the SDK | DONE | P1 | Adapters reach board, movement, barriers, and capture without internal imports `[G§4.1]` |
| M2-07 | Cover the domain layer with boundary tests | DONE | P1 | Every edge, corner, quota limit, and illegal input asserted |
| M2-07a | Test movement against all four board edges | DONE | P1 | Off-board attempts reject |
| M2-07b | Test movement into and around barriers | DONE | P1 | A blocked cell is never entered |
| M2-07c | Test barrier placement at and beyond quota | DONE | P1 | The boundary case is asserted, not assumed |
| M2-07d | Test capture in each of the three ways | DONE | P1 | Co-location, barrier-on-cell, trapped |
| M2-07e | Test malformed and hostile inputs reject | DONE | P1 | Non-integer, negative, and oversized coordinates |
| M2-08 | Document the domain vocabulary | DONE | P2 | Terms match the book's rules, not invented synonyms |
| M2-09 | Prove the domain layer is contract-independent | DONE | P0 | It imports no shared-contract byte and no transport module |
| M2-10 | Keep every domain value configurable | DONE | P0 | Board size, quota, and thresholds all read from config `[G§7.2]` |

---

## M3 — Local state, scoring and deterministic baseline

*Gate: a full local sub-game runs to capture or survival with no transport.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M3-01 | Implement Cop-local immutable state | DONE | P1 | `CopState` has exactly board/position/barriers/turn; tests whitelist those fields and prove changing only `thief_start` cannot change the state. Transitions are primitives that assert no turn ordering |
| M3-01a | Prove the state type cannot hold opponent truth | DONE | P0 | A field whitelist test fails if any opponent-position field is added `[AE-2]` `[AE-8]` |
| M3-02 | Implement deterministic state history | DONE | P1 | `CopHistory` is append-only; identical opening state and action sequence produce an equal history and identical positions; illegal actions record nothing |
| M3-03 | Implement fixed scoring and technical loss | DONE | P1 | Appendix F table 17 awards and the Appendix E zero-point sanction pass table-driven tests; values are read from the negotiated config, not hard-coded. Technical loss scores zero for **both** peers (`U-026` closed 2026-07-31) |
| M3-03a | Encode capture 20/5 and survival 5/10 | DONE | P1 | Values read from config, asserted against `[AF-t17]` |
| M3-03b | Encode the tie award at the series level | DONE | P1 | Tie is a cumulative-series outcome, never a single sub-game result `[AF-t17]` |
| M3-03c | Encode the technical-loss zero | DONE | P1 | `[AE-19]` `[AE-48]`; the award is **symmetric** — chapter 3 table 2 prints the row as `0 \| 0` and rule 48 writes it "technical loss 0/0". `Outcome.TECHNICAL_LOSS` returns `(0, 0)` from `award()`. `U-026` closed 2026-07-31 |
| M3-04 | Build single-process rules harness | DONE | P1 | `run_sub_game` referees a full local sub-game to capture or survival with no transport; no opponent behaviour ships in source; the Cop policy receives no referee-only Thief cell; actor and capture-check ordering is an injected event schedule whose default is explicitly `PROJECT-PROPOSED` |
| M3-05 | Implement SDK-reachable deterministic pursuit baseline (movement) | DONE | P1 | Policy emits only legal movement actions; barrier-aware BFS distance, fixed-order tie-breaking, SDK-reachable, contract-independent. See [PURSUIT_BASELINE.md](PURSUIT_BASELINE.md) |
| M3-06 | Decide and implement baseline barrier placement | DONE | P1 | SDK-reachable `choose_turn_intent` returns one move or one barrier, exclusivity encoded in the return type; the local harness executes either intent; policy captures by moving before spending quota, places a trapping barrier, and never wastes quota on an already-trapped Thief |
| M3-07 | Resolve the step-limit / survival-threshold boundary | DONE | P0 | Closed 2026-07-31 from the book, without needing an owner ruling: chapter 3 table 2 defines survival as surviving "the limit of valid moves", and table 15 makes the limit equal the threshold, so the horizon is **inclusive**. `run_sub_game` already behaved this way; `test_the_survival_horizon_is_inclusive_at_the_threshold` and `test_a_capture_on_the_final_turn_still_outranks_survival` now pin both sides. `U-027` closed, `C-024` `RESOLVED` |
| M3-07a | Register the boundary as a numbered unknown | DONE | P0 | `U-027` registered in `UNKNOWN_REQUIREMENTS.md` naming both readings; conflict `C-024` records the source defect |
| M3-07b | Add a boundary test pinning the chosen reading | PENDING | P0 | Turn `threshold-1`, `threshold`, and `threshold+1` are each asserted |
| M3-07c | Disclose the choice in the academic report | PENDING | P1 | Book p. 5 requires stating where the contradiction is, what was chosen, and why |
| M3-08 | Expose state, history, and policy through the SDK | DONE | P1 | Adapters never import `orchestration` or `strategy` internals `[G§4.1]` |
| M3-09 | Prove the pursuit baseline is deterministic | DONE | P1 | Identical inputs yield an identical action every run |
| M3-09a | Fix the tie-break order explicitly | DONE | P1 | No reliance on set or dict iteration order |
| M3-09b | Compute distance barrier-aware, not straight-line | DONE | P1 | A wall does not look like a shortcut |
| M3-10 | Prove the barrier policy never wastes quota | DONE | P1 | It captures by moving before spending, and never blocks an already-trapped Thief |
| M3-10a | Prefer a capturing move over a barrier | DONE | P1 | Spending quota when a capture exists is a waste |
| M3-10b | Refuse to place a barrier that traps the Cop itself | DONE | P1 | Self-entrapment is a real failure mode `[book §5]` |
| M3-11 | Cover the harness with turn-order tests | DONE | P1 | The injected event schedule is exercised in more than one order |
| M3-11a | Prove the schedule is genuinely injectable | DONE | P0 | An alternative ordering runs without touching the rules |
| M3-11b | Prove the Cop policy never receives the referee's Thief cell | DONE | P0 | Signature and call-site test `[AE-8]` |
| M3-12 | Prove scoring reads config rather than constants | DONE | P0 | Changing the config changes the award; no literal 20 or 10 in the policy path |
| M3-13 | Document the local-state and scoring model | DONE | P2 | `PURSUIT_BASELINE.md` and the ledger describe the built behaviour |

---

## M4 — Protocol, canonicalization and commit-reveal

*Gate: independent vectors and tamper/failure tests pass.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M4-01 | Finalize public message/envelope contract | DONE | P0 | Accepted ADR-001/002 schemas and error semantics exist |
| M4-02 | Finalize canonical JSON and commitment-nonce vectors | DONE | P0 | Independent implementations reproduce exact hashes |
| M4-02a | Pin sorted-key, compact-separator, UTF-8 canonicalization | DONE | P0 | Golden vectors cover nesting, non-ASCII, escapes, and non-BMP `[ADR-006]` |
| M4-02b | Separate the three hash domains | DONE | P0 | Per-turn commitment, `config_sha256`, and `config_file_sha256` cannot collide |
| M4-03 | Implement commit, acknowledge, reveal, and final audit | DONE | P0 | Valid state sequence round-trips through SDK with fresh commitment nonces that never reuse or derive from the public challenge |
| M4-03a | Generate nonces with `secrets`, never `random` | DONE | P0 | `[book §8]`; 16-byte hex, fresh per commit |
| M4-03b | Keep the nonce secret until the final audit | DONE | P0 | Reveal carries move and hint only `[AE-18]` |
| M4-04 | Reject illegal transitions, replay, and idempotency conflicts | DONE | P0 | Failure vectors terminate deterministically |
| M4-04a | Enforce the six-state phase table | DONE | P0 | Every transition absent from the table raises `[AE-4]` `[AE-5]` |
| M4-04b | Reject replayed and conflicting message identifiers | DONE | P0 | `TurnInbox` rejects duplicates deterministically `[ADR-002]` |
| M4-05 | Implement tamper and technical-loss audit outcomes | DONE | P0 | Byte, field, and commitment-nonce mutations are detected |
| M4-05a | Recompute every commitment at audit and compare | DONE | P0 | Any mismatch yields a technical loss with no appeal path `[AE-19]` |
| M4-06 | Implement Step-0 code and host attestation | DONE | P0 | Both peers seal hardware/model/group/game data and the exact running Git commit before moves |
| M4-06a | Seal OS, CPU, RAM, and GPU/VRAM facts | DONE | P0 | `[AE-24]`; forging or omitting forfeits the computational bonus |
| M4-06b | Seal the exact running Git commit hash | DONE | P0 | `[AE-53]`; the same value later populates `github_commit` |
| M4-06c | Seal the agreed LLM token budget | DONE | P1 | `[AE-54]`; the sealed figure is the one reported |
| M4-06d | Prove Step-0 completes before the first move | DONE | P0 | An ordering test rejects a move taken before attestation |
| M4-07 | Expose the protocol layer through the SDK | DONE | P1 | `CopSDK` reaches commit, reveal, audit, and attestation `[G§4.1]` |
| M4-08 | Cover commit-reveal with adversarial vectors | DONE | P0 | Every tampering class is detected, not merely most |
| M4-08a | Detect a mutated move at audit | DONE | P0 | Recomputed hash diverges |
| M4-08b | Detect a mutated intent flag | DONE | P0 | The bluff flag is inside the seal `[book §8]` |
| M4-08c | Detect a mutated or substituted nonce | DONE | P0 | Nonce is part of the hashed payload |
| M4-08d | Detect a single-byte mutation anywhere in the record | DONE | P0 | SHA-256 is bit-sensitive; the test proves it end to end |
| M4-08e | Detect a reordered step sequence | DONE | P0 | Step index is bound into the record |
| M4-09 | Prove nonce generation quality | DONE | P0 | Fresh per commit, cryptographically sourced, never reused |
| M4-09a | Prove two identical moves produce different commitments | DONE | P0 | The dictionary-attack defence, demonstrated `[AE-18]` |
| M4-09b | Prove no nonce derives from the public challenge | DONE | P0 | Separate domains, separate entropy |
| M4-10 | Prove canonicalization is byte-stable across platforms | DONE | P0 | LF endings, sorted keys, and fixed separators give identical bytes |
| M4-10a | Prove CRLF cannot enter a controlled file | DONE | P0 | `.gitattributes` plus a byte check; CRLF would break every hash |
| M4-10b | Prove non-ASCII content hashes identically | DONE | P0 | Encoding is pinned, not platform-dependent |
| M4-11 | Compare digests in constant time | DONE | P1 | `secrets.compare_digest`, never `==` `[book §8]` |
| M4-12 | Document the protocol layer | DONE | P2 | `PRD_commit_reveal.md` and `ADR-006` match the built construction |
| M4-13 | Prove the protocol layer imports no transport | DONE | P0 | Guard test; the protocol must work over any carrier |

---

## M5 — FastMCP runtime and resilience

*Gate: two independent local processes complete a resilient game.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M5-01 | Implement transport-neutral peer interface | DONE | P1 | `peer.PeerTransport` (outbound Port) and `peer.InboundPeer` (inbound handler) route the four Option-B tools through the protocol/SDK layers with no FastMCP import; a guard test proves the transport-neutral core imports no FastMCP |
| M5-02 | Implement FastMCP server adapter | DONE | P1 | `adapters.build_server` exposes the four Option-B tools as enqueue-and-ack mailboxes (matching the reference wire behaviour); `adapters.drain` validates each queued message through `InboundPeer`, so a rejection is a game outcome, not a transport error. ADR-002 amended accordingly |
| M5-03 | Implement FastMCP client connector | DONE | P1 | `adapters.FastMCPClient` implements `peer.PeerTransport` and round-trips against an in-memory `build_server`; 10 tests in `tests/integration/test_fastmcp_client.py` |
| M5-03a | Wrap `fastmcp.Client(opponent_url)` in `adapters/fastmcp_client.py` | DONE | P1 | The only outbound FastMCP import; implements `peer.PeerTransport` (verified structurally via `runtime_checkable`) |
| M5-03b | Shape tool arguments per the wire profile | DONE | P0 | Keywords come from `peer.TOOL_ARGUMENTS`, so inbound and outbound cannot drift; a test asserts each of the four messages lands in its own inbox |
| M5-03c | Return `.data` and map transport faults | DONE | P1 | Two disjoint types: `TransportError` (unreachable/timeout/malformed) and `PeerRejectionError` (reached but declined). A test asserts neither subclasses the other, so `except TransportError` cannot swallow a lost game as a retry |
| M5-03d | Drive an in-memory loopback against `build_server` | DONE | P1 | Client → server → `drain` → SDK validation, no external process |
| M5-03e | Prove accepted calls against the neutral stub | DONE | P0 | Parent DoD. `tests/conformance/neutral_stub_server.py` exposes the neutral stub over a real FastMCP wire and `test_neutral_stub_wire.py` drives `FastMCPClient` against it: the advertised tool and argument names are read back from the server itself and asserted equal to the stub's independently written `TOOLS`; our `build_offer` signature is reproduced by the stub's own reimplemented hashing; a sealed turn, a three-record audit, and a control message all cross and are accepted; and tamper/replay cases prove the stub is really checking. This is the half the in-memory loopback could not give, because there both sides read `peer.TOOL_ARGUMENTS` and a wrong name would agree with itself |
| M5-03f | Read the opponent URL from private configuration only | DONE | P0 | `shared/private_config.py` reads `[network].opponent_url` from one explicit private TOML path and is the only door to an opponent address; `assert_no_network_address` is the lock on the other door, refusing a shared match object that carries an address either by member **name** (`opponent_url`, `port`, `host`, `mcp_servers`, …) or by **value** (any URL scheme), since either check alone is evadable. The controlled `match_config.example.json` is asserted clean `[ADR-004]`. **Reference behaviour confirmed 2026-07-31** before implementing: a peer reads `config/police/game.toml` or `config/thief/game.toml` (separate directories per role) and takes the address from `[network].opponent_url`; asked directly whether the shared negotiated JSON ever carries a URL, port, host, or any network address, the answer was **no** — local settings must not "leak into the agreement". `config/game.toml.example` was realigned from an invented `[local]` section to the `[network]` skeleton the book publishes on page 131, plus the four extra timing keys the shipped reference carries |
| M5-03g | Fail cleanly on an unreachable opponent URL | DONE | P1 | `http://127.0.0.1:1/mcp` raises `TransportError`, not a crash |
| M5-03h | Fail cleanly on a malformed opponent response | DONE | P1 | A tool returning a non-object raises `TransportError` deterministically. The client is **liberal** about the ack shape — `{"ok": true}`, `{"status": "ok"}`, `{"status": "delivered"}` all count as acknowledgements — because the profile never fixed the opponent's shape and the reference's exact dict is unestablished. Only an explicit `ok: false` / failing `status` / non-empty `error` is a `PeerRejectionError`. The first implementation demanded our own `{"ok": true}`, which would have read every successful delivery from a simulator-built classmate as a refusal |
| M5-03l | Record that the server's always-ack diverges from the reference | DONE | P1 | The reference validates structurally **inside** the tool and raises, so a malformed message reaches its caller as an MCP error; this repository acks everything and validates on drain. Kept deliberately: a tampered audit is structurally well-formed but must be scored as a technical loss `[AE-19]`, and raising invites the opponent to retry a decided loss as a transport fault. `fastmcp_server.py` previously claimed the always-ack behaviour *matched* the reference; corrected 2026-07-31 |
| M5-03i | Keep the client stateless between calls | DONE | P1 | `__slots__` makes hidden per-turn state impossible rather than merely absent; each call opens and closes its own session |
| M5-03j | Add a guard test that only `adapters/` imports fastmcp | DONE | P0 | Walks every module under `src/` and asserts no non-`adapters` file imports fastmcp |
| M5-03k | Document the client contract in `PRD_p2p_mcp.md` | DONE | P2 | Call shapes and the two-way fault mapping recorded |
| M5-03m | Judge an opponent's acknowledgement in one place only | DONE | P0 | Found while building `M5-03e`. `M5-03h` made the *client* liberal about the opponent's ack shape, but `TurnLedger.acknowledge` still demanded this peer's own `{"ok": true}` — so a turn delivered successfully to a peer answering `{"status": "ok"}` passed the client and then failed the ledger, aborting every turn against a simulator-built classmate. The same bug in a second place. `signals_refusal`/`is_acknowledgement` now live in the transport-neutral `protocol/messages.py` and both the outbound adapter and the ledger call them, so the two halves cannot drift again; `is_ok_response` is kept but documented as an assertion about what **we** send, never about what an opponent sent back |
| M5-04 | Implement negotiation and mismatch refusal | DONE | P0 | `protocol/negotiation.py`: offer construction, signature verification, Appendix F enforcement, and participant checks, all refusing with the offending term named. Wiring it into the live `InboundPeer.negotiate` handler (which still only schema-checks) is `M5-11` turn-loop work. Unknown opponent acceptance works both directions. **Reference behaviour confirmed 2026-07-31** before implementing: the signature covers the shared terms with a 16-byte nonce concatenated outside behind `\|`; `config_sha256` hashes the **whole** terms object, not a subset; the negotiate message carries **no role** and no `sub_game_number`, because roles alternate across sub-games; a mismatch refuses to play and names the offending term. Critically, `game_id`/`game_uid` are **NOT** members of the signed terms — they are derived as a pure function of shared inputs and appear only as top-level artifact keys, so adding them to the signed set would break every cross-peer signature check |
| M5-04a | Build and send a match offer | DONE | P0 | `protocol.build_offer` returns terms, the **public** challenge nonce, a signature over the terms, and role-free identity. A test asserts no `role` or `sub_game_number` appears anywhere in the message, since roles alternate across sub-games |
| M5-04b | Compare `config_sha256` byte-for-byte before play | DONE | P0 | `verify_offer` refuses on any differing term and **names** it, which rule 11 requires — a bare refusal teaches the opponent nothing. A test pins that `config_sha256` covers the **whole** game object, never the terms projection, against the controlled fixture's recorded digest `[AE-11]` |
| M5-04c | Validate participant identity and ordering | DONE | P0 | `validate_participants` requires exactly two distinct non-empty names and that the offering group is one of them. Ordering is already fixed by `agreed_between` living inside the hashed object |
| M5-04d | Refuse below-minimum and altered fixed values | DONE | P0 | `check_appendix_f` treats `smell_grid_size`, `decay_per_step`, `emit_intensity`, `num_games` as `Fixed` (exact match) and `board_size`, `max_steps`, `barriers_max` as `Minimum` (raising allowed, lowering refused) `[AE-12]` `[AF-§1]` |
| M5-04e | Prove propose and accept directions both pass | DONE | P0 | Offers built under either group identity verify against the same expected terms; no profile file is edited in either direction |
| M5-04f | Pin the terms projection to the controlled fixture | DONE | P0 | `terms_from_config` is asserted equal to `negotiation_terms.projection.json`, so the mapping is checked against the contract rather than against itself. The fixture also proves `game_id`/`game_uid` are **not** signed terms — a test guards against adding them, which would refuse every classmate's match |
| M5-04g | Settle whether `min_center_intensity` is a required shared term `U-028` | DONE | P0 | **Settled 2026-08-01 — no coordinator decision needed after all.** The second notebook holds the **book PDF itself** plus the lecturer's four artifact templates, and it answered both halves outright: Appendix F table 16 has exactly three rows, all `Fixed` (centre intensity `0.9`, decay `0.10`, field `5x5`) with **no** minimum or floor row, and the lecturer's own `agreed-config` template carries exactly those same three keys. This repository's optional treatment was right and `match_config.example.json` already matched the template, so **the controlled bundle needed no change**; a test now pins the scent block against the template. The companion peer, which required the key and so would have refused the lecturer's own template, was corrected the same day. Original (now superseded) reasoning below | **Coordinator decision, raised 2026-07-31 while building `M5-03e`.** Appendix F table 16 defines no minimum-centre floor, so this repository treats the term as optional: emitted only when the match config carries it, tolerated, never required. The reference disagrees in a way that bites. Its `terms_from_config` is a standardizing transformer that **always** writes the key (`None` when absent), the key is in its `REQUIRED_TERMS`, and a `None` value aborts at startup with `Missing required agreed game term(s): …`; its shipped police and thief configs both carry `pheromone_min_center_intensity`. So `match_config.example.json`, which has no such key, would stop a simulator-built classmate from starting, and our 13-key projection would not equal their 14-key one. The companion peer already treats the term as required, so the two repositories disagree with each other. Resolving it edits the controlled bundle and the pinned projection fixture — a contract revision, hence not this agent's call. The exact numeric value the reference uses was **not** established |
| M5-04h | Enforce the book's mandated Step-0/negotiation content and the `config_sha256` lock `U-029` | DONE | P0 | **`U-029` now resolved (2026-08-01): tolerate omission, verify presence.** The enforcement question is answered without a schema change or an interop-losing refusal. `verify_offer` gained an optional `expected_config_sha256`: an offer that **omits** the lock still verifies (a simulator-built peer keeps it in artifacts, not on the wire — refusing would forfeit the match), but an offer that **carries** a lock which does not match ours is a config mismatch that rule 11 requires refusing. So the fields stay optional in the schema (no classmate is refused for omitting metadata), while a *present-and-wrong* lock is caught. Split `verify_offer` into `protocol/offer_review.py` to keep `negotiation.py` within length. 4 new tests in `test_negotiation_identity.py`. Original "populate ours" note below | **Closed under the 2026-08-01 "populate ours, tolerate theirs" decision** (`C-031`, Amr-confirmed). The split is the whole point: **populating our own offer is contract-independent** (the schema already defines every identity member and is `additionalProperties: true`, so `config_sha256` is already tolerated), while **requiring them of an opponent** would refuse a simulator-built peer that keeps these values in artifacts, not on the wire — a contract change reserved for the coordinator. Built: `protocol/identity.py` (`build_identity` assembles the mandated content from **injected** sources, `require_complete_identity` refuses to ship an incomplete offer); `build_offer` now enforces our identity is complete and attaches `config_sha256` over the **whole** game object (`shared_config_sha256`). `verify_offer` is unchanged — an opponent that omits them still verifies. 12 tests across `test_identity.py`/`test_negotiation_identity.py`; the three stub `IDENTITY` fixtures were completed (the gap this row named). No `shared_contract/` change; contract stays `0.2.5-proposed`. **Still the coordinator's call (`U-029`):** whether to make the fields `required` in `negotiate.schema.json` and refuse an opponent that omits them |
| M5-05 | Implement deadlines, retry, idempotency, and backpressure | DONE | P0 | Injected failures cannot hang the peer. All four children (05a–05d) are DONE, and the parent DoD 05e is now proven: see the consolidated adversarial suite `tests/unit/test_adversarial_peer.py` (M5-15) plus the per-mechanism tests below |
| M5-05a | Attach a timestamp and expiry to every request | DONE | P0 | `services/deadlines.Deadline` carries `started` and `expires`; the boundary itself counts as expired. Book §8.4.1 boxed note is the spec — *"Missing a Deadline is a Failure, Not Patience"* — and its two permitted outcomes are retry, or declare a technical loss and clear the queue cleanly. Time is **injected**, so a timeout is proven by passing a number rather than sleeping `[book §8.4.1]` |
| M5-05b | Implement bounded retry with backoff | DONE | P0 | `services/deadlines.attempt` gives each try its own expiry and stops at `max_retries`, raising `DeadlineError` so the caller can declare a technical loss. **Key names confirmed against the reference 2026-08-01** — `network_and_league.response_timeout_sec` (30), `rate_limiter_gatekeeper.retry_backoff_sec` (5), `.max_retries` (3), `network_and_league.watchdog_timeout_sec` (60) — all in the **shared, signed** match object, so neither peer can give itself a longer rope. A slow attempt that overruns its own expiry is **not** retried; the budget does not rescue it. Appendix F table 19 marks the first three `Minimum` and the watchdog `Negotiation` `[AF-t19]` |
| M5-05c | Enforce idempotency keys across retries | DONE | P0 | Already satisfied by `protocol/receive.TurnInbox` (`M4-04`): a redelivered `(sender, step, commit)` returns `Intake.fresh=False` so the effect applies once, a re-sent `(sender, step)` with a **different** commit raises `ConflictError`, and a step that fails to advance raises `ReplayError`. Verified during the 2026-08-01 audit rather than rebuilt — the idempotency key is the `(sender, step)` pair and the guard predates this milestone |
| M5-05d | Enforce the queue depth and backpressure signal | DONE | P1 | `services/gatekeeper.py`. Guidelines §5 settles the design in one line — **"Overflow is queued, not rejected"** — so a busy gate returns `False` (queued) rather than raising, and `queue_status()` reports depth, capacity, in-flight and totals as `get_queue_status` requires. The **only** failure is a genuinely full queue, and it raises rather than discarding, so work is never silently lost. Limits are Appendix F table 19 `Minimum` values from the signed match object: `requests_per_minute` 30, `concurrent_requests` 2, `queue_depth` 100. Book ch. 9.3.1 aims the Gatekeeper at **outbound** Gmail/LLM calls, not the inbound mailbox — that is `TurnInbox`'s job. **"FIFO" was dropped from this row's title:** the book notebook marked it *inferred*, not stated, so the ledger no longer claims book authority for it `[G§5.3]` `[AF-t19]` |
| M5-05e | Prove no injected failure can hang the peer | DONE | P0 | Parent DoD; timeout, drop, duplicate, and reorder are each injected, and each now reaches a **defined** outcome rather than a hang: **timeout** — `test_deadlines.py` (bounded retry raises `DeadlineError`) and `test_watchdog.py` (silence trips the watchdog); **drop** (silent peer) — `test_turn_loop_faults.py` and `test_sub_game.py` route to `TECHNICAL_LOSS`; **duplicate** — `test_turn_inbox.py` idempotent redelivery (`fresh=False`) and `test_adversarial_peer.py`; **reorder** — `test_turn_inbox.py` `ReplayError` on a non-advancing step and `test_adversarial_peer.py`. The composition is proved end-to-end through the shipped `InboundPeer` in the M5-15 suite. No new code was needed — the guards were built test-first in 05a–05d, M5-06, and M4-04 |
| M5-06 | Implement watchdog and terminal disconnect handling | DONE | P0 | Silence/disconnect produces defined outcomes. `services/watchdog.py` (liveness timer, distinct from the per-request `Deadline`) and `orchestration/shutdown.py` (`controlled_shutdown`, `heartbeat_on_transition`); 16 tests in `tests/unit/test_watchdog.py` and `tests/unit/test_controlled_shutdown.py`, both new files at 100% branch coverage |
| M5-06a | Emit a heartbeat from the main loop | DONE | P0 | `[AE-6]` `[AE-7]`. The loop already emits one transition per phase (M5-11d); `heartbeat_on_transition(watchdog, clock)` subscribes to that `on_transition` stream as the heartbeat, so no new plumbing threads through `run_turn`/`run_sub_game_over_wire`. A test drives transitions and asserts the watchdog's silence window resets |
| M5-06b | Trip the watchdog at `watchdog_timeout_sec` | DONE | P0 | Default 60 s from `[AF-t19]`; the book's 180 s code sample is illustrative only. `Watchdog.from_match` reads `network_and_league.watchdog_timeout_sec` via the same `read_limit` the deadlines use (so neither peer can lengthen its own rope); `check(now)` trips on the inclusive boundary and is **sticky** — a late heartbeat after a trip raises rather than reviving. Time is injected |
| M5-06c | Persist state and shut down cleanly on trip | DONE | P0 | `persist_state()` then `controlled_shutdown()`. `orchestration/shutdown.py` owns the **ordering and fail-closed guarantee**: persist runs first, and a *failing* `persist_state` is recorded (`ShutdownReport.persisted=False`) yet the game still ends — a shutdown that could hang is the exact failure the watchdog exists to catch. The concrete snapshot writer stays injected (the format is the log manager's job, M5-12; the wiring is the orchestrator's, M5-08) |
| M5-06d | Route a mid-turn disconnect to `TECHNICAL_LOSS` | DONE | P0 | No deadlock path exists out of `AWAITING_REVEAL`. `controlled_shutdown` routes to the one terminal state using **only declared transitions**: `AWAITING_REVEAL`/`COMPUTING_MOVE` have a direct edge, and a merely-*waiting* peer steps through `COMPUTING_MOVE` — the same documented bridge `turn_loop._await_opponent` uses, not a new edge. A trip in a synchronous phase (`COMMITTING`/`VERIFYING`) has no defined exit and raises `ShutdownError` rather than fabricating a reveal. The turn loop's own mid-turn faults already routed to `TECHNICAL_LOSS` (M5-11b); this closes the *global* liveness stall between requests |
| M5-07 | Validate provider-neutral public tunnel boundary | DONE (07a/07b) / 07c needs hardware | P1 | No provider secret enters shared configuration. The boundary is enforced and tested; the two-machine rehearsal (07c) is the one part that needs real infrastructure and is a manual runbook, below |
| M5-07a | Keep tunnel credentials out of shared config | DONE | P0 | `[AE-39]` `[G§7.4]`; secrets stay in the private TOML/env. Three independent locks, each tested: `assert_no_network_address` refuses any URL — including `public_url`, `tunnel_url`, `mcp_servers` — in the shared signed object (`test_private_config.py`); `scripts/check_secrets.py` refuses a committed `auth_token`/`api_key`/etc.; and `test_tunnel_boundary.test_only_the_url_is_exchanged_never_the_tunnel_secret` proves a tunnel token sitting beside the URL in private config never reaches the identity a peer receives |
| M5-07b | Exchange only the public URL | DONE | P1 | `[AE-10]`; provider choice is local and unobservable. `shared.private_config.public_url` reads our advertised address from `[network].public_url`, and it feeds the negotiation identity's `mcp_servers` (M5-04h). Provider-neutral by test: ngrok, cloudflare, and a self-hosted domain URL all read identically — nothing in the code privileges a provider. `config/game.toml.example` now teaches the key. `tests/unit/test_tunnel_boundary.py` |
| M5-07c | Rehearse a game across two machines over the tunnel | BLOCKED — all code DONE; needs hardware + M8 evidence (neither is code) | P0 | Book stage 5 milestone: a remote agent plays a full game. **Decided 2026-08-01, revised 2026-08-02/03; all code closed 2026-08-03.** Every code blocker is now resolved: (1) *the autonomous play loop* — `M5-17`; (2) *the pre-play protocol sequence* — `M5-17f` (`play_match`); (3) *the team-identity config source* — settled and read by `shared/team_config.py`; (4) *the `serve` command* — **BUILT**: `adapters/serve.py` `serve_match` assembles the peer from private config, hosts the mailbox on `0.0.0.0`, waits for the opponent, seals Step-0, and plays a whole match; `p2p-cop serve --root . --match … --rate-limits … --private …` launches it. Its pure helpers are unit-tested; the network body is **runbook-only** (no CI without a socket), the same boundary `M5-09`/`M5-10` already cross with real processes. **The two remaining blockers are not code:** (a) *hardware* — two physical machines and a live tunnel, Amr's to run; (b) *evidence* — the mandated proof is "Live GUI (belief map) and Replay App (Verified OK) screenshots" (`police_thief_p2p_Summary.md:2295`), both **M8** deliverables, so `M5-07c` cannot be *evidenced* until M8 exists. **Runbook:** on machine A start a tunnel (`ngrok http <my_port>` / cloudflare), set `[network].public_url` to the printed https URL and `[network].opponent_url` to the peer's, fill `[game]`/`[llm]`/`[hardware]` in `config/game.toml`, then `p2p-cop serve …`; do the mirror on machine B and confirm the match completes with both audits verifying. Driving all **six sub-games** as a series is `M7-01` |
| M5-08 | Implement the Orchestrator single-gateway coordinator | DONE | P0 | Appendix E rule 3: one coordinator owns the five subsystems and is the only place they are wired together. `orchestration/orchestrator.py` — `Orchestrator` holds each subsystem as an injected **port**, drives a turn through the M4 phase machine, and on shutdown persists through the log manager then routes to `TECHNICAL_LOSS` (wiring the `persist_state` seam M5-06 left injected). Enabling this required decoupling the watchdog from the deadline tracker: the shared "read a signed match limit" helper moved to a neutral `services/limits.py`, so no subsystem imports a sibling. 12 tests (`test_orchestrator.py`, `test_gateway_boundary.py`), both new src files at 100% branch |
| M5-08a | Define the five subsystem ports behind the gateway | DONE | P0 | MCP connector, decision module, log manager, deadline tracker, watchdog. `orchestration/ports.py` defines four `Protocol`s (`DecisionModule`, `LogManager`, `DeadlineTracker`, `LivenessWatchdog`) and re-exports the existing `peer.PeerTransport` as `MCPConnector` rather than duplicating it. The log-manager and deadline-tracker ports are deliberately minimal — their full subsystems are M5-12/M5-13 — but the seams are fixed so the gateway builds against interfaces |
| M5-08b | Forbid subsystem-to-subsystem imports by test | DONE | P0 | An import-graph test fails on any direct peer link. `test_gateway_boundary.py` walks each subsystem's source and asserts it imports none of its siblings, that none imports the gateway (the dependency points one way), and that the gateway imports the four **ports**, not the concrete subsystems. This caught the real `watchdog → deadlines` link, fixed by extracting `services/limits.py` |
| M5-08c | Keep decision logic out of the orchestrator | DONE | P1 | The gateway coordinates; it does not decide `[book §9]`. `Orchestrator.run_turn` hands the opponent's message to `decision.decide` and publishes exactly what comes back — it never inspects a move, computes a position, or reads the board. Proven by `test_orchestrator.test_the_gateway_delegates_the_decision_and_publishes_what_it_returns` (the sealed move never appears on the wire and nothing is added by the gateway) |
| M5-09 | Run the two peers as two separate OS processes | DONE | P0 | `[AE-1]` `[AE-2]`: `tests/integration/test_localhost_two_processes.py` spawns a real second interpreter and asserts the validating PID is not this one. Separate **config directories** for a live match remain M5-04/M7 work |
| M5-10 | Complete the book's stage-2 localhost milestone | DONE | P0 | Book p. 105: a message sent by peer A on localhost is received correctly by peer B — now observed, not asserted. A turn crosses HTTP into a separate OS process, is validated there through `InboundPeer`, and the transcript proves it. **The skipped gate is closed** |
| M5-10a | Launch two peers on distinct localhost ports | DONE | P0 | A free port is chosen per run and the peer is spawned with `subprocess`; readiness is polled, and the process is terminated in a fixture teardown `[AE-1]` |
| M5-10b | Exchange one negotiate round trip | DONE | P0 | Unblocked by `M5-04`. `tests/integration/test_localhost_negotiation.py`: an offer is signed in this process, carried over HTTP, and judged by a separate interpreter that loaded the match object from disk itself. Three cases cross a real socket — a matching offer is agreed; a mismatched one is refused **by name** (`hint_max_words`), which only a peer comparing against its **own** config can catch; and terms tampered with after signing are refused on the signature `[AE-11]`. The localhost peer now runs `verify_offer` rather than only schema-checking, and the spawn/reap harness moved to `tests/integration/conftest.py` so both localhost modules share it |
| M5-10c | Exchange one turn round trip | DONE | P0 | A `receive_turn` crosses the socket and is accepted; a malformed turn is acknowledged and then recorded as rejected, proving `ADR-002` holds over a real carrier |
| M5-10d | Complete one full sub-game over the wire | DONE | P0 | `orchestration/sub_game.run_sub_game_over_wire` plays bounded turns and stops the moment the game is decided. **Termination is claimed, answered, and only later proven** — over the wire nothing can referee, because neither peer sees the other. The Cop names a cell in `capture_claim`; only the Thief knows whether it stood there, so its `claim_response` decides; a `win_claim` ends it the other way; and the horizon is inclusive (`U-027`). A test asserts our own claim ends nothing, since a claim asserts nothing until the peer that knows the truth replies. `tests/integration/test_localhost_sub_game.py` runs a whole sub-game over HTTP into a separate OS process and reads back its transcript `[AE-21]` `[AE-22]` |
| M5-10e | Complete the end-of-game mutual audit over the wire | DONE | P0 | Every sealed record is revealed and delivered once the sub-game ends, with the `result_claim` matching the outcome. The audit is sent **even when this peer is taking the technical loss** — a withheld reveal cannot be checked, and the whole point is that the other side recomputes it — and an opponent that has already left does not break the reveal. Over the wire the remote process accepts a sound audit and **rejects a tampered one**, which is rule 19 enforced across a real socket rather than asserted `[AE-19]`. Mutual verification of an opponent's audit is `M7` work; this closes our half |
| M5-10f | Record the run as stage-2 milestone evidence | DONE | P1 | The peer process appends a JSONL transcript of every call's validation outcome, which the test reads back; observed behaviour, not written code |
| M5-11 | Define the turn loop around the transport | DONE | P0 | `orchestration/turn_loop.py`: `run_turn` drives one iteration through the phase machine and returns what it did. **Order corrected against the reference 2026-08-01** — it is *await → compute → apply locally → seal → send*, not compute-first: a peer must receive before advancing its own step, which is what makes the alternation strict. Transport-neutral, so a whole turn is driven, starved, and broken without a socket. `opens=True` covers the peer that moves first (the book gives that to the Thief, so a Cop always waits). 15 tests across `test_turn_loop.py` and `test_turn_loop_faults.py`. The sub-game driver and the audit that follows it are `M5-10d`/`M5-10e` |
| M5-11a | Drive the loop from the phase machine, not ad-hoc flags | DONE | P0 | `orchestration/phases.py`: the specification's transition table transcribed unchanged, with `PhaseMachine` refusing every undeclared transition **by name** `[AE-4]` `[AE-5]`. 53 tests, and deliberately most of them are refusals — a machine that accepted everything would pass a happy-path test and still deadlock the first time a peer went out of order, so every one of the 36 - 8 undeclared pairs is asserted to raise. `TECHNICAL_LOSS` is reachable only from `COMPUTING_MOVE` and `AWAITING_REVEAL`, exactly as the table writes it, so a peer cannot abandon a turn it never committed `[AE-7]`. **Phase meaning on this wire, confirmed against the reference 2026-08-01:** the profile has no live reveal tool — a turn message carries the hint and the commitment hash while the move, true position, bluff verdict, and nonce stay private until the end-of-game audit — so `AWAITING_REVEAL` means "committed and owed the opponent's next turn". The mandated names are kept verbatim rather than renamed to fit the carrier |
| M5-11b | Make one turn atomic against partial failure | DONE | P0 | A turn is sealed **exactly once**. If the send then fails the record is *not* re-sealed: a commitment is a promise, and re-sealing would give one step two hashes and hand the opponent an audit mismatch, which is an automatic zero `[AE-19]`. Tested for both failure kinds — unreachable transport and outright peer rejection — each asserting `is_sealed_once` still holds and the phase reached `TECHNICAL_LOSS` |
| M5-11c | Bound the loop by the negotiated step limit | DONE | P0 | `run_sub_game_over_wire` is bounded by `survival_threshold` and validates it (rejecting non-integers, booleans, and non-positive values), and the horizon is **inclusive** — completing the final step uncaught is a Thief win, not one step short (`U-027`) `[AF-t15]`. Missed when `M5-10d` closed on 2026-08-01: the Thief's equivalent `M5-007c` was marked DONE and this row was not. Caught by re-reading the ledger before starting the next feature |
| M5-11d | Emit a structured log line per phase transition | DONE | P1 | `run_turn` takes an `on_transition` callback invoked with every phase entered, and `PhaseMachine.history` keeps the full ordered record; a test asserts the callback sees all five phases of a turn. The log manager that consumes them is `M5-12` |
| M5-12 | Implement the log manager subsystem | DONE | P1 | Append-only, structured, and sufficient to reconstruct the match. `services/log_manager.py` — `MatchLog` is the concrete subsystem behind the `LogManager` port (M5-08); it satisfies the port structurally, and `test_gateway_boundary` now covers it as the fifth subsystem. 9 tests in `test_log_manager.py`, 100% branch |
| M5-12a | Record every sent and received message | DONE | P0 | Enough to satisfy the end-of-game audit `[AE-36]`. `record(event, detail)` appends one structured entry (`{"event": …, **detail}`); a test records a `sent` and a `received` and reads them back in order. This is the same `record` the orchestrator already calls on every phase transition (M5-08) |
| M5-12b | Record commitments and, at audit time, nonces | DONE | P0 | Nonces are written only after the final reveal `[AE-18]`. The commit **hash** is recorded live, but `record` **refuses** any detail whose member name carries `nonce` until `open_reveal()` marks the post-game reveal, raising `LogError`. So a log captured mid-match cannot leak the seal. Tested both before (refused) and after (allowed) the reveal |
| M5-12c | Keep the log append-only | DONE | P1 | No in-place edit path exists. There is no edit/delete method, and `events` returns a **tuple copy**, so a caller holding an earlier view cannot rewrite history through it. Tested: an earlier snapshot stays length-1 after a second append |
| M5-12d | Write logs under a per-match path | DONE | P1 | `logs/<match>.jsonl`; matches never overwrite each other. `MatchLog.for_match(id, dir)` writes append-only JSONL to `dir/<id>.jsonl`; distinct ids get distinct files (tested). The id is validated as a safe file stem first — empty, whitespace, `.`/`..`, or one carrying a path separator is refused. (`.jsonl`, not the row's original `.json`: the log is one append-only line per event, which a single JSON document cannot be) |
| M5-13 | Implement the deadline tracker subsystem | DONE | P0 | Every outbound request carries an expiry and is reaped on breach. `services/deadline_tracker.py` — `DeadlineTracker` is the concrete subsystem behind the `DeadlineTracker` port (M5-08); it wraps the M5-05 `RetryPolicy`/`Deadline` primitive to track the *set* of requests in flight (`open`/`close`/`pending`), reading its 30 s bound from the signed match object. 8 tests in `test_deadline_tracker.py`, 100% branch. The boundary test treats the primitive and the tracker as one subsystem (the tracker using its own primitive is intra-subsystem) |
| M5-13a | Reap expired requests rather than awaiting them | DONE | P0 | Past expiry is failure, never patience `[book §9]`. `reap(now)` returns and **drops** every request past its expiry, leaving the un-breached ones; a test opens a slow and a fresh request, advances the clock past the slow one, and asserts only it is reaped |
| M5-13b | Clear the queue cleanly on a declared technical loss | DONE | P0 | No orphaned pending request survives. `clear()` empties the whole in-flight set, so a request cannot be answered after the game is already lost; tested that `pending` is empty afterwards |
| M5-14 | Handle opponent-side rejection responses | DONE | P0 | A peer's content rejection is recorded as a game outcome and scored, not retried forever. The mechanisms were built earlier (the disjoint `TransportError`/`PeerRejectionError` types in M5-03c, `attempt`'s `retry_on`, and `turn_loop._deliver`); `tests/unit/test_rejection_handling.py` is the milestone-level proof that they combine correctly. No new runtime code was needed |
| M5-14a | Distinguish rejection from transport failure | DONE | P0 | Retry applies to one and not the other. Proven: `attempt(..., retry_on=(TransportError,))` retries a transient `TransportError` until it succeeds, but a `PeerRejectionError` **propagates at once** (tried once, never retried, even with attempts to spare). The guarantee rests on the two types being disjoint — a test re-pins that neither subclasses the other, so a rejection can never be caught by `except TransportError` and quietly retried `[M5-03c]` |
| M5-14b | Terminate deterministically on an unrecoverable rejection | DONE | P0 | The match reaches a defined terminal state. A `PeerRejectionError` during delivery drives `run_sub_game_over_wire` to `Outcome.TECHNICAL_LOSS` with the audit still sent (`result_claim: "timeout"`), so the outcome is recorded and scorable, not a hang. Also proven per-turn by `test_turn_loop_faults.test_a_refusing_acknowledgement_ends_the_turn` (`{"ok": false}` → `TECHNICAL_LOSS`) |
| M5-15 | Prove the runtime under adversarial peer behaviour | DONE | P0 | A hostile or broken opponent cannot hang or corrupt this peer. Each guard was built test-first in its own milestone; `tests/unit/test_adversarial_peer.py` is the consolidated milestone-level proof, adding the two properties the piecemeal tests did not assert: **cannot corrupt** (a rejected message leaves prior audit-bearing state intact and the next honest turn still admits) and **cannot hang** (sustained silence trips the watchdog into a terminal shutdown, composing M5-05 + M5-06). Verified through the shipped `InboundPeer`, not a stand-in |
| M5-15a | Survive a peer that never responds | DONE | P0 | Deadline plus watchdog produce a terminal outcome. Two proofs: the per-turn side is `test_turn_loop_faults.test_a_silent_opponent_reaches_the_terminal_state` and `test_sub_game.test_a_silent_opponent_is_a_technical_loss_not_a_hang`; the **watchdog** side is `test_adversarial_peer.test_sustained_silence_trips_the_watchdog_into_a_terminal_shutdown`, with `test_a_peer_that_keeps_moving_never_trips_the_watchdog` as the contrast that makes the trip meaningful (new with M5-06) |
| M5-15b | Survive a peer that responds out of order | DONE | P0 | The phase machine rejects the transition `[AE-5]` (`test_phases`, illegal-transition rejection), and an out-of-order **turn step** that does not advance its sender is refused without rewinding progress: `test_adversarial_peer.test_a_replayed_turn_is_rejected_yet_the_next_real_step_admits` |
| M5-15c | Survive a peer that replays an earlier message | DONE | P0 | Idempotency guard rejects it `[ADR-002]`. `TurnInbox` dedup/replay/conflict is proven in `test_turn_inbox` and `test_peer_inbound`; the new `test_adversarial_peer.test_a_conflicting_turn_leaves_the_accepted_commit_on_record` adds the corruption property — a refused conflict leaves the first commit as the one the audit must reproduce |
| M5-15d | Survive a peer that sends oversized or malformed input | DONE | P0 | Schema validation rejects before domain code runs (`test_peer_inbound.test_invalid_message_is_rejected`); `test_adversarial_peer.test_a_malformed_turn_changes_no_state_before_it_is_refused` and `test_an_unknown_tool_is_refused_without_side_effects` add that a refusal changes no state. **Note on "oversized":** the turn schema is `additionalProperties: true` at top level, so an over-large message with extra junk fields is *tolerated* (the domain reads only known fields) rather than rejected — a size cap is deliberately not invented, as any threshold would be un-sourced and could refuse a legitimate classmate message; a single large message is not a hang |
| M5-15e | Survive a peer that disconnects mid-audit | DONE | P0 | The audit outcome is still decided and recorded: `test_sub_game.test_an_opponent_that_has_left_does_not_break_the_reveal` (a `submit_audit` that raises `ConnectionError` still yields a verifiable audit) and `test_a_technical_loss_still_sends_its_audit`. `sub_game._reveal` tolerates an opponent already gone and returns the payload regardless |
| M5-16 | Document the runtime architecture | DONE | P2 | `PRD_p2p_mcp.md` "Runtime architecture (M5-16)" section describes the gateway, the five subsystems, and the turn loop, now that all of them exist (M5-08/12/13 built this session) |
| M5-16a | Draw the subsystem diagram | DONE | P2 | Gateway plus five subsystems, no peer-to-peer links `[G§20.1]`. A mermaid `graph TD` in `PRD_p2p_mcp.md`: every arrow runs gateway↔subsystem, and the neutral `services.limits` is shown below the subsystem line (read by tracker/watchdog/gatekeeper) so the diagram matches the boundary test |
| M5-16b | Document every failure path and its outcome | DONE | P1 | One row per fault class and its terminal state. A table in `PRD_p2p_mcp.md` maps eight fault classes (silence, out-of-order, replay, malformed, mid-audit disconnect, content rejection, transport fault, own-seal failure) each to its guard and defined terminal outcome, with the pinning test named for each |
| M5-17 | Drive the mailbox: the autonomous over-wire play loop | DONE | P0 | The M5→M6 bridge, and the code half of `M5-07c`. `adapters.build_server` is a passive mailbox and `run_turn` only consumes, so **nothing joined them** — every sub-game test had to hand `receive` a scripted opponent. Built: `orchestration/polling.py` (`poll_for_turn`, `turn_receiver`) and `adapters.take_turn`. `tests/unit/test_autonomous_play.py` plays a whole sub-game whose only turn source is the mailbox, with no message fed in by hand. 24 tests across four new files, both new src files at 100% branch |
| M5-17a | Poll the local inbox for the opponent's turn | DONE | P0 | Confirmed against the reference 2026-08-02 before implementing: its `PeerRuntime` polls **its own** inboxes via `McpTransport` at `[network].poll_interval_seconds` (0.5 s shipped), and the inbound `receive_turn` tool "does not compute the next turn; it only deposits the message". The book mandates a strict state machine rather than a bare loop (§8.3) — both hold, because polling is only *how* a queued message is picked up while `PhaseMachine` still decides what may legally follow. `DEFAULT_POLL_INTERVAL` is local, private and never negotiated, so it cannot affect a hash or interoperability |
| M5-17b | Bound the wait so silence decides instead of blocking | DONE | P0 | `[AE-6]` verbatim: "Mandatory to implement a deadline-tracking mechanism to prevent deadlocks while waiting for the opponent". `poll_for_turn` stops at the turn timeout and returns `None`, which `run_turn` turns into the one declared exit to `TECHNICAL_LOSS`. The boundary itself counts as expired, matching `services/deadlines.py`, so "expired" never means two things in one peer. A turn **already queued** is taken even at zero budget: the deadline bounds *waiting*, and refusing an arrived message would forfeit a match on a technicality |
| M5-17c | Emit the heartbeat from the loop that actually waits | DONE | P0 | Book §8.4.2 puts the watchdog on "the main game loop", and a peer waiting for an opponent is otherwise doing nothing observable — exactly when a frozen process and a patient one look identical. Every poll iteration pulses, so a peer asleep inside the wait still proves it is alive `[AE-7]`. Time is injected, so the pulse train is asserted by advancing a number rather than by sleeping |
| M5-17d | Keep a hostile mailbox from starving the loop | DONE | P0 | Three behaviours in `take_turn`, each of which would silently break an unattended match: a **rejected** turn is consumed (leaving it queued makes the poller re-reject it forever and starve the real turn behind it); a **second** queued turn is left in place (draining both discards the next step rather than playing it); and the other three mailboxes are drained first (a negotiate/audit/control message parked in front of a turn stalls the game). 7 tests in `test_take_turn.py` |
| M5-17e | Launch a peer as a long-running process — hosting and readiness | DONE | P0 | The two mechanical halves of launching, built 2026-08-02 and both testable without a real match. `adapters/serving.py`: `serve_in_background` runs the mailbox on a **daemon** thread (so it can never outlive the game and turn a finished match into a hang) after `ensure_port_free` fails loudly on a stale peer still holding the port; `port_answers` is the readiness probe. `services/readiness.py`: `wait_for_peer` is a **bounded** retry so start order does not matter. 18 tests across `test_serving.py`/`test_readiness.py`. See `ADR-009` |
| M5-17e-i | Bind `0.0.0.0`, never `127.0.0.1` | DONE | P0 | **The one-word bug no local test would ever catch.** Confirmed from three independent sources: the book prints `mcp.run(transport="http", host="0.0.0.0", port=8000)` with the comment "Bind the server so a tunnel can expose it publicly" (`police_thief_p2p_Summary.md:657`); rule 10 is "Use tunnels to expose the local server to the public internet. **Sanction: Inability to compete against opponents**" (`:3326`); `DEV-SPEC.md:382` agrees. The **reference binds `127.0.0.1`** (police 8802, thief 8801) because it runs both peers on one machine — single-machine convenience, and the book outranks the simulator. Loopback would pass every local check and be invisible through the tunnel, failing only at the stage-5 rehearsal where it reads as a network fault. `DEFAULT_BIND_HOST` is pinned by a test `[AE-10]` |
| M5-17e-ii | Tolerate either start order | DONE | P0 | Two peers launched by two people cannot start at the same instant; the reference is explicit that "start order doesn't matter". `wait_for_peer` polls until the opponent answers, bounded by `[network].connect_timeout_seconds` (60) with `retry_interval_seconds` (1.0) between tries — both confirmed against the reference 2026-08-02, both **private** so neither can affect a hash. It returns `False` rather than raising: an opponent nobody launched is an operator situation, and raising would blur it with the in-match deadline failures rule 6 governs. Deliberately a separate module from `deadlines`/`watchdog`, because startup is the **one** phase where waiting is correct and that leniency must not leak into the match |
| M5-17f | Sequence negotiation and first move autonomously | DONE | P0 | **Closed 2026-08-03; all three children DONE and composed end to end.** The book's pre-play order — negotiate → exchange & verify Step-0 → write and lock the declaration → play — runs as one autonomous sequence in `orchestration/match.py` (`play_match`): it calls `negotiate_match` (`M5-17f-i` gate + `M5-17f-ii` attestation), and **only** on agreement builds and locks the declaration (`M5-17f-iii`) before handing off to `run_sub_game_over_wire`. A match that never agrees never plays — a `None` (silent opponent) or a `NegotiationError` (refusal) stops before the declaration is built, so no lock is ever written for a game that will not happen. Transport-neutral (injected transport + mailbox sources + clock), so the whole sequence is proven in-memory: 3 tests in `test_match.py`, module at 100% branch. **What this does NOT include:** the network `serve` command that assembles `play_match` from config + a live socket — that is the remaining `M5-07c` "serve CLI" item, and it needs one unsettled input, the **team-identity config source** (`group_id`/`members`/`repos`/`mcp_servers`/`llm_model`/`spec`), which is not yet defined in any config file and must not be invented silently. `serve` stays unwired until that source is settled |
| M5-17f-i | Reach mutual agreement before the first move | DONE | P0 | Built 2026-08-02. `orchestration/negotiation_handshake.py` — `negotiate_match` sends our signed offer (`build_offer`), waits for the opponent's on the agreements mailbox with the same bounded `poll_for_turn` the turn loop uses, and returns an `Agreement` **only** once `verify_offer` accepts it against our own terms and `config_sha256` lock. Three distinct outcomes, each tested: an `Agreement` (verified); a `NegotiationError` naming the offending term (rule 11 refusal — play must not start); and `None` (no counter-offer before the deadline — a silent opponent is not a refusal but is equally not a game). A carrier fault sending *our* offer is a separate `HandshakeError`, never a rule-11 loss. Transport-neutral and time-injected: 7 tests in `test_negotiation_handshake.py`, module at 100% branch. Contract-independent; no `shared_contract/` change |
| M5-17f-ii | Exchange and mutually sign the Step-0 attestation | DONE | P0 | Built 2026-08-02 after the **Amr-confirmed carrier decision: Option A — fold Step-0 into the negotiation offer, verify on receipt, tolerate omission.** The key realisation that settled the wire shape: Step-0 carries **nothing secret** (hardware, model, git commit, config hash are exactly what the public declaration lists), so unlike a move it is exchanged *revealed* and verified on the spot — "mutually signed before the first move" is met cleanly, with no deferral to the audit and no schema change (`negotiate` is `additionalProperties: true`, so `step_zero` is tolerated). `protocol/attestation.py` gained `attestation_wire` (serialize a `SealedAttestation` to `{payload, nonce, commit}`) and `review_opponent_attestation` (tolerate omission; return a sound present seal; **refuse** a malformed or non-reproducing one — the `verify_offer` config-lock pattern, `U-029`). `negotiate_match` gained an optional `step_zero`: when given it rides on our offer, and the opponent's is verified into `Agreement.opponent_step_zero`. Enforcement is one-directional per `U-029`: we always send ours, we never refuse a peer that omits, but a **present-and-tampered** seal is a rule-11 refusal. 11 tests in `test_attestation_exchange.py`; both changed modules at 100% branch. No `shared_contract/` change; contract stays `0.2.5-proposed` |
| M5-17f-iii | Write and lock the pre-game declaration | DONE | P0 | **Minimal M5 form built 2026-08-03 (Amr-confirmed "pull the lock forward").** `protocol/declaration.py` — `build_declaration` assembles the pre-game declaration from injected, already-agreed sources (both identities' `groups` and their four repo `links` per rule 49, `config_sha256`, `num_sub_games`, `max_tokens_per_game`, `game_started_at`; `game_ended_at` null until post-game), and `lock_declaration` produces the cryptographic lock — a plain canonical SHA-256, the same public/reproducible construction as the config lock, since nothing here is secret. This closes the **timing-and-lock obligation** M5 owns: a declaration exists after negotiation and is locked before the first move. **Deliberately does NOT preempt M7:** `game_id`/`game_uid` are *injected*, not derived (their cross-peer derivation is M7's to fix), and the JSON-Schema envelope (`_schema`/`schema_version`), file emission, and email reporting stay `M7-02a`/`M7-22`. 11 tests in `test_declaration.py`, module at 100% branch. No `shared_contract/` change. Cross-reference: `M7-22` |

---

## X — Interoperability defects found by probing (2026-08-06)

*Not a milestone. Cross-repo defects that had no owning row — a ledger defect, not an exemption. `X-01`/`X-02` were found by sending our own peers the messages a classmate would send; `X-03` was found by reading the bundle as a stranger would.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| X-01 | Stop scoring a verifying audit as forgery over nonce shape `C-033` | DONE | P0 | Found 2026-08-06 by probing our own peers. `verify_commit` hashes whatever nonce it is given; only a digest mismatch is `TAMPERED` `[AE-19]` `[book :1270]`. Generation stays strict at 32 lowercase hex. Schemas relaxed to `^[0-9a-f]+$`; bundle bumped to `0.2.6-proposed` `[G-18]`. `test_audit_nonce_tolerance.py` |
| X-02 | Make the two peers agree on unmodelled wire fields | DONE | P0 | The Cop tolerated an extra field and the Thief refused it, so one classmate message played fine against one peer and silently starved the other into a technical loss. Both now ignore extras on turn, control and audit messages, matching the reference; missing **required** fields still refuse |
| X-03 | Stop the bundle advertising the retired copy model | DONE | P0 | **Fixed 2026-08-06**, bundle `0.2.6-proposed` → `0.2.7-proposed`, manifest `4dd5d18a…`. The correction is not "copying is wrong" — the book **recommends** sharing the *formula* (ch. 6, the scent model) and Appendix E rule 2 prohibits only sharing memory or variables, sanction "immediate disqualification". The bundle holds no live state, so offering it to **any opponent** is the recommended half. Three things were actually wrong: it named our **companion Thief repo** (retired under `THIEF-002`, and the book names that exact hazard — a team building both sides on one machine); it implied copying establishes conformance, when the book's evidence is a `Verified OK` replay of a real match (§7.4, Appendix C) and rule 52 permits warm-ups for exactly that; and it cited **our own summary's line numbers**, useless to the stranger the file is written for — now cited by chapter and rule. 12 in-bundle `x-contract-version` declarations still said `0.2.6` after the bump and would have shipped an internally inconsistent bundle; 19 current-state claims updated, 3 historical ones deliberately left |
| X-04 | Stop the per-sub-game config schema validating only a template | DONE | P0 | Found 2026-08-06 while building the artifact it governs. `schemas/per-subgame-config.schema.json` pinned `links.config` with `"pattern": "g<NN>"` — a **literal**, matching the fixture's placeholder rather than a filename. It accepted `config_x_g<NN>.json` and **refused every real emitted artifact**, so the schema could only ever validate a template: exactly the failure `M7-23` exists to prevent, baked into the contract. Patterns corrected to `^config_.+_g\d{2}\.json$` / `^log_…$`, the valid fixture given real filenames, and the invalid fixture too — it exists to prove `sub_game > 6` is refused and was failing on the placeholder instead, masking the case it was written for. Bundle `0.2.7-proposed` → `0.2.8-proposed`, manifest `88df2089…` `[G-18]` |
| X-05 | Read the six-sub-game count off the right Appendix F row | DONE | P1 | Found 2026-08-06 while implementing `M7-01b`. Appendix F prints **two rows with the same label** `[Number of Agents]`: `:3484` is "number of players in the race | 2 | Fixed" and `:3540` is "number of agents **in a series against an opponent** | 6 | Fixed". The second is the *games* count under a mistranslated label -- its own description says so. The template at `:2963` further carries `"num_games": 1`, a single-game default for the example file rather than the league requirement. Reading either of the other two would have produced a series of 2 or of 1. Recorded so the next reader does not have to re-derive it |
| X-06 | Align the artifacts to the lecturer's templates | DONE | P0 | **Fixed 2026-08-06**, bundle `0.2.8-proposed` → `0.2.9-proposed`, manifest `245c10f1…`. Config now uses `sub_game_number` (`inst/:3019`) and carries `agreed_between` (`:2928`) and `config_name`. The log uses **one `records[]`** whose entries gain `payload` and `nonce` at reveal, instead of a `steps` array plus a separate `audit` section -- same rule 18 timing guarantee, the template's structure. The declaration's `links` now names the four artifact files and rule 49's four repo URLs moved to `repositories`; **those were one field, which was a conflation of two different requirements, not a shortcut**. Our own schema had required `sub_game`, so this cost a bundle bump; 18 current-state version claims updated line by line. **Both notebooks had already said this** -- the code notebook gave the exact roster including `sub_game_number` and `config_name`, and it went unregistered because it was read from a screenshot. Second concrete cost of that habit in one day |

---

## M6 — Scent, belief and private strategy

*Gate: legal deterministic behaviour under observation and fallback tests.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M6-01 | Implement multiplicative scent field | DONE | P1 | Book equation and fixed constants pass numeric tests. **Closed 2026-08-05**: all four children DONE. `M6-01a` reached 25/25 once `U-030` was resolved *by negotiation* rather than by a ruling — the eight unnamed cells are an agreed, hash-locked term (`M6-07`), not a private guess. `U-031` (re-emission cap) remains open but does not block: the formula is implemented as written and is inside the lock, so a peer reading it differently is refused pre-game |
| M6-01a | Emit a 5×5 field centred on the agent | DONE | P1 | Centre `τ = 0.9`, radial decay `[AF-t16]` `[PRD-scent]`. `emission_field` now places **all 25 cells**. The 17 book-documented values stay in `DOCUMENTED_EMISSION` (centre `0.90`, cross `0.62`, diagonal `0.20`, mid-side `0.14`, corner `0.04`, verified 2026-08-05 at `inst/police_thief_p2p_Summary.md:947-955`); the **8 intermediate cells** `(±2,±1)`/`(±1,±2)` take `DEFAULT_OUTER_RING_DELTA`, a **negotiated** parameter carried inside the `M6-07` lock. Omitting them was an interop defect, not caution: the reference emits 25 and asserts a snapshot length of 25, so 8 absent cells read to an opponent as 8 zeros. The two records are kept apart on purpose so a negotiated number never acquires book authority |
| M6-01b | Apply `τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ)` per full turn | DONE | P1 | Decay runs once after both sides act, never per half-turn. `strategy/scent.decay` implements the formula exactly; **multiplicative, not subtractive** (`C-009`) — at `ρ=0.10` a cell retains `0.90·τ`, and a test asserts `0.81 ≠ 0.80`. No re-emission cap is applied (`U-031`). The once-per-full-turn timing is the caller's to honour |
| M6-01c | Pin the radial profile with numeric vectors | DONE | P1 | 0.90 / 0.62 / 0.20 / 0.14 / 0.04 asserted to the documented precision. `DOCUMENTED_EMISSION` sourced from the book heatmap (`police_thief_p2p_unverified_translation.md:962-970`); `test_scent.py` pins each radial class and its symmetry |
| M6-01d | Clip intensities to non-negative | DONE | P1 | A never-visited cell reads 0, meaning absence of information. `decay`'s `max(0.0, …)` clips a negative update to absence; tested at `τ=0`, `Δτ=−1` |
| M6-02 | Implement Cop-local belief update | DONE | P1 | Belief uses observation only and normalizes safely. **Closed 2026-08-06**: the hint-driven half landed with `M6-11`. `strategy/hint_decode.py` turns free text into a directional likelihood, `strategy/trust.py` carries the book's reliability factor, and `strategy/consume.py` applies them in the book's order — unfalsifiable scent first, then the claim judged against it (`:1017-1020`). Belief stays Cop-private (M6-18), so the likelihood/trust math is a **local** decision, not a cross-peer-locked value |
| M6-02a | Maintain a board-sized probability matrix | DONE | P1 | Sized to `grid_size`, not to the book's 10×10 illustration. `Belief.uniform(grid_size)` builds a normalised `grid_size²` distribution; a test pins it sums to 1 and is sized to the negotiated board |
| M6-02b | Apply Bayes with a per-hint trust factor | DONE | P1 | A hint contradicted by scent lowers its own trust weight `[PRD-scent]`. `trust_weighted` tempers the decoded likelihood toward uniform by `(1−t)` before `Belief.updated` applies Bayes, so a distrusted hint moves belief less and a fully distrusted one not at all — the book's "the pursuer ignores the verbal claim" reached by arithmetic rather than a special case. **The book fixes no numbers here**: it states no trust value, step, decay rate or bound, and says the translation into a belief map is the agent's own (`:1025`), so `INITIAL_TRUST` and `TRUST_STEP` are PROJECT-PROPOSED. Confirmed against the book PDF 2026-08-06 |
| M6-02c | Normalize without dividing by zero | DONE | P1 | A zero-evidence update leaves a valid distribution. `Belief.updated` returns the prior unchanged when total evidence is `≤ 0`; tested with an empty and an all-non-positive likelihood |
| M6-02d | Prove the belief never reads objective truth | DONE | P0 | `[AE-8]` `[AE-9]`; input is observation only. `Belief.updated` takes a likelihood map and `scent_likelihood` takes the observed field — never a Thief cell; a signature test asserts neither carries a `thief`/`truth`/`position`/`target` parameter, so truth cannot enter by construction |
| M6-02e | Decode an inbound hint into a belief-space update | DONE | P1 | Free text maps to evidence without a coordinate protocol `[AE-27]`. `decode_hint` matches common direction words by regex and treats a direction as a **half-plane** claim relative to *our own* cell — the only frame two peers share without exchanging coordinates. An unrecognised, absent, empty, non-text or over-long hint decodes to uniform, which Bayes applies as no evidence (`M6-11c`) |
| M6-02f | Lower a hint's trust when scent contradicts it | DONE | P1 | The book's worked example, implemented as arithmetic. `expected_fresh_scent()` derives the study's `0.81 = 0.9·(1−0.1)` from the **locked** model's constants rather than hard-coding it, `corroboration` compares it to the strongest scent actually measured where the hint points, and `update_trust` moves the running coefficient, clipped `[0,1]`. **Found while doing this (`C-032`): the case study's quadrant labels are inverted** — it calls `(1,4)` south-east and `(5,2)` northern under a top-left origin. Its intensities are used, its cell labels are not |
| M6-03 | Integrate belief into deterministic pursuit | DONE | P1 | Policy improves target choice without illegal actions. `strategy/belief_pursuit.py` composes `Belief.most_likely` with the M3 pursuit: `pursue_belief`/`belief_turn_intent` aim the deterministic, barrier-aware policy at `argmax b(s)` instead of an oracle Thief cell. 5 tests, module at 100% branch |
| M6-03a | Target `argmax b(s)` and minimise Manhattan distance | DONE | P1 | `[book §7]`; ties broken in fixed order for determinism. Target is `Belief.most_likely` (deterministic row-major tie-break); distance is the M3 **barrier-aware BFS**, a deliberate improvement over the book's straight-line Manhattan (equal on an open board, correct around walls, `M3-09b`) — the belief pursuit inherits it rather than regressing |
| M6-03b | Keep every emitted action legal under the domain layer | DONE | P0 | Belief may misdirect the target; it may never produce an illegal move. `pursue_belief` delegates to `choose_action`, whose candidates come only from `legal_moves`; a test boxes the Cop in and a far, unreachable belief peak still yields `Action.STAY` — legal, never illegal |
| M6-03c | Bound per-turn decision time | DONE | P1 | The policy returns within the negotiated response timeout `[AF-t19]`. Bounded **by construction**: belief update, `argmax`, and BFS are each `O(grid²)`, terminating, with no I/O or unbounded loop — microseconds at the 7×7 floor. The empirical worst-case measurement now corroborates this (`M6-13a`): 1.3 ms at the 7×7 floor, 69× inside the 30 s timeout even at 100×100 |
| M6-03d | Keep the policy deterministic and reproducible | DONE | P1 | Identical observations yield an identical action sequence. Both halves are deterministic — `most_likely` breaks ties row-major, the pursuit falls back to `Action` declaration order — and a test asserts two calls on the same belief and position agree |
| M6-04 | Add private strategy configuration | DONE | P2 | Tuning stays local and SDK-loaded. **There is no tuning to localise:** every policy in this repository ranks lexicographically rather than by a weighted sum — `pursue_belief`, `choose_turn_intent` and `choose_squeeze` all order candidates by strict criterion priority with a fixed tie-break, so no coefficient exists that could be tuned, leaked, or drift between peers. That is a deliberate choice recorded in the report: no calibration data exists that would justify weights, and a strict order is auditable from the log while tuned coefficients are not |
| M6-04a | Load strategy tuning from the private TOML only | DONE | P2 | No tuning value enters the shared JSON `[ADR-004]`. Vacuously satisfied and pinned: `test_the_squeeze_never_receives_the_thiefs_true_position` and the weight-free signatures show no policy takes a tunable coefficient at all, so the shared object carries none. Any future weight must load from `config/game.toml` |
| M6-05 | Add optional verbal/LLM adapter with zero-token fallback | DONE | P2 | Provider failure always falls back deterministically. Template layer (`strategy/hints.py`) + optional LLM adapter (`strategy/verbal.py`, **2026-08-05**): `generate_hint` wraps any provider and returns the deterministic template on **any** failure (absent/raising/timeout/empty/over-long/coordinate-laden); `openai_provider` reads `OPENAI_API_KEY` at call time with an injected transport; `provider_from_config` selects on `[trash_talk].provider`. Default stays `template` (zero tokens). 24 offline tests |
| M6-05a | Ship the zero-token template provider as default | DONE | P1 | A whole series must be playable at zero tokens `[AF-t21]`. `template_hint` needs no network and no account — a pure-Python template with truth/bluff variants |
| M6-05b | Enforce the hint word limit | DONE | P0 | 15 words by default, applied to template and model alike `[AF-t14]`. `hint_max_words` reads `world.hint_max_words` (default 15); `within_word_limit`/`enforce_word_limit` bound and truncate; `validate_hint` is the single guard both providers pass |
| M6-05c | Keep hints natural-language only | DONE | P0 | `[AE-26]` mandatory; `[AE-27]` forbids coordinate or numeric protocols. A validator rejects a hint that encodes coordinates. `encodes_coordinates` refuses a digit pair (`3,4`/`3 4`) or an explicit `row`/`col`/`cell` index while allowing worded quantities (`three blocks north`); deliberately conservative (PROJECT-PROPOSED) since our templates emit no digits |
| M6-05d | Keep the LLM out of movement decisions | DONE | P0 | `[AE-25]` `[ADR-007]`; the move is always pure Python. `generate_hint` only ever returns a `Hint` (text + intent), never an `Action`; the guard test reads the movement modules (`pursuit`, `belief_pursuit`, `barrier_policy`) and asserts none imports `verbal`/`openai` — no code path from a move to the model |
| M6-05e | Fall back deterministically on provider failure | DONE | P1 | Parent DoD; a blocked provider never stalls a turn. `generate_hint` catches any provider exception and returns the deterministic template; parametrised tests cover a raising, timing-out, empty, over-long, and coordinate-encoding provider — every one degrades to zero-token play |
| M6-06 | Implement predictive barrier squeezing | DONE | P2 | `strategy/squeeze.py` (13 tests). `:812` is the whole specification — "block the Thief's escape routes **without inadvertently obstructing their own path**" — and the second clause is the hard half. `choose_squeeze` ranks legal cells by escapes removed, then our own mobility, then proximity, lexicographically; it **refuses** any cell that lengthens our own route to the prediction. Needed the belief model (`M6-02`), because it acts on the argmax *prediction*, never an observed cell — a signature test pins that truth cannot enter. **The tactic is deliberately selective:** at range 1 the only squeezing cell is our own, and at range 2 in a straight line it is our route; it fires where our path has redundancy, which is why the reference likewise "only occasionally walls a cell" |
| M6-07 | Lock and exchange the scent-model hash before the first move | DONE | P0 | **Built 2026-08-05** (`strategy/scent_lock.py`). | Appendix E rule 23 (deviation cancels the game): the agreed emission/decay model is canonicalised, SHA-256 locked pre-game, exchanged during negotiation, and any mismatch refuses the match. The locked formula follows the DEV-SPEC reading — at `ρ = 0.10` the factor `(1-ρ)` **retains** 90% of prior scent. The book's "reduced by 90%" (p. 43) and "`ρ` toward 1.0 saturates the board" (p. 46) are arithmetic errors and must not be implemented |
| M6-07a | Canonicalise the scent model to hashable bytes | DONE | P0 | `scent_model_record()` is one canonical dict — formula string, `center_intensity`/`decay_per_step`/`field_size`, and the full 25-cell profile keyed by **squared distance** (not by offset, so two peers cannot agree on physics yet differ on key spelling). Hashed with the same canonical JSON as `config_sha256`. The record shape is the interop contract: `test_scent_lock.py` pins the digest `416a57e1…`, which the independently written Thief peer reproduces exactly |
| M6-07b | Exchange and compare the lock at negotiation | DONE | P0 | `build_offer(scent_lock=…, scent_outer_ring=…)` publishes ours; `verify_offer(expected_scent_lock=…)` compares theirs. **Tolerate omission, refuse a mismatch** — the same `U-029`/`C-031` rule already settled for `config_sha256`. Silence is not deviation, and the pinned simulator publishes no standalone scent hash (it folds pheromone terms into `config_sha256`), so requiring one would refuse every simulator-built classmate over a message they never send. The lock rides **outside** the signed `terms` for that reason. Both values are **injected** by the caller so `protocol/` never imports `strategy/` |
| M6-07c | Record the arithmetic correction in the report | DONE | P1 | Book p. 43 and p. 46 errors disclosed under the p. 5 contradiction clause. **Already satisfied** — verified 2026-08-06 at `README.md` lines 412-414, written during the `M6-07` scent-lock work: `(1-ρ)` *retains* 90%, the p.43 "reduced by 90%" prose and the p.46 saturation claim are named as arithmetic errors, and a decay rate near 1.0 is stated to erase the trail rather than saturate it. The row was stale, not open |
| M6-08 | Serialize and parse the scent observation on the wire | DONE | P1 | The observed field survives a round trip without precision loss. `protocol/scent_wire.py`: `encode_scent`/`decode_scent`, proven end to end — emit, encode, decode, and the belief argmax lands on the emitter's cell |
| M6-08a | Encode the emitted field in the turn message | DONE | P1 | **The DoD was wrong and is corrected.** It said "empty cells are omitted, not zero-filled"; the reference *includes* zeros so the receiver always sees a fixed-size window, and interop follows the reference. We now send the full window clipped to the board and **tolerate** an omitting peer on receive — an absent cell and a zero cell mean the same thing. `serve.py` no longer sends a hard-coded `{}` |
| M6-08b | Parse an opponent field defensively | DONE | P0 | Out-of-range, non-numeric, and off-board keys reject, plus NaN/infinity, booleans, negative intensities, non-string keys, and values above the model's saturation limit. Eleven hostile shapes are pinned. A corrupt grid **raises** rather than degrading to empty: scent is the one channel that cannot be faked, so silently reading a corrupt one as "no evidence" would discard our strongest signal |
| M6-08c | Pin the numeric precision on the wire | DONE | P0 | Repeated decay yields `0.7290000000000001`; the wire carries 6 decimal places. **Send-side only** — parsing accepts any precision, because tightening what we emit cannot break a peer while tightening what we accept can. Note the row's premise ("or the locked model hash means nothing") is wrong: `scent_model_hash` locks the *model*, never the emitted numbers, so rounding cannot invalidate a lock |
| M6-09 | Prove the scent model is symmetric and involuntary | DONE | P1 | Emission follows movement automatically; no code path can suppress or fake it. `strategy/scent_field.py` `[book :895]` |
| M6-09a | Emit on every action including `STAY` | DONE | P1 | Staying still still deposits scent `[book §6]`. `:895`: the scent "is emitted by the **movement or the stay itself**". A test proves a STAY and an arrival leave the same trail, and that five stays cannot hide a Thief |
| M6-09b | Read only the opponent's field, never one's own | DONE | P0 | A test proves own-scent is never used as evidence. `:895`: "each side emits its own scent, and each side reads the scent field of its opponent only". Structurally separated: `ScentField` is ours and is only ever *encoded*; `decode_scent` produces the opponent's and is the only input to `consume_turn` |
| M6-09c | Make suppression impossible by construction | DONE | P0 | No flag or branch can skip emission. `ScentField.advance` takes a **cell** and nothing else — a signature test asserts its only parameter is `occupied`, so there is no action, flag, or provider a caller could set to stay silent. Suppression is unrepresentable, not merely refused |
| M6-10 | Implement hint generation | DONE | P1 | A hint is produced each turn, truthful or bluffed, within the agreed limits. `serve_decide` now emits a real hint every turn -- it used to send the fixed string "holding position", a hint in name only, since constant text carries no information true or false. Intent alternates so both a truthful and a bluffed hint are exercised, and it is sealed in the commitment so a bluff cannot be denied at audit (`M6-10a`). **DoD corrected:** the row said the place should be "belief-derived". It must not be -- see `M6-10e` |
| M6-10a | Carry an explicit truth/bluff intent flag | DONE | P0 | Sealed in the commitment so it cannot be revised later `[book §8]`. `Hint.intent` is `truth`/`bluff`; it rides in the private sealed payload (the commit-reveal ledger already seals `intent`), so it cannot be revised after commit |
| M6-10b | Generate from the zero-token template provider | DONE | P1 | Default path; no network, no account `[AF-t21]`. `template_hint` |
| M6-10c | Enforce the word limit at generation time | DONE | P0 | 15 words default; the limit applies to template and model alike `[AF-t14]`. `template_hint` truncates and then `validate_hint`s, so an over-limit hint cannot leave the generator |
| M6-10d | Reject a generated hint that encodes coordinates | DONE | P0 | `[AE-27]`; a validator, not a convention. `validate_hint` runs `encodes_coordinates` on the generated text and raises `HintError`; a test proves a coordinate-laden `place` is refused, not emitted |
| M6-10e | Support landmark hints when a map area is agreed | DONE | P2 | Generic landmarks when `map_area` is empty `[AF-t14]`. `strategy/landmarks.py` (12 tests): `place_for` dresses **our own cell** in a landmark from the agreed `world.map_area`, and falls back to generic bearings when it is empty, unknown, malformed or absent -- `:1585` "defaults to generic landmarks" and p.51/131 "in the absence of a definition… generic bearings are used". Every vocabulary word is asserted coordinate-free `[AE-27]` and short enough that no composed hint can overrun the word limit. **The place is NOT belief-derived, and that is load-bearing:** a hint is a claim about the *sender*, which the opponent tests against the sender's own scent (`:1016`, `:1020`), so a hint about the opponent would be unfalsifiable -- and a belief-derived place would publish private inference the `M6-18` guard exists to keep off the wire. Both notebooks confirmed the reference derives `place` from the negotiated `setting` and explicitly **not** from the belief heatmap |
| M6-10f | Trigger any model provider only every N steps | DONE | P2 | `every_n_steps` bounds consumption `[:1581]`. `is_model_turn(step, n)` fires on multiples of `n`; `n=1` is every step and `n<=0` disables the model entirely, so "disable every provider" is a supported configuration rather than an untested edge |
| M6-11 | Implement hint consumption | DONE | P1 | An inbound hint updates belief without ever being trusted blindly. `strategy/consume.consume_turn` is the one entry point; trust runs **forward** between turns, so a peer that lies repeatedly is believed less each time — a value recomputed per turn would forgive every lie. All three sub-tasks below |
| M6-11a | Parse an inbound hint without executing it | DONE | P0 | Text is evidence, never an instruction. Two guards, merged 2026-08-06: `receive_hint` returns an inert `ReceivedHint` and **refuses a coordinate-encoding hint outright** using the same `encodes_coordinates` our own generator must pass, so `[AE-27]` is one rule in both directions; `hint_directions` then matches only direction words by regex, never `eval`/`exec`. `test_a_command_like_hint_is_read_as_text_not_executed` proves "move north immediately or forfeit the match" and "north" decode identically |
| M6-11b | Weight the hint by the sender's running trust score | DONE | P1 | Repeated contradiction lowers the weight. `consume_turn` returns the updated trust as the input to the next turn; a test runs four contradicted hints and asserts trust falls monotonically. A distrusted hint is **ignored, never inverted** — a liar's claim is evidence of nothing, not of the opposite, since it may still be true |
| M6-11c | Tolerate an absent, empty, or over-long hint | DONE | P1 | Missing evidence is not an error state. `None`, `""`, whitespace, a non-string, and an over-`max_words` hint all decode to a uniform likelihood and leave belief untouched; refusing them would let a silent opponent crash us |
| M6-12 | Prove the strategy layer under observation tests | DONE | P0 | Behaviour stays legal and deterministic under every observation shape. **Closed 2026-08-06** with `M6-12b`, the last open child. `test_strategy_observation.py` covers the scent-driven shapes end to end; `test_contradiction.py` covers the verbal one |
| M6-12a | Test with no scent and no hint | DONE | P1 | A uniform belief still yields a legal action. An empty observation leaves belief uniform and the pipeline returns a member of `Action`, never an error |
| M6-12b | Test with contradictory scent and hint | DONE | P1 | The physical evidence wins. `test_contradiction.py`, 12 tests. Both clauses of `:508` ("**must reduce their trust level and update their map**") asserted separately, and `:1020`'s verb pinned exactly: the pursuer *continues*, so the target under a lie is **identical** to the target having heard nothing. **Probing showed the dominance is structural, not a trust effect** — a `0.04` trace beats a lie held at complete trust, because a located peak concentrates likelihood where a bearing spreads it. The two headline tests would therefore pass with trust disabled, so `test_a_hint_decides_only_what_the_scent_leaves_open` pins the other half: on a **tie** between two equal peaks the hint decides, which is what keeps the verbal layer from being dead code. Ordering is lexicographic, as everywhere else (`M6-04`) |
| M6-12c | Test with a saturated scent field | DONE | P1 | No overflow, no division by zero. Every cell at max scent yields a valid, normalised belief (sums to 1) and a legal action |
| M6-12d | Test with the Thief adjacent and with the Thief far | DONE | P1 | Both produce sane, legal, distinct choices. Adjacent vs far scent give **different** `belief_target`s (the exact source cell) and both resolve to legal actions |
| M6-12e | Test that repeated runs are byte-identical | DONE | P0 | Determinism is a submission property, not an accident. The same observation yields the same action **and** byte-identical belief probabilities across two independent runs |
| M6-13 | Benchmark the per-turn decision cost | DONE | P1 | Belief update plus policy stays well inside the response timeout. **Started 2026-08-05** (`scripts/bench_decision.py`): the measurement (`M6-13a`) is DONE; the parent stays open on `M6-13b`, recording the number into the M9 research evidence, which is a later phase |
| M6-13a | Measure worst-case belief update time | DONE | P1 | Measured at the negotiated grid size. `scripts/bench_decision.py` times the real path on the deliberate worst case — a **saturated** field, argmax at the far corner, an **open board** (the BFS's true worst case, since barriers only shrink the reachable set). Measured: **1.3 ms at the 7×7 floor** (belief update alone 0.04 ms), 2.5 ms at 10×10, and **437 ms at 100×100** (100× the book's largest illustration) — still **69× inside** the 30 s timeout `[AF-t19]`. Guarded by `test_decision_cost.py`: deterministic `O(grid²)`-shape checks plus one loose 5 s ceiling that only a super-polynomial regression could trip |
| M6-13b | Record the measurement in the research evidence | DONE | P2 | Feeds `M9-06` and the computational-fairness claim. The number exists (`M6-13a`, logged in `PROMPT_LOG` P-049); the formal recording waits for the M9 research-evidence artifact rather than fabricating it a phase early |
| M6-14 | Document the perception and strategy layers | DEFERRED | P2 | `PRD_scent_belief.md` and `PRD_strategy.md` match the built behaviour |
| M6-14a | Document the belief update rule and its trust factor | DEFERRED | P2 | Formula, inputs, and normalisation |
| M6-14b | Document the locked scent model and its hash | DEFERRED | P1 | The exact bytes that were locked `[AE-23]` |
| M6-15 | Offer the scent implementation to the opponent for parity | DEFERRED | P2 | The book recommends sharing the scent source so both run identical logic `[book §6]` |
| M6-16 | Keep the verbal layer strictly optional | DONE | P1 | Disabling every provider still produces a complete, legal game. `test_verbal_optional.py` (12 tests) drives `generate_hint` with no provider and with five distinct failure modes; every path yields a validated hint `[:1565]` |
| M6-16a | Prove a full series runs at zero tokens | DONE | P1 | Template provider only `[AF-t21]`. `test_a_full_six_sub_game_series_runs_at_zero_tokens` produces all 210 hints of a counted six-sub-game series with **no provider at all** — no account, no network, no token. `:1565`: the template is "the default… zero tokens, no network dependency… the recommended path" |
| M6-16b | Prove a provider outage never forfeits a turn | DONE | P0 | Fallback is automatic and silent to the opponent. Five failure modes pinned — raises, times out, returns a non-string, leaks coordinates, exceeds the word limit — each degrading to the template. `test_the_fallback_is_indistinguishable_from_an_ordinary_hint` proves the degraded hint is **byte-identical** to the healthy one, so an opponent cannot read our outage off the wire and gain a signal we never agreed to send |
| M6-17 | Record the belief model in the academic report | DONE | P1 | Bayes update, trust factor, and the Manhattan objective `[AE-42]`. README §Report now carries the belief model **and** the `M6-20` measurement that justifies it, including the oracle bound and the informativeness caveat |
| M6-18 | Prove belief and scent never leak into the wire beyond the agreed fields | DONE | P0 | Internal certainty is private; only the agreed observation crosses. `test_belief_privacy.py`: the public turn schema's property roster is pinned and carries no belief/certainty/probability/trust member; the existing `not:` guard against `position`/`move`/`nonce`/`intent`/`verdict` is pinned so it cannot erode; the sealed record's secret-key roster is pinned; and a walk over `protocol/` and `adapters/` proves the wire layers import no inference module, so belief cannot reach a message even indirectly through an existing field. **The guard was verified to bite** — injecting `from strategy.belief import Belief` into `scent_wire.py` fails it. Deliberately *not* over-reaching: `strategy.scent`/`scent_field` stay outside the ban, because emitting scent is an obligation (`AE-23`, `:895`), not a leak. **Scope note:** rules 8 and 9 are narrower than usually quoted — verified verbatim at `:3311-3312`, they govern the **live user interface**, which is M8. The wire constraint comes from Zero-Trust instead (`:705`: a backdoor "through which one agent might see the local truth of its rival") |
| M6-19 | Add regression vectors for the scent field | DEFERRED | P1 | Stored expected fields guard against silent physics drift |
| M6-20 | Measure strategy quality against the baseline | DONE | P1 | Belief-driven pursuit must beat the blind baseline or be reverted. **Measured 2026-08-06** (`scripts/compare_strategies.py`, pinned by `test_strategy_quality.py`): over 30 seeds at the negotiated 7×7 fixture, mean Cop score **19.5 vs 9.0** and capture rate **96.7% vs 26.7%**, catching in **12.5 turns vs 32.4**. Stable across sample size (belief 99.0% at n=100, 99.7% at n=300). It stands |
| M6-20a | Define the comparison protocol | DONE | P1 | Fixed seeds, fixed opponent policy, repeated runs. Seeds 0–29; one opponent for every arm — a seeded random legal walk that **does not react to the Cop**, so for a given seed every arm faces the *identical* Thief trajectory and the result is a **paired** comparison, not two averages. The Cop observes the real channel (the Thief's `ScentField`, read as the 5×5 window `M6-08` puts on the wire); only the `oracle` arm sees the true cell. Separate RNG streams per actor. The book specifies **no** run count, seed policy, significance test or baseline (`:3115` requires only "empirical evidence for their success"), so the protocol is ours and is stated in full in `PRD_strategy.md` |
| M6-20b | Record the result either way | DONE | P1 | A negative result is evidence, not a failure to hide — and the result is positive, recorded with the caveats that make it honest. Paired outcome **21–0**: belief captured on 21 seeds the blind Cop lost and lost none it won. Against an `oracle` Cop that reads the true cell (**not a legal agent**, included as the ceiling), belief closes **95.5%** of the available gap. The caveat is stated in the report: the book's scent channel is highly informative — a 5×5 window peaks at the emitter's own cell — so belief lands near the oracle partly because the observation is generous, not solely because the policy is good |

---

## M7 — Series orchestration, artifacts, gatekeeper and reporting

*Gate: one complete local series produces accepted audit artifacts.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M7-01 | Implement six-sub-game series orchestration | DONE | P1 | `orchestration/series.py`. `run_series` plays all six on the ruled schedule with `play` injected, so it orchestrates without owning transport, strategy or artifacts |
| M7-01a | Run six sub-games under one series identity | DONE | P1 | One `MatchIdentity` across the series: `artifact_names` yields **2 per-series + 2 per-sub-game = 14** filenames, all sharing one `game_uid` (`M7-02c`). Each sub-game is otherwise a fresh game -- own barrier quota, own scent field, own belief. Carrying belief across would mean our score in sub-game 4 depended on inference gathered while we were the *other role* |
| M7-01b | Implement the confirmed six-sub-game role schedule | DONE | P0 | `U-025`, closed 2026-07-31 on a coordinator-relayed lecturer answer: 1/3/5 natural, 2/4/6 swapped, Thief first. **Written out as constants, not computed.** A formula is one refactor away from silently disagreeing with the ruling, and a test pins the two sides are opposite in every sub-game -- the error a computed alternation makes silently |
| M7-01c | Aggregate cumulative series score | DONE | P1 | `SeriesResult.cumulative` sums the six lines |
| M7-01d | Apply the tie award on a cumulative tie | DONE | P1 | A cumulative tie awards the `tie_score` to each side while keeping the raw totals visible. `:2042`: "no meeting remains without a decision" -- a draw is decided, not undecided |
| M7-02 | Finalize artifact identity and generate declaration/per-game config artifacts | DEFERRED | P1 | Accepted `game_id`/UUID protocol, schemas, logical links, and resolved filenames validate |
| M7-02a | Emit `declaration_<game_id>.json` | DONE | P1 | `declaration_<game_id>.json`, written atomically by `reporting.emit` with the lock folded in as `declaration_lock` |
| M7-02b | Emit `config_<game_id>_g<NN>.json` | DONE | P1 | `config_<game_id>_g<NN>.json`, built from the negotiated game object and written in the same pre-play step, so the config on disk describes the match about to be played |
| M7-02c | Share one `game_uid` across all four artifacts | DONE | P1 | `MatchIdentity(game_id, game_uid)` is the single identity every filename derives from, validated once at construction — `M7-14e` refuses a mismatched set after the fact, but the cheaper guarantee is that the builders were never able to disagree. `game_id` is refused unless filename-safe, since it is negotiated with an opponent and then becomes part of a path |
| M7-03 | Generate game logs and final result | DONE | P1 | `reporting/result_artifact.py` completes the four builders. Audit links, commit hash, tokens and scores are consistent by construction: the cumulative block is **summed from** the per-sub-game lines rather than passed in, so the two cannot disagree |
| M7-03a | Emit `log_<game_id>_g<NN>.json` with full commit-reveal | DONE | P1 | `build_log` + `reveal_log` produce it; feeding real per-turn records from the turn loop is the consumer and follows |
| M7-03b | Emit `result_<game_id>.json` as the emailed report | DONE | P0 | `build_result` produces the emailed report -- per-group blocks, per-sub-game score lines and the cumulative `final_result`. `:2241`: "the score of each group in all games and the cumulative result". **An unagreed result is refused at build time**: rule 35 (Mandatory) scores a conflicting report 0 for **both** teams, while `:2584` says a side that does not report merely "will not be credited" -- so sending a contradictory report is strictly worse than sending none, and the asymmetry is encoded rather than commented |
| M7-03c | Carry four repository links in the result artifact | DONE | P0 | Exactly four links, refused otherwise -- rule 49 (Mandatory), "four links in the JSON files of the two teams". Three means one side's submission is wrong, and failing here beats filing a report the lecturer cannot trace back to the code |
| M7-03d | Carry the per-game commit hash and total tokens | DONE | P0 | `commit_hash` -- rule 53 (Mandatory), code may change between games so a result that does not say *which* code played cannot be reproduced. Tokens **per sub-game and for the series**, because rule 54 asks for the total "for the game **and in the sequence**": two numbers, not one |
| M7-04 | Implement API Gatekeeper and token-bucket/FIFO limits | DONE | P1 | `services/send_gates.py` + `send_pipeline.py`. Appendix F table 19 `Minimum` values honoured (rate 30, queue depth 100, concurrency 2) with backpressure rather than rejection, alongside the pre-existing `services/gatekeeper` |
| M7-04a | Route every external call through one gatekeeper | DONE | P0 | `SendPipeline.send` takes the transmitting callable rather than importing one, so this layer **cannot name Gmail** — a module that cannot name the API cannot bypass the gates to reach it. A refused send never calls the transmitter |
| M7-04b | Implement the token bucket | DONE | P0 | **A real token bucket, and this was a genuine gap.** The existing `services/gatekeeper` is a *sliding window* — it drops timestamps older than 60s and counts what remains. Rule 28 (Mandatory) requires "a rate-limiter based on asynchronous **tokens**", and `:2085` says why: a bucket prevents the **bursts** that trigger an immediate provider block. A window caps a rate; a bucket caps a burst and then refills. `tokens ← min(C, tokens + r·Δt)`, allow iff `tokens ≥ 1`, with the `min(C, …)` clause tested separately — without it an idle agent banks an unbounded burst |
| M7-04c | Queue overflow rather than rejecting | DONE | P1 | Already satisfied by `services/gatekeeper`: FIFO to `queue_depth` then backpressure; `submit` returns **queued, not rejected** and nothing is discarded |
| M7-04d | Read every limit from configuration | DONE | P0 | `SendPipeline.from_match` reads `requests_per_minute` from the signed match object. Table 19 makes 30 a `Minimum`, so a negotiated higher value is **honoured rather than clamped back down** — clamping a minimum is the classic misreading |
| M7-05 | Implement signed final JSON reporting adapter | DONE | P1 | `reporting/gmail_message.py` + `send_report.py`. Attachment-only delivery, send-only scope, credential files already git-ignored, and no Google library imported anywhere -- `transmit` is injected, so this layer cannot reach the API on its own |
| M7-05a | Restrict the OAuth scope to `gmail.send` | DONE | P0 | `REQUIRED_SCOPE` is `.../auth/gmail.send`, asserted to contain neither `readonly` nor `modify`. Rule 30 (Mandatory), sanction "security breach that will lead to code disqualification" |
| M7-05b | Keep `credentials.json` and `token.json` git-ignored | DONE | P0 | **Already satisfied; verified rather than added.** `.gitignore` carries `credentials.json`, `token.json`, `*credentials*.json`, `.env` and `.env.*` with an `!.env-example` exception, all present before any commit that could have carried one `[AE-39]` `[AE-40]` |
| M7-05c | Send JSON as an attachment only | DONE | P0 | The artifact rides as an `application/json` attachment and the body is a fixed pointer carrying no report data -- tested by asserting the result's own values do **not** appear in the body. Rule 34 (Prohibited): free text "will be rejected and result in a zero score", so a helpful covering note *is* the violation |
| M7-05d | Send to the confirmed reporting address | DONE | P0 | `rmisegal+uoh26finalgame@gmail.com`, on lecturer answer `AF-020`. **The book prints both spellings** -- `:3040` has `rmisegal`, `:3605-3606` have `rimesegal` -- so this is a confirmed source inconsistency (`C-004`) rather than a choice. Not read from the shared config: a peer able to move our reporting destination could silence it |
| M7-05e | Back off on HTTP 429 rather than retrying immediately | DONE | P0 | Backoff on 429 only, doubling from the Appendix F table 19 `Minimum` of 5s. A non-429 is **not** retried -- retrying a 400 spends quota on a request that will fail identically |
| M7-06 | Validate series audit and mutual-result agreement | DONE | P0 | `orchestration/settlement.py`. Four settled states, each with its own remedy: `AGREED`, `CONFLICT` (rule 35, 0/0 both), `AUDIT_FAILED` (rule 19, 0 for the falsifying group) and `UNANSWERED`. One generic "not agreed" would send all three down the same wrong path |
| M7-06a | Run the full mutual audit before agreeing a result | DONE | P0 | `audit_series` runs `audit_reveal` over **every** sub-game and stops at the first mismatch, naming it. Rule 19 calls a mismatch an "iron rule", so there is nothing to weigh once one is found. **An empty series does not pass** — auditing nothing must not read as auditing successfully, which is the commonest way an audit gate is bypassed |
| M7-06b | Send both reports independently | DONE | P0 | Each side sends its own report; `ReportSender` is per-peer and keyed on `game_id`. `:2584`: a side that does not send "will not be credited" even if it won |
| M7-06c | Treat conflicting reports as 0/0 for both | DONE | P0 | `require_reportable` refuses a `CONFLICT` naming rule 35's "0 for BOTH teams". Sending ours is not a way to win the argument — it is how the argument costs us the game |
| M7-07 | Run a complete six-sub-game stub series | DONE | P0 | `test_series_run.py` drives the whole stack: schedule → six per-sub-game configs, each schema-validated and written → `check_one_identity` across the set → settlement → result artifact. **The first row that exercises everything together rather than in isolation**, which is why it ran before the M7 mirror to the Thief: a design worth copying should be one that has actually run |
| M7-08 | Implement the Quota Manager and DOS Detector gates | DONE | P0 | All three gates in the book's order. `:2096`: "Outgoing report → Quota Manager → Token Bucket → DOS Detector → Gmail API", with three distinct outcomes (`:2098`) because they differ in remedy — *try tomorrow*, *try shortly*, *the code is wrong* |
| M7-08a | Implement the daily quota counter | DONE | P0 | `QuotaManager`, a per-day counter that rolls over. `:2083`: "the **final line before account blocking**: if the quota is exhausted, no further requests are sent" |
| M7-08b | Implement the DOS detector and pipeline lock | DONE | P0 | `DosDetector` locks the pipeline on a burst. `:2087` says what it is *for* — "a bug or an infinite loop **in the agent's code**", not a hostile peer — which is why the lock is deliberately **not self-clearing**: a detector that reset itself would let the same loop resume the moment it briefly looked calm |
| M7-08c | Prove fail-fast ordering across the three gates | DONE | P0 | Fail-fast, and it is a **correctness** requirement rather than an optimisation. Each gate has a side effect, so a later gate running after an earlier refusal corrupts the counters the gates protect. Two tests pin the consequences: a quota rejection must not consume a token (or a send that never went out would throttle tomorrow), and a token-blocked send must not register in the DOS window (or a legitimately throttled burst would look like a runaway loop and lock the pipeline for the wrong reason). A transmitter that **raises** still counts, because a gate that only counted successes would let a failing loop retry without limit |
| M7-09 | Declare games already played against each opponent | DEFERRED | P0 | Appendix E rules 37/38: every game start carries an accurate count of prior counted games against that opponent, derived from emitted result artifacts rather than hand-entered. A false declaration is absolute disqualification, so the count is reproducible from the artifact set |
| M7-09a | Derive the count from emitted result artifacts | DEFERRED | P0 | No hand-entered figure can enter the declaration |
| M7-09b | Exclude warm-up games from the counted total | DEFERRED | P1 | `[AE-52]`; warm-ups are permitted but uncounted |
| M7-10 | Attach every game's configuration artifact to the repository | DEFERRED | P1 | Appendix F.2 items 3 and 4: each game's configuration artifact is named from its `game_id` and committed to the repository, so any past game's exact configuration remains retrievable |
| M7-10a | Commit each game's config under a `game_id`-derived name | DEFERRED | P1 | Artifacts from different games cannot collide |
| M7-10b | Prove any past game's config is retrievable from the repo | DEFERRED | P1 | A retrieval test walks the committed set |
| M7-11 | Account for LLM tokens across a series | DEFERRED | P1 | Per-game and per-series totals are counted, sealed at Step-0, and reported `[AE-54]` |
| M7-12 | Emit warm-up games as uncounted | DEFERRED | P1 | A warm-up produces artifacts but never enters the counted total `[AE-52]` |
| M7-13 | Persist artifacts atomically | DEFERRED | P2 | A crash mid-write cannot leave a half-written artifact that later fails audit |
| M7-14 | Validate every emitted artifact against its schema | DONE | P0 | `reporting/validate.validated_write` sits **between building and writing**, and is what `play_match` calls for the config. The row's condition is about placement -- a validator living only in the test suite proves the artifacts were valid on a developer's machine, not that a hand-edited file never reaches a disk someone can email it from |
| M7-14a | Validate the declaration artifact | DEFERRED | P0 | **Blocked on a schema, not on code.** `validate_artifact` refuses any artifact kind with no controlled schema rather than waving it through, so "validated" never quietly means "unchecked". The bundle carries a schema for the per-sub-game config only; authoring the declaration, log and result schemas is a contract change and its own row. Required identity, hardware, and timing fields present |
| M7-14b | Validate the config artifact | DONE | P0 | The config validates against `shared_contract/schemas/per-subgame-config.schema.json` on the live emit path; an invalid one raises and **leaves no file behind** |
| M7-14c | Validate the log artifact | DEFERRED | P0 | **Blocked on a schema, not on code.** `validate_artifact` refuses any artifact kind with no controlled schema rather than waving it through, so "validated" never quietly means "unchecked". The bundle carries a schema for the per-sub-game config only; authoring the declaration, log and result schemas is a contract change and its own row. Every step carries commitment, nonce, move, and hint |
| M7-14d | Validate the result artifact | DEFERRED | P0 | **Blocked on a schema, not on code.** `validate_artifact` refuses any artifact kind with no controlled schema rather than waving it through, so "validated" never quietly means "unchecked". The bundle carries a schema for the per-sub-game config only; authoring the declaration, log and result schemas is a contract change and its own row. Scores, four links, commit hash, and token totals present |
| M7-14e | Reject an artifact set whose `game_uid` values disagree | DONE | P0 | `check_one_identity` compares artifacts to each other -- the check no per-file schema can make, since each file is individually valid and they simply belong to different matches. A re-run config beside yesterday's log is what an auditor notices and we would not |
| M7-15 | Implement the OAuth setup path | DEFERRED | P1 | First run creates a token; later runs refresh without human action |
| M7-15a | Run the consent flow once and store the token locally | DEFERRED | P1 | `token.json` is created, never committed `[book App. A]` |
| M7-15b | Refresh the access token automatically | DEFERRED | P1 | The refresh token gives months of autonomy |
| M7-15c | Fail closed when no credential is present | DONE | P0 | `require_credential` raises rather than skipping. A missing `token.json` degrading into "skipped the report" is indistinguishable from success in a log that only records errors |
| M7-15d | Document the five setup steps for a fresh machine | DEFERRED | P2 | Reproducible by a teammate `[G§2.1]` |
| M7-16 | Compose the report email | DONE | P1 | `build_report_message` assembles the MIME message; `encoded_message` returns the base64url `raw` body |
| M7-16a | Attach the result artifact as a file | DONE | P0 | Attachment read back **out of the assembled message** rather than trusting the object that went in -- the only way to know it survived encoding intact |
| M7-16b | Use a deterministic subject naming the game | DONE | P1 | `[<team_code>] final-result <game_id>`, generated rather than written. Rule 45 (Mandatory) ties **automatic report assignment** to the 8-character code, and a per-game hand-written subject would sort inconsistently the first time someone was in a hurry. A code that is not exactly 8 characters is refused |
| M7-16c | Base64url-encode and send through the API | DONE | P1 | `base64.urlsafe_b64encode` of the raw MIME, shaped for `users().messages().send` |
| M7-17 | Prove reporting under failure | DONE | P0 | `ReportSender` covers all three failure modes; no path loses a report silently |
| M7-17a | Retry after a 429 with backoff | DONE | P0 | Retries only on 429, sleeping `5s, 10s, …`. Appendix F table 19 makes the delay a `Minimum` of 5s and attempts a `Minimum` of 3 -- **floors to honour, not values to tune down**, and a constructor below either is refused |
| M7-17b | Surface a permanently failed send loudly | DONE | P0 | Raises `ReportNotSentError` naming the game and the last error. Rule 32 (Mandatory): "absence of reporting **disqualifies the game points**", so there is no useful fallback -- a caller that could quietly continue would convert a lost game into a silent one |
| M7-17c | Never send twice for one game | DONE | P0 | Keyed on `game_id` and not resettable through the API. Rule 35: a conflicting report scores **0 for BOTH teams**, and two sends for one game is the easiest way to produce one by accident |
| M7-18 | Implement result agreement with the opponent | DONE | P0 | Both sides converge before either reports, and `build_result` now accepts a `Settlement` so `mutual_agreement` can be **earned** rather than asserted. Previously it was a bool a caller passed, which meant a report could claim an agreement that never happened |
| M7-18a | Exchange the computed outcome after the audit | DONE | P0 | `agree(audit, ours, theirs)` **takes the audit as its first argument**, so agreement cannot be reached without one. Rule 36 makes the audit "a mandatory condition before agreement on the JSON result" — a precondition a caller can forget is not a precondition |
| M7-18b | Detect and record a disagreement | DONE | P0 | A conflict keeps **both** claims side by side in `settlement_record`, for the log's `mutual_agreement` block. The temptation is to adopt their number to keep the peace; that files a result we do not believe and destroys the evidence an auditor needs. **Silence is its own state**, not agreement — treating a missing reply as consent would let a crashed peer decide our report |
| M7-18c | Refuse to report an unagreed result | DONE | P0 | `require_reportable` is the only gate to reporting, and the audit-failure message differs deliberately: their forgery is *their* rule 19 loss, and firing off our own contradicting report would convert it into a **shared** rule 35 loss. A test asserts the three refusals carry three distinct messages |
| M7-19 | Implement series-level score aggregation evidence | DEFERRED | P1 | The cumulative figure is reproducible from the artifact set |
| M7-19a | Recompute the series total from stored artifacts | DEFERRED | P1 | No in-memory-only total is trusted |
| M7-19b | Apply the diversity reward for a new opponent | DEFERRED | P1 | `[AF-t18]`; a repeat opponent adds nothing |
| M7-20 | Run a full local series rehearsal before any counted game | DONE | P0 | `tests/integration/test_series_rehearsal.py` + `_tampered` + `_invariants`. A clean six-sub-game run emits all 12 per-sub-game files, settles, and reports; identity consistency and schedule adherence are then checked across that **real run** rather than a constructed pair. Run against the `X-06`-corrected shapes -- rehearsing before that would have produced a green result making the wrong shape look settled |
| M7-20a | Rehearse with a deliberately failing sub-game | DONE | P0 | A technical loss in sub-game 3 still writes its config and log, the log records the outcome, the file count is unchanged, and the series still settles and reports with 0/0 for that sub-game. **The sub-game that goes wrong is when the evidence matters most, and when a happy-path pipeline quietly stops producing it** |
| M7-20b | Rehearse with a tampered audit | DONE | P0 | A forged payload in sub-game 4 is detected and named, and `require_reportable` then **refuses to report** -- two separate behaviours. Rule 19 costs *them* the sub-game; filing our own contradicting report over the top would invoke rule 35 and cost us **both** the game. The artifacts stay on disk either way, because a failed audit is evidence rather than a reason to withhold it |
| M7-21 | Document the reporting pipeline | DEFERRED | P2 | `PRD_gatekeeper_reporting.md` matches the built gates and flow |
| M7-22 | Emit the declaration before the first move of each game | DONE | P0 | The declaration is now **written to disk inside `play_match`, immediately after it is locked and before the first turn is sent**. Proven by timing rather than presence: a spy records whether the file existed at each outbound turn, and every one must see it already there. A declaration emitted at the end could have been edited to suit the result, which is the whole thing locking it beforehand rules out |
| M7-22a | Include both groups and their members | DONE | P1 | Both groups and their members ride in `groups`, each entry projected from the negotiated identity block |
| M7-22b | Include both repository links per group | DONE | P0 | `links` collects every repo URL across both groups — rule 49 (Mandatory): "four links in the JSON files of the two teams" |
| M7-22c | Include the MCP addresses in use | DONE | P1 | `groups[].mcp_servers`, required by `:2229` ("addresses of the MCP server"). **A URL carrying a credential is refused**: the declaration is committed and emailed, and rule 39 (Prohibited) forbids pushing secrets, sanction "severe security failure and project failure". The guard cost two bug-fixes to get right — a key-bearing query parameter slipped through a pattern anchored at the leading `?`, and `http://127.0.0.1:8000` was then refused because the port colon read as `user:pass`. Both directions are pinned |
| M7-22d | Include the hardware and model declaration | DONE | P0 | `hardware` and `llm_model`, required by `:2229` and rule 24 (Mandatory, "perform a cryptographic hardware declaration before the start of the game", sanction "denial of eligibility for computational bonuses"). **Read from the negotiated identity block, not passed separately** — `spec` and `llm_model` are already two of its seven members, and a second source for the same fact is a second thing that can disagree |
| M7-22e | Include the agreed token limit and game times | DONE | P1 | `max_tokens_per_game`, `game_started_at`, `game_ended_at` (null until the post-game re-lock) and `timezone` |
| M7-23 | Bind the config artifact to the negotiated match | DONE | P0 | `reporting/config_artifact.build_config` takes the **negotiated game object** and reads every section from it, so the artifact and its hash cannot describe different documents. The row's condition — "the one actually played, not a template" — is tested by changing an agreed value and asserting the artifact follows, not by comparing against a constant. Validates against `shared_contract/schemas/per-subgame-config.schema.json` |
| M7-23a | Include every quantitative parameter | DONE | P0 | All six Appendix F sections (`board_and_agents`, `movement_and_barriers`, `scoring`, `pheromones`, `network_and_league`, `rate_limiter_gatekeeper`), named explicitly so a section added later is a visible decision rather than a silent inclusion or omission. Asserted against the source game object |
| M7-23b | Include the cryptographic locks | DONE | P0 | Both locks. `config_sha256` over the whole agreed object — rule 11 (Mandatory), "identical, bit-for-bit", sanction "disqualification… for lack of symmetry". `scent_model_sha256` — rule 23 (Mandatory), "lock the cryptographic hash of the scent model before the start of the game. Sanction: **deviation from the formula cancels the game**". Top-level rather than buried in `config`, so an auditor sees both without parsing a subtree; the schema leaves top-level open so this needed no contract revision |
| M7-24 | Make the log artifact sufficient for an independent audit | DONE | P0 | `reporting/log_artifact.py`. The binding test is the row's own condition -- "a third party can re-verify **without our code**" -- so it recomputes every commitment from the emitted file alone with `hashlib`, exactly the procedure `:1690` gives the replay viewer, and asserts a tampered payload fails that same recomputation |
| M7-24a | Record each step's commitment and revealed payload | DONE | P0 | Each step records `step`/`sender`/`commit`/`move`/`hint`/`intent`, and the final audit section pairs every commitment with its `nonce` and `payload`. A reveal count that disagrees with the step count is refused, as is a reveal for a step never played |
| M7-24b | Record nonces only in the final audit section | DONE | P0 | **Made unrepresentable rather than observed.** `build_log` refuses a step carrying `nonce` or `payload`; `reveal_log` is the only way they enter. Rule 18 (Mandatory) -- "keep the Nonce secret until the end of the game", sanction "disqualification due to risk of dictionary attack" -- is a rule about *when a byte exists*, and the finished log is byte-identical whether the nonces were written at the end or leaked at step one. No inspection of the artifact could catch it; only refusing to build the intermediate state can |
| M7-24c | Record the hint and intent per step | DONE | P1 | `hint` and `intent` per step. A hint without its bluff flag cannot be judged -- there would be no way to tell a bluff from a mistake |
| M7-25 | Keep artifact emission independent of transport health | DONE | P0 | `reporting/emit.write_artifact` takes a directory and an object — no socket, no client, no peer state, pinned by a signature test. Writes to a temporary file **in the same directory** then `os.replace`, so the visible file is either the old one or the complete new one, never a prefix; same-directory matters because `os.replace` is only atomic within a filesystem. A half-written artifact is indistinguishable from a tampered one during rule 19's audit, whose sanction is "score of 0 for the falsifying group" |
| M7-26 | Version the artifact schemas | DEFERRED | P1 | A schema change is visible, not silent `[G§8.1]` |
| M7-27 | Verify every emitted artifact is committed | DEFERRED | P1 | Appendix F.2 item 4; nothing exists only on a local disk |

---

## M8 — GUI, replay, interoperability and security hardening

*Gate: remote rehearsal and evidence screenshots pass.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M8-01 | Implement local-truth live GUI | DONE | P1 | No objective opponent state is exposed |
| M8-01a | Render the belief heatmap | DONE | P1 | Deeper colour means higher probability `[PRD-gui]` `[ADR-009]` |
| M8-01b | Render the turn banner | DONE | P1 | Green `YOUR TURN`, grey `LOCKED` after commit |
| M8-01c | Lock input while the banner is grey | DONE | P1 | Out-of-turn input is ignored, not queued |
| M8-01d | Prove the objective board is never renderable | DONE | P0 | `[AE-8]` `[AE-9]`; a view-model test asserts no opponent-truth field |
| M8-02 | Implement replay verifier and tamper view | DONE | P1 | `Verified OK` and `TAMPERED` paths are demonstrable |
| M8-02a | Load a saved match log and step forward/back | DONE | P1 | `[AE-20]` mandatory deliverable `[PRD-replay]` |
| M8-02b | Recompute every step's hash and compare | DEFERRED | P0 | Uses the M4 construction, not the book's chapter-7 sketch |
| M8-02c | Void the whole match on the first mismatch | DONE | P0 | A single tampered step yields `TAMPERED` for the match |
| M8-02d | Record why the book's chapter-7 verifier is not used | DONE | P1 | Book p. 74 computes `SHA256("{nonce}|{move}")`, which cannot verify a chapter-5 commitment. Disclosed under the p. 5 contradiction clause |
| M8-02e | Document the replay UI workflow and states | DONE | P2 | Screens, controls, and both verdict states described `[G§10.2]` |
| M8-03 | Run neutral unknown-opponent interoperability suite | DEFERRED | P0 | Both proposal/acceptance directions pass remotely |
| M8-03a | Rehearse against a stub that shares no source with this repo | DEFERRED | P0 | Independently authored; imports no project module |
| M8-03b | Prove both proposal and acceptance directions | DEFERRED | P0 | Neither direction needs a profile file edited |
| M8-03c | Rehearse against a real classmate agent before the counted league | DEFERRED | P0 | A warm-up game is permitted and uncounted `[AE-52]` |
| M8-04 | Run fault, security, secret, and resource hardening | IN PROGRESS | P0 | Failure matrix and abuse tests pass |
| M8-04c | Bound memory and queue growth under sustained load | IN PROGRESS | P1 | No unbounded queue or leak under a long series |
| M8-04d | Apply Nielsen usability heuristics to both UIs | DEFERRED | P2 | Visibility of status, error prevention, recovery `[G§10.1]` |
| M8-04a | Inject crash, timeout, mismatch, and tamper faults | DONE | P0 | Each produces a defined, logged outcome |
| M8-04b | Validate every inbound field before use | IN PROGRESS | P0 | Malformed peer input cannot reach domain code `[G§6.3]` |
| M8-05 | Capture required GUI/replay evidence | DONE | P1 | Submission-quality screenshots are reproducible |
| M8-05a | Capture the belief-map GUI screenshot | DONE | P1 | Required README content `[AE-42]` |
| M8-05b | Capture the replay `Verified OK` screenshot | DONE | P1 | Required README content `[AE-42]` |
| M8-05c | Capture a `TAMPERED` screenshot from a deliberately corrupted log | DONE | P2 | Demonstrates the detection path, not just the happy path |
| M8-05d | Make every screenshot reproducible from a stored fixture | DONE | P1 | A grader can regenerate them |
| M8-06 | Build the GUI view-model behind the SDK | DONE | P1 | No widget touches domain or protocol code directly `[G§4.1]` |
| M8-06a | Expose a read-only snapshot for rendering | DONE | P1 | The view cannot mutate game state |
| M8-06b | Update the view on state change rather than polling | DONE | P2 | Redraw follows the phase machine |
| M8-06c | Keep the GUI out of coverage requirements | DONE | P2 | Omitted per the guidelines' coverage config `[G§6.2]` |
| M8-07 | Render the board and own position | DONE | P1 | Own cell, disclosed barriers, and turn number are visible |
| M8-07a | Render disclosed barriers only | DONE | P0 | A barrier appears only once disclosed `[AE-15]` |
| M8-07b | Render received hints as text | DONE | P2 | The verbal channel is visible to the operator |
| M8-07c | Show the current score and step count | DONE | P2 | Operator can see progress toward the threshold |
| M8-08 | Implement replay navigation | DONE | P1 | Step forward, step back, and jump to a step |
| M8-08a | Recompute verification on every navigation | DONE | P0 | The verdict is derived, never cached from load time |
| M8-08b | Show the per-step verdict alongside the board | DONE | P1 | Operator sees where a match failed |
| M8-08c | Load a malformed log without crashing | DONE | P1 | Corrupt input yields a clear error, not a stack trace |
| M8-08d | Detect a reordered log | DONE | P0 | Step sequence is validated, not assumed |
| M8-09 | Run the security review | IN PROGRESS | P0 | Secrets, identity, input validation, and dependencies all reviewed |
| M8-09a | Confirm no secret is readable from any artifact | DONE | P0 | Artifacts are shared; secrets must not travel in them `[AE-39]` |
| M8-09b | Confirm no private field crosses the wire | IN PROGRESS | P0 | Leakage vector per private field class |
| M8-09c | Review third-party dependencies and pin them | DONE | P1 | `uv.lock` is authoritative `[G§8.4]` |
| M8-09d | Confirm the LLM path cannot influence a move | DONE | P0 | Even with a provider enabled `[AE-25]` |
| M8-10 | Run the resource and endurance pass | DEFERRED | P1 | A full six-sub-game series runs without degradation |
| M8-10a | Run a long series and watch memory | DEFERRED | P1 | No unbounded growth across sub-games |
| M8-10b | Confirm clean shutdown releases every resource | DEFERRED | P1 | Sockets, files, and threads all closed |
| M8-11 | Document both interfaces | DONE | P2 | Screens, states, and workflows described `[G§10.2]` |
| M8-11a | Document the live GUI workflow | DONE | P2 | Turn banner states and what each means |
| M8-11b | Document accessibility considerations | DONE | P2 | Colour is not the only signal `[G§10.2]` |
| M8-12 | Prove the replay app on a foreign log | DONE | P0 | It verifies a log this peer did not write |
| M8-12a | Verify an opponent-produced log | DONE | P0 | The audit is mutual; both logs must verify `[AE-36]` |
| M8-12b | Detect a foreign log that was tampered | DONE | P0 | The detection path is not self-only |
| M8-13 | Rehearse the full failure matrix end to end | DONE | P0 | Every fault class has an observed outcome, not a predicted one |
| M8-13a | Rehearse an opponent crash mid-series | DONE | P0 | The series still produces artifacts |
| M8-13b | Rehearse a tunnel drop mid-turn | DONE | P0 | Terminal outcome is defined, not a hang |
| M8-13c | Rehearse a config mismatch at negotiation | DONE | P0 | The match is refused before play `[AE-11]` |
| M8-14 | Freeze the interoperability profile before the counted league | DEFERRED | P0 | No wire change after the first counted game without a coordinator decision |

---

## M9 — League evidence, submission and release

*Gate: submission checklist and current Moodle instructions satisfied.*

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M9-01 | Run counted league series against required opponents | DEFERRED | P0 | Current official minimums and declarations are satisfied |
| M9-01a | Play at least two counted games against at least two groups | DEFERRED | P0 | `[AE-31]` `[AF-t18]`; below the minimum scores zero |
| M9-01b | Count only one scoring game per opponent | DEFERRED | P0 | `[AE-52]`; repeats add nothing |
| M9-01c | Secure opponent scheduling early | DEFERRED | P0 | External dependency on other teams; longest lead time in the project |
| M9-02 | Complete six-section academic README report | DEFERRED | P0 | Model, protocol, strategy, results, screenshots, and links are present |
| M9-02a | Describe the Dec-POMDP model | DEFERRED | P0 | State space, observations, uncertainty `[AE-42]` |
| M9-02b | Discuss the FastMCP communication dilemma | DEFERRED | P0 | Queues, failures, orchestrator, gatekeeper |
| M9-02c | Describe the implemented strategy | DEFERRED | P0 | Heuristic, belief, and barrier policy |
| M9-02d | Include learning curves if RL is used | DEFERRED | P2 | Not applicable while the policy stays deterministic |
| M9-02e | Embed the GUI and replay screenshots | DEFERRED | P0 | From `M8-05a`/`M8-05b` |
| M9-02f | Cross-link the companion repository | DEFERRED | P0 | `[AE-49]` |
| M9-03 | Complete performance, token, and cost evidence | DEFERRED | P1 | Results derive from reproducible runs |
| M9-03a | Tabulate input/output tokens and cost per model | DEFERRED | P1 | `[G§11.1]` `[AE-54]` |
| M9-04 | Run final two-repository submission audit | DEFERRED | P0 | Access, secrets, reports, artifacts, and quality gates pass |
| M9-04a | Verify lecturer access to both repositories | DEFERRED | P0 | Public, or shared with `rmisegal@gmail.com` `[AE-49]` |
| M9-04b | Verify no secret exists anywhere in Git history | DEFERRED | P0 | `[AE-39]`; a secret committed once requires credential rotation |
| M9-05 | Create annotated release tag and submit | DEFERRED | P0 | Current Moodle tag/form/PDF instructions are followed |
| M9-05a | Push an annotated `v1.0-submission` tag | DEFERRED | P0 | `[AE-41]` |
| M9-05b | Fill the Moodle template without moving fields | DEFERRED | P0 | `[AE-43]`; save as PDF |
| M9-05c | Confirm each member submits separately | DEFERRED | P0 | `[AE-44]` |
| M9-05d | Use the eight-character team code | DEFERRED | P0 | `sharNamr`, confirmed 2026-07-28 `[AE-45]` |
| M9-05e | Provide the code-quality self-assessment | DEFERRED | P1 | `[AE-55]`; grades code quality only, never the league result |
| M9-06 | Complete parameter research and sensitivity analysis | DONE | P1 | Guidelines §9.1: systematic one-at-a-time experiments across the negotiable parameters, with the measured effect of each on match outcomes documented in tables |
| M9-06a | Sweep the negotiable board and movement parameters | DONE | P1 | Grid size, barrier quota, step limit, survival threshold |
| M9-06b | Sweep the scent parameters within their fixed bounds | DONE | P1 | Sensitivity to `ρ` and field size, noting both are `Fixed` for play |
| M9-06c | Record each parameter's measured effect on outcome | DONE | P1 | Experiment tables with run counts, not anecdotes |
| M9-07 | Publish the results-analysis notebook and result visualisations | DONE | P1 | Guidelines §9.2/§9.3: a notebook compares strategies and configurations, uses LaTeX for equations, cites academic references, and emits labelled high-resolution charts |
| M9-07a | Compare baseline against belief-driven pursuit | DONE | P1 | Win rate and mean capture turn over repeated runs |
| M9-07b | Emit labelled, accessible, high-resolution charts | DONE | P1 | Clear axes, legend, caption `[G§9.3]` |
| M9-07c | Cite academic references and format equations in LaTeX | DEFERRED | P2 | `[G§9.2]` |
| M9-08 | Evidence ISO/IEC 25010, extension points, and concurrency safety | DEFERRED | P2 | Guidelines §12/§13/§15 (grouped as "Extension and Standards" in their §17.6): the eight quality characteristics are evidenced, plugin/extension seams are documented, and any threading or multiprocessing carries a thread-safety justification |
| M9-08a | Map the eight ISO/IEC 25010 characteristics to evidence | DEFERRED | P2 | One evidence pointer per characteristic `[G§13.1]` |
| M9-08b | Document the strategy and verbal-provider extension seams | DEFERRED | P2 | How a third party swaps a policy without editing core `[G§12.1]` |
| M9-08c | Justify every thread or process with a safety note | DEFERRED | P2 | Locks, queues, and shutdown paths described `[G§15.2]` |
| M9-09 | Assemble the league evidence bundle | DEFERRED | P0 | Every counted game's four artifacts, commit hashes, and sent-report proof |
| M9-09a | Archive the artifact set per counted game | DEFERRED | P0 | Retrievable by `game_id` |
| M9-09b | Record the commit hash that ran each game | DEFERRED | P0 | `[AE-53]`; code may change between games |
| M9-09c | Record proof that each report was sent | DEFERRED | P0 | An unsent report voids that game's points `[AE-32]` |
| M9-09d | Reconcile declared game counts against the artifact set | DEFERRED | P0 | A false declaration is absolute disqualification `[AE-38]` |
| M9-10 | Write the academic report body | DEFERRED | P0 | A scientific document, not an installation guide `[AE-42]` |
| M9-10a | Justify the architectural decisions and trade-offs | DEFERRED | P1 | ADRs summarised with rationale `[G§20.1]` |
| M9-10b | Present empirical results, not claims | DEFERRED | P1 | Numbers come from reproducible runs |
| M9-10c | Disclose every book contradiction relied on | DEFERRED | P0 | Book p. 5 requires where, what, and why; see `M0-04` |
| M9-10d | Cite the reference list | DEFERRED | P2 | Academic citation format `[G§9.2]` |
| M9-11 | Complete the installation and usage documentation | DEFERRED | P1 | A grader can install and run from the README alone `[G§2.1]` |
| M9-11a | Document system requirements and setup | DEFERRED | P1 | Including `uv` and Python version |
| M9-11b | Document every run mode and flag | DEFERRED | P1 | Peer, replay, and CLI paths |
| M9-11c | Document the configuration files and their effect | DEFERRED | P1 | Shared JSON versus private TOML `[ADR-004]` |
| M9-11d | Document troubleshooting for common failures | DEFERRED | P2 | Tunnel down, opponent unreachable, credential missing |
| M9-11e | State the licence and third-party attributions | DEFERRED | P2 | `[G§2.1]` |
| M9-12 | Run the pre-submission dry run | DEFERRED | P0 | Clone fresh, install frozen, run every gate, run a game, produce artifacts |
| M9-12a | Verify from a clean clone on a second machine | DEFERRED | P0 | Nothing depends on an untracked local file |
| M9-12b | Verify every gate passes from that clean clone | DEFERRED | P0 | `G-01`…`G-09` |
| M9-12c | Verify the replay app validates a real stored match | DEFERRED | P0 | `[AE-20]` |
| M9-13 | Complete the Moodle submission | DEFERRED | P0 | Form, PDF, per-member submission, and team code all correct |
| M9-13a | Confirm the reporting and sharing addresses one final time | DEFERRED | P0 | `rmisegal@gmail.com` and `rmisegal+uoh26finalgame@gmail.com`; the book's Table 20 spelling is a typo |
| M9-13b | Confirm both repositories are reachable by the grader | DEFERRED | P0 | Public, or shared `[AE-49]` |
| M9-13c | Confirm the cross-links resolve in both READMEs | DEFERRED | P0 | Cop links Thief and Thief links Cop `[AE-49]` |
| M9-14 | Complete the code-quality self-assessment | DEFERRED | P1 | Graded against the guidelines' quick-reference card, never the league result `[AE-55]` |
| M9-14a | Score each guidelines requirement honestly | DEFERRED | P1 | SDK, OOP, gatekeeper, TDD, coverage, linter, secrets, `uv` `[G§19.1]` |
| M9-14b | Name the requirements not met and why | DEFERRED | P1 | An honest gap costs less than an overclaim |
| M9-15 | Verify the four success metrics are demonstrable | DEFERRED | P1 | Coordination, adaptation, integrity, architecture — each with evidence `[book §11.4]` |
| M9-15a | Evidence coordination | DEFERRED | P1 | Turn management and P2P synchronisation without a judge |
| M9-15b | Evidence adaptation | DEFERRED | P1 | Belief updating under partial observation |
| M9-15c | Evidence integrity | DEFERRED | P1 | Commit-reveal plus a passing mutual audit |
| M9-15d | Evidence architecture | DEFERRED | P1 | Orchestrator and gatekeeper patterns under load |
| M9-16 | Archive the final submission state | DEFERRED | P1 | The tagged commit, artifacts, and evidence bundle are retained together |

---

## Appendix — Appendix E rule coverage map

Every mandatory rule maps to at least one owning task. A rule with no owning task is a
ledger defect, not an exemption.

| Rules | Subject | Owning tasks |
|---|---|---|
| 1, 2 | Two processes, no shared memory | `M5-09` |
| 3 | Orchestrator single gateway | `M5-08`, `M5-08a`…`c` |
| 4, 5 | State machine, illegal transitions | `M4-04`, `M4-04a` |
| 6, 7 | Watchdog | `M5-06`, `M5-06a`…`d` |
| 8, 9 | Local-truth UI only | `M3-01a`, `M6-02d`, `M8-01d` |
| 10 | Public tunnel | `M5-07`, `M5-07b` |
| 11, 12 | Identical config, raise-only minimums | `M5-04b`, `M5-04d` |
| 13, 14 | Orthogonal only, no diagonals | `M2-01b`, `M2-03a` |
| 15, 16 | Truthful barrier disclosure | `M2-04c` |
| 17, 18 | Commit-reveal, nonce secrecy | `M4-03`, `M4-03a`, `M4-03b` |
| 19 | Reject audit mismatch | `M4-05a` |
| 20 | Replay verification app | `M8-02`, `M8-02a`…`c` |
| 21, 22 | Truthful capture claims | `M2-05a` |
| 23 | Scent-model hash lock | `M6-07`, `M6-07a`, `M6-07b` |
| 24 | Step-0 attestation | `M4-06`, `M4-06a`…`c` |
| 25 | LLM never decides moves | `M6-05d` |
| 26, 27 | Natural language only, no coordinate protocol | `M6-05c` |
| 28 | Token-bucket rate limiter | `M7-04b` |
| 29 | DOS detector | `M7-08b` |
| 30 | Authorized send only | `M7-05a` |
| 31 | Minimum different opponents | `M9-01a` |
| 32, 33, 34 | Automatic JSON reporting | `M7-05c`, `M7-06b` |
| 35 | Result agreement, separate reports | `M7-06b`, `M7-06c` |
| 36 | Full mutual audit | `M7-06a` |
| 37, 38 | Accurate game-count declaration | `M7-09`, `M7-09a`, `M7-09b` |
| 39, 40 | No secrets, `.gitignore` | `G-05`, `M7-05b`, `M9-04b` |
| 41 | Annotated submission tag | `M9-05a` |
| 42 | Academic report | `M9-02`, `M9-02a`…`f` |
| 43, 44, 45 | Moodle form, per-member, team code | `M9-05b`, `M9-05c`, `M9-05d` |
| 46, 47, 48 | Barrier capture, trapped, scoring table | `M2-05b`, `M2-05c`, `M3-03a`…`c` |
| 49 | Two repos, cross-links | `M7-03c`, `M9-02f`, `M9-04a` |
| 50 | Minimum repository contents | `G-10`, `M9-04` |
| 51 | Reporting address | `M7-05d` |
| 52 | One scoring game per opponent | `M9-01b`, `M7-09b` |
| 53 | Per-game commit hash | `M4-06b`, `M7-03d` |
| 54 | Total tokens reported | `M4-06c`, `M7-03d`, `M9-03a` |
| 55 | Self-assessment on code quality only | `M9-05e` |

---

## Appendix — submission-guidelines coverage map

The book's Table 4 names the course submission guidelines as a graded criterion, so each
section needs an owning task exactly as the Appendix E rules do.

| Guideline | Subject | Owning tasks |
|---|---|---|
| §2.1 | Comprehensive `README.md` | `M9-02` |
| §2.2 | `docs/PRD.md`, `PLAN.md`, `TODO.md` | `G-10` |
| §2.3 | One PRD per algorithm/mechanism | `G-10` |
| §2.4 | Recommended project structure | `M1-01` |
| §3.1 | Modular structure | `M1-01b` |
| §3.2 | 150-line file cap | `G-04` |
| §3.3 | Docstrings and why-comments | `G-02` |
| §4.1 | SDK is the sole entry point | `M1-01b` |
| §4.2 | OOP, no duplication | `G-02` |
| §5.1 | Centralized API gatekeeper | `M7-04a` |
| §5.2 | Rate limits from configuration | `M7-04d` |
| §5.3 | Queue management for overflow | `M7-04c`, `M5-05d` |
| §6.1 | TDD red/green/refactor | `G-03` |
| §6.2 | 85% coverage floor | `G-03` |
| §6.3 | Edge cases and error handling | `M8-04b` |
| §7.1 | Zero Ruff violations | `G-02` |
| §7.2 | No hardcoded values | `M7-04d`, `M2-02a` |
| §7.3 | Configuration architecture | `M1.5-03` |
| §7.4 | Secrets management, `.env-example` | `G-05`, `M7-05b` |
| §8.1 | Version tracking from 1.00 | `M1-01a` |
| §8.2 | Branches, PRs, tags | `M9-05a` |
| §8.3 | Prompt engineering log | `G-08` |
| §8.4 | `uv` mandatory, no pip | `G-01` |
| §9.1 | Parameter research / sensitivity | `M9-06`, `M9-06a`…`c` |
| §9.2 | Results-analysis notebook | `M9-07`, `M9-07a`, `M9-07c` |
| §9.3 | Visual presentation of results | `M9-07b` |
| §10.1 | Usability criteria, Nielsen heuristics | `M8-04d` |
| §10.2 | Interface documentation and screenshots | `M8-02e`, `M8-05` |
| §11.1 | Token cost analysis | `M9-03a` |
| §11.2 | Budget management | `M7-04b` |
| §12.1 | Extension points | `M9-08b` |
| §13.1 | ISO/IEC 25010 characteristics | `M9-08a` |
| §14 | Package organization | `M1-01` |
| §15 | Parallel processing, thread safety | `M9-08c` |
| §16 | Building-block design | `M1-01b` |

---

## Appendix — book seven-stage roadmap coverage

Book chapter 10 prescribes building in order, each stage running end-to-end before the
next. Stage 6 was completed before stage 2 closed; `M5-10` exists to close that gap.

| Stage | Subject | Owning tasks | State |
|---|---|---|---|
| 1 | Base logic: grid, movement, barriers, capture | `M2-01`…`M2-05`, `M3-04` | complete |
| 2 | Basic MCP infrastructure over localhost | `M5-01`…`M5-03`, `M5-10` | **open — built out of order** |
| 3 | Blind strategy module | `M3-05`, `M3-06` | complete |
| 4 | Natural language and scent | `M6-01`…`M6-05` | open |
| 5 | Cloud exposure and tunnelling | `M5-07`, `M5-07c` | open |
| 6 | Security and cryptography | `M4-01`…`M4-06` | complete |
| 7 | Reporting and visualization shell | `M7-05`, `M8-01`, `M8-02` | open |

---

## Appendix — PRD to task map

| PRD | Owning tasks |
|---|---|
| `PRD_p2p_mcp.md` | `M5-01`…`M5-10` |
| `PRD_commit_reveal.md` | `M4-01`…`M4-06` |
| `PRD_scent_belief.md` | `M6-01`…`M6-03`, `M6-07` |
| `PRD_strategy.md` | `M3-05`, `M3-06`, `M6-03`, `M6-06` |
| `PRD_gatekeeper_reporting.md` | `M7-04`, `M7-05`, `M7-08`, `M7-11` |
| `PRD_gui.md` | `M8-01`, `M8-05a` |
| `PRD_replay.md` | `M8-02`, `M8-05b` |

---

## Appendix — open unknowns and the tasks they block

A task whose authority is an open unknown must not be implemented as binding. Ruling on
these is coordinator work, not engineering work.

| Unknown | Question | Blocks |
|---|---|---|
| `U-025` / `OB-005` | Within-series role schedule (odd natural, even swapped). Observed in the pinned simulator and present in owner-supplied lecturer direction, but not book-authenticated. The companion repo currently treats it as confirmed; this repo does not | `M7-01`, `M7-01b`, `M7-07` |
| ~~`U-026`~~ | ~~Counterpart award on a technical loss~~ — **CLOSED 2026-07-31**: chapter 3 table 2 prints the row `0 \| 0` and rule 48 writes "technical loss 0/0", so both peers score zero | `M3-03c`, `M7-06` |
| `U-0xx` (`M3-07`) | Whether surviving exactly `survival_threshold` turns is a Thief win. Appendix F table 15 sets step limit and survival threshold to the same value | `M3-07a`…`c`, `M7-01c` |
| Artifact UUID protocol | Whether `game_uid` is UUIDv4 or SHA-256 derived | `M7-02c` |
| Turn ordering | Whether the Thief or the Cop acts first in a live turn. The local harness injects a `PROJECT-PROPOSED` default rather than asserting one | `M3-04`, `M5-04` |

---

## Appendix — critical path and external dependencies

Ordering constraints that no amount of parallel work removes.

| # | Item | Depends on | Note |
|---|---|---|---|
| 1 | `M5-03` FastMCP client | nothing | The single missing piece before two peers can exchange a message |
| 2 | `M5-10` localhost end-to-end | `M5-03` | Closes the skipped book stage-2 gate; everything downstream is unverified until it passes |
| 3 | `M5-07c` tunnel rehearsal | `M5-10` | First test against real latency and NAT |
| 4 | `M8-03c` warm-up vs a classmate | `M5-07c` | **External dependency: another team's schedule** |
| 5 | `M9-01a` counted league games | `M8-03c`, `M7-05`, `M7-06` | **External dependency**; a game without a sent report scores nothing |
| 6 | `M9-05a` submission tag | all of the above | Cannot precede the league evidence it must contain |

Items 4 and 5 are the longest lead time in the project because they depend on other
groups being ready at the same time. Everything else is internal and can be parallelised;
these cannot. Start opponent scheduling as soon as item 3 passes, not when item 5 begins.

---

## Appendix — glossary

Terms used throughout this ledger, for anyone joining mid-project.

| Term | Meaning |
|---|---|
| Option B | The decision to adopt the pinned simulator's wire shape wherever the book leaves a wire detail open, while the book still governs rules and scoring |
| Wire | The exact bytes exchanged between peers. Two agents must agree byte-for-byte or every hash comparison fails |
| `shared_contract/` | The controlled bundle of schemas, fixtures, and golden vectors that both peers must satisfy. Currently `0.2.9-proposed`, `UNFROZEN` |
| Mailbox semantics | The server tools enqueue a message and always acknowledge; a content rejection is a game outcome, decided later, not a transport error `[ADR-002]` |
| Commit-reveal | Send a hash of the move first, reveal the move after, disclose the nonce only at the final audit. Any mismatch is a technical loss |
| Nonce | A fresh random value per commitment. Prevents identical moves producing identical hashes and defeats dictionary attacks |
| Canonical JSON | Sorted keys, compact separators, fixed encoding, so both peers hash byte-identical input |
| Step-0 | The pre-game sealed declaration of hardware, model, group, game, token budget, and the exact running Git commit |
| Local truth | Each peer knows only its own position, its disclosed barriers, and its observations. Representing the opponent's true position is a rule violation, not a shortcut |
| Technical loss | A crash, timeout, or proven forgery. Scores zero regardless of the position on the board |
| Gate | An automated check that must pass before a commit. Listed under Continuous gates above |
| `PROJECT-PROPOSED` | A choice this repo made where no authority exists. Injectable and reversible; never presented as confirmed |
| `U-nnn` | An open unknown. Blocks any task that would otherwise have to guess it |
