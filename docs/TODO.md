# Active Cop TODO

Only Cop-owned work is decomposed here. `DONE` means implemented and locally
verified; it does not imply cross-repository acceptance. `BLOCKED` names an external
evidence/review dependency. All M2–M9 work is `DEFERRED` by the controlling audit.

| ID | Cop-owned task | Status | Priority | Definition of done |
|---|---|---|---|---|
| M0-01 | Audit requirements, contradictions, and historical parity claims | DONE | P0 | Evidence ledger and baseline differences are recorded |
| M0-02 | Correct authority order and local JSON provenance | DONE | P0 | All affected claims use the coordinator hierarchy and `NEEDS_MANUAL_REVIEW` |
| M0-03 | Maintain conflicts, unknowns, and proposal boundaries | DONE | P0 | P0 uncertainties remain explicit and no simulator behavior is promoted |
| M1-01 | Maintain installable behavior-free Cop package/SDK | DONE | P0 | Frozen install, version, import, CLI, and SDK smoke paths pass |
| M1-02 | Define stable public league semantics | DONE | P0 | Appendix F status and ownership are separate from match values |
| M1-03 | Define public-match/private-peer boundaries | DONE | P0 | Ports, URL storage, models, credentials, strategies, secrets, and nonces stay private |
| M1-04 | Model neutral participant and match binding | DONE | P0 | `agreed_between`, game/sub-game identity, and neutral identifiers validate |
| M1-05 | Validate fixed, minimum, and negotiated match values | DONE | P0 | Fixed changes and below-minimum values reject; negotiated values load from files |
| M1-06 | Isolate 1.1, 1.2, and 1.3 observations | DONE | P0 | Unsupported versions reject without translation or normalization |
| M1-07 | Enforce match mismatch/private leakage failures | DONE | P0 | Participant, value, hash-shape, duplicate-key, and private-field vectors reject |
| M1-08 | Distinguish local integrity from cross-root comparison | DONE | P0 | Checker reports local manifest result and optional exact-byte comparison separately |
| M1-09 | Add reproducible CI | DONE | P0 | Required frozen sync, lint, tests, length, secret, integrity, and diff gates run |
| M1-10 | Authenticate four local JSON artifacts | BLOCKED | P0 | Original Moodle/lecturer handoff or authenticated checksum is supplied |
| M1-11 | Specify participant order and match canonicalization | DONE | P0 | Ordered IDs, complete-object scope, canonical UTF-8 bytes, and external hash claim are tested |
| M1-12 | Reconcile config split, identity fields, and role schedule | DONE | P0 | Unified shared authority, artifact lifecycle, identities, and odd/even roles are documented |
| M1-13 | Incorporate accepted M1 answers and vectors | DONE | P0 | Candidate hash `adac9efe…82db` and rejection vectors pass |
| M1-14 | Produce candidate handoff | DONE | P0 | Controlled paths/hashes, manifest self-hash, gates, and blockers are recorded |
| M1-15 | Promote contract version after acceptance evidence | BLOCKED | P0 | Coordinator authorizes freeze after independent parity/interop proof |
| M2-01 | Implement immutable coordinate and action types | DEFERRED | P1 | SDK-visible unit tests prove immutability and vocabulary |
| M2-02 | Implement board geometry and boundary validation | DEFERRED | P1 | Negotiated board/origin semantics pass boundary tests |
| M2-03 | Implement legal orthogonal movement and `STAY` | DEFERRED | P1 | All legal/illegal transitions are deterministic |
| M2-04 | Implement barrier inventory, placement, and disclosure rules | DEFERRED | P1 | Quota, legality, and disclosed events pass tests |
| M2-05 | Implement capture conditions after `STAY` clarification | DEFERRED | P1 | Current-cell and trapped-Thief rules match accepted interpretation |
| M3-01 | Implement Cop-local immutable state | DEFERRED | P1 | No opponent private truth is representable |
| M3-02 | Implement deterministic state history | DEFERRED | P1 | Repeated input creates reproducible history |
| M3-03 | Implement fixed scoring and technical loss | DEFERRED | P1 | Appendix F/E outcomes pass table-driven tests |
| M3-04 | Build single-process rules harness | DEFERRED | P1 | Full local sub-game completes without transport |
| M3-05 | Implement SDK-reachable deterministic pursuit baseline | DEFERRED | P1 | Policy emits only legal actions and barriers |
| M4-01 | Finalize public message/envelope contract | DEFERRED | P0 | Accepted ADR-001/002 schemas and error semantics exist |
| M4-02 | Finalize canonical JSON and nonce vectors | DEFERRED | P0 | Independent implementations reproduce exact hashes |
| M4-03 | Implement commit, acknowledge, reveal, and final audit | DEFERRED | P0 | Valid state sequence round-trips through SDK |
| M4-04 | Reject illegal transitions, replay, and idempotency conflicts | DEFERRED | P0 | Failure vectors terminate deterministically |
| M4-05 | Implement tamper and technical-loss audit outcomes | DEFERRED | P0 | Byte/field/nonce mutations are detected |
| M5-01 | Implement transport-neutral peer interface | DEFERRED | P1 | SDK has no FastMCP-specific business logic |
| M5-02 | Implement FastMCP server adapter | DEFERRED | P1 | Accepted tools validate inbound calls |
| M5-03 | Implement FastMCP client connector | DEFERRED | P1 | Accepted calls work against a neutral stub |
| M5-04 | Implement negotiation and mismatch refusal | DEFERRED | P0 | Unknown opponent acceptance works both directions |
| M5-05 | Implement deadlines, retry, idempotency, and backpressure | DEFERRED | P0 | Injected failures cannot hang the peer |
| M5-06 | Implement watchdog and terminal disconnect handling | DEFERRED | P0 | Silence/disconnect produces defined outcomes |
| M5-07 | Validate provider-neutral public tunnel boundary | DEFERRED | P1 | No provider secret enters shared configuration |
| M6-01 | Implement multiplicative scent field | DEFERRED | P1 | Book equation and fixed constants pass numeric tests |
| M6-02 | Implement Cop-local belief update | DEFERRED | P1 | Belief uses observation only and normalizes safely |
| M6-03 | Integrate belief into deterministic pursuit | DEFERRED | P1 | Policy improves target choice without illegal actions |
| M6-04 | Add private strategy configuration | DEFERRED | P2 | Tuning stays local and SDK-loaded |
| M6-05 | Add optional verbal/LLM adapter with zero-token fallback | DEFERRED | P2 | Provider failure always falls back deterministically |
| M7-01 | Implement six-sub-game series orchestration | DEFERRED | P1 | Accepted role schedule and identities drive all six games |
| M7-02 | Generate declaration and per-game config artifacts | DEFERRED | P1 | Accepted artifact schemas and filenames validate |
| M7-03 | Generate game logs and final result | DEFERRED | P1 | Audit links, commits, tokens, and scores are consistent |
| M7-04 | Implement API Gatekeeper and token-bucket/FIFO limits | DEFERRED | P1 | Appendix F minimums and backpressure pass load tests |
| M7-05 | Implement signed final JSON reporting adapter | DEFERRED | P1 | Attachment-only delivery uses least privilege |
| M7-06 | Validate series audit and mutual-result agreement | DEFERRED | P0 | Conflicts/missing reports produce defined failure |
| M8-01 | Implement local-truth live GUI | DEFERRED | P1 | No objective opponent state is exposed |
| M8-02 | Implement replay verifier and tamper view | DEFERRED | P1 | `Verified OK` and `TAMPERED` paths are demonstrable |
| M8-03 | Run neutral unknown-opponent interoperability suite | DEFERRED | P0 | Both proposal/acceptance directions pass remotely |
| M8-04 | Run fault, security, secret, and resource hardening | DEFERRED | P0 | Failure matrix and abuse tests pass |
| M8-05 | Capture required GUI/replay evidence | DEFERRED | P1 | Submission-quality screenshots are reproducible |
| M9-01 | Run counted league series against required opponents | DEFERRED | P0 | Current official minimums and declarations are satisfied |
| M9-02 | Complete six-section academic README report | DEFERRED | P0 | Model, protocol, strategy, results, screenshots, and links are present |
| M9-03 | Complete performance, token, and cost evidence | DEFERRED | P1 | Results derive from reproducible runs |
| M9-04 | Run final two-repository submission audit | DEFERRED | P0 | Access, secrets, reports, artifacts, and quality gates pass |
| M9-05 | Create annotated release tag and submit | DEFERRED | P0 | Current Moodle tag/form/PDF instructions are followed |
