# Specification Conflicts and Unresolved Discrepancies

Shared register, byte-identical in both repositories. Each row is `CONFIRMED` (resolved with
direct evidence), `CONFLICT` (sources still disagree), or `UNKNOWN` (evidence missing). No
entry is resolved by adopting a simulator default or an unverified number; numeric values live
in [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md) as directly confirmed Appendix F values.

| ID | Status | Issue | Resolution / evidence |
|---|---|---|---|
| C-001 | CONFIRMED | Draft `num_games = 1` versus a derived-source claim of "6". | Appendix F table 18 directly confirms 6 games in a series, minimum-to-pass 2, and maximum 10 per group (original PDF p. 154). It does not confirm a JSON field named `num_games` or its default; those schema/simulator details remain `UNKNOWN`. |
| C-002 | CONFIRMED | README "five components + a cross-link" versus "six mandatory sections". | Reconciled: the academic report has **six mandatory sections and #6 is the companion cross-link**, so "five + link" equals six. Book Ch.9.4.2 (summary :2291–2296); Appendix E rule 42. Recorded as `SR-008`. |
| C-003 | UNKNOWN | Simulator audit-tool name may be `submit_audit`, `exchange_audit`, or another. | Import the centralized verified simulator export at a recorded commit. Not derivable from summaries. |
| C-004 | CONFIRMED | Gmail address spelling differed across derived sources. | Original PDF p. 157, table 20 gives `rmisegal@gmail.com` for repository sharing and `rmisegal+uoh26finalgame@gmail.com` for automated reports. |
| C-005 | CONFIRMED | Earlier references cited Appendix G for GitHub submission. | Corrected: book v3.0.0 uses Appendix C. |
| C-006 | UNKNOWN | Whether all four reporting artifacts must be byte-identical. | Only the shared `config` JSON is byte-identical (`config_sha256`); the four files share a `game_uid` but differ by content (summary :2227–2243). Exact field-equality rules need the official Moodle templates. |
| C-007 | UNKNOWN | Whether an independently duplicated stateless shared package is permitted. | Shared **live** state is prohibited (`SR-004`). Whether duplicated stateless code is allowed needs a direct rule or lecturer clarification. |

_No unresolved entry is closed by selecting an example or a simulator default._
