# Unknown Requirements and Decisions

These items block only the affected runtime/freeze decision. Confirmed values,
filename patterns, shared/private split, report attachment, six README sections,
annotated tag, and email addresses are not unknown.

| ID | Narrow unresolved question | Blocks | Resolution evidence |
|---|---|---|---|
| U-001 | Original Moodle checksum/provenance beyond the owner's designation of `Json-examples/` as the course examples | Provenance claim only; no longer the M1 shared-config gate | Original Moodle/lecturer download, message, archive, or checksum |
| U-002 | Exhaustive artifact required/optional, type/enum, conditional, and compatibility rules beyond the established core lifecycle | M7 full artifact validation | Referenced official schemas/fixtures or accepted project schema |
| U-004 | Envelope, acknowledgement, sequencing, errors, and idempotency fields | Network contract freeze | ADR-002 plus interop tests |
| U-006 | Exact peer ports and tunnel provider | Private runtime config | Team choice; must remain private/provider-neutral |
| U-007 | Artifact-version compatibility beyond observed 1.1 and shared config 1.2 | Compatibility policy | ADR-003 plus authoritative schema evidence |
| U-009 | Gmail client/delivery implementation details beyond confirmed destination and JSON attachment | Reporting runtime | ADR-010 plus dated official guidance if needed |
| U-010 | Whether generic stateless runtime code may be duplicated across repositories | Shared runtime architecture | Direct rule/lecturer clarification and accepted ADR |
| U-016 | ~~Team/group/member identifiers and eight-character team code~~ | ~~Declaration/reporting~~ | **CLOSED 2026-07-31.** Verified team input supplied 2026-07-28: group identifier and eight-character team code both `sharNamr`; members Amr safadi; Sharbel Maroun. Recorded in `TEAM_INFO.md` |
| U-017 | Newer Moodle/lecturer instructions | Recency-sensitive submission choices | Obtain dated official post |
| U-018 | Exact controlling Ruff course configuration if newer than the inspected guideline | Quality configuration | Current official course config |
| U-019 | Independent peer acceptance and exact hashes for `0.2.5-proposed` | Contract freeze | Independent peer review and matching parity runs |
| U-020 | Permission/provenance for any substantial simulator-source reuse | Simulator reuse | ADR-008 review and, if necessary, written permission |
| U-021 | Allowed runtime `group_id` syntax beyond non-empty JSON text; the Moodle team code is a separate eight-character identifier | M7 formal identifier validation | Authenticated schema or lecturer clarification |
| U-022 | UUIDv4 proposal versus current deterministic non-versioned simulator UUID; exact `game_id` syntax | M7 artifact identity protocol | Accepted ADR/vector or higher-authority clarification |
| U-024 | Complete artifact constraints and compatibility beyond common identities/lifecycle | M7 full artifact validation | Authenticated templates/schemas or accepted project schema |
| U-026 | What the non-falsifying peer scores when its opponent takes a technical loss. Appendix E rules 19/48 fix the falsifying peer at zero, but no consulted source states the counterpart award: whether it is the capture value, the survival value, or something else | M3 scoring completeness; M7 series aggregation | Direct book or appendix text, or an authenticated lecturer answer. `ScoringTable.technical_loss_award` deliberately returns one side's award only and never invents the counterpart |
| U-025 | ~~Six-sub-game role schedule~~ | ~~M7 series orchestration~~ | **CLOSED 2026-07-31.** The required lecturer answer was obtained and relayed by the coordinator on 2026-07-29: sub-games 1, 3, 5 use the natural role, 2, 4, 6 the swapped role, and the **Thief moves first**. Recorded here on 2026-07-31 after the answer was found already applied in the companion peer but never propagated to this repository. Provenance is a coordinator-relayed lecturer answer, not a Moodle announcement; see `C-029`. Re-admitting the schedule to the contract bundle requires a version bump under `OB-005` |
| U-027 | Whether surviving *exactly* `[Survival Threshold]` turns is a Thief win, given Appendix F table 15 sets `[Step Limit]` and `[Survival Threshold]` to the same value (35) | Terminal-outcome scoring; series aggregation | Owner ruling plus a boundary test. `run_sub_game` currently resolves it as a Thief win at exactly the threshold without recording the choice; see `C-024` and `M3-07` |

Resolved: Appendix F values/statuses; multiplicative scent equation; report
attachment/no-free-text rule; per-turn commitment-nonce secrecy until final reveal
and the distinct public negotiation challenge; explicit per-match/private-TOML
boundary; two-ID `agreed_between` representation; config
hash scope and serialization; common artifact identities and
lifecycle; literal `<NN>` logical links/resolved physical filenames; local
`rate_limits.json` boundary; book-defined artifact filename patterns; rule-25 recommendation status;
six README sections; tag requirement; both addresses; Option-B FastMCP tool names;
Option-B per-turn commitment canonical bytes, delimiter, and commitment-nonce
profile.
