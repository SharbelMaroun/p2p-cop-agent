# Specification Conflicts and Unresolved Discrepancies

Shared register, byte-identical in both repositories. Each row is `CONFIRMED` (resolved with
direct evidence), `CONFLICT` (sources still disagree), or `UNKNOWN` (evidence missing). No
entry is resolved by adopting a simulator default or an unverified number; numeric values live
in [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md) as candidates pending official confirmation.

| ID | Status | Issue | Resolution / evidence |
|---|---|---|---|
| C-001 | CONFIRMED | Draft `num_games = 1` versus a NotebookLM claim of "6". | Distinct concepts, not a contradiction: `num_games` is a shared-config field whose default is 1 (a single game); a **series** is 6 games vs one opponent, with minimum-to-pass 2 and maximum 10 per group. Book Ch.9 / Appendix F Table 18 (summary :2963, :3540–3544). The "6" is labelled *[Number of Agents]* (series), distinct from the board *[Number of Agents]* = 2 (:3484). The numeric values themselves stay in PARAMETERS_BASELINE.md (pending). |
| C-002 | CONFIRMED | README "five components + a cross-link" versus "six mandatory sections". | Reconciled: the academic report has **six mandatory sections and #6 is the companion cross-link**, so "five + link" equals six. Book Ch.9.4.2 (summary :2291–2296); Appendix E rule 42. Recorded as `SR-008`. |
| C-003 | UNKNOWN | Simulator audit-tool name may be `submit_audit`, `exchange_audit`, or another. | Import the centralized verified simulator export at a recorded commit. Not derivable from summaries. |
| C-004 | CONFLICT | Gmail address spelling and controlling announcement. | Candidates recorded, NOT confirmed — the spelling itself is in conflict across sources: reporting appears as `rmisegal+uoh26finalgame@gmail.com` (DEV-SPEC §16; book rule 51) and as `rimesegal+…` in translation; repo-sharing as `rimesegal@gmail.com` (summary :3605). The `rmisegal` vs `rimesegal` drift must be verified with the lecturer before wiring. Tracked in TEAM_INFO.md. |
| C-005 | CONFIRMED | Earlier references cited Appendix G for GitHub submission. | Corrected: book v3.0.0 uses Appendix C. |
| C-006 | UNKNOWN | Whether all four reporting artifacts must be byte-identical. | Only the shared `config` JSON is byte-identical (`config_sha256`); the four files share a `game_uid` but differ by content (summary :2227–2243). Exact field-equality rules need the official Moodle templates. |
| C-007 | UNKNOWN | Whether an independently duplicated stateless shared package is permitted. | Shared **live** state is prohibited (`SR-004`). Whether duplicated stateless code is allowed needs a direct rule or lecturer clarification. |

_No unresolved entry is closed by selecting an example or a simulator default._
