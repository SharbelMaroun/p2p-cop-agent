# Specification Conflicts

| ID | Status | Conflict | Evidence | Required resolution |
|---|---|---|---|---|
| CONFLICT-001 | CONFLICT | Current `game.json` uses `num_games: 1`; secondary material claims a fixed series count of 6 | Current config; unverified translation; simulator README/default | Verify Appendix F and current Moodle announcements |
| CONFLICT-002 | CONFLICT | Current README says six mandatory report sections; the unverified translation describes five components | Current README before audit; translation around Appendix C | Verify Chapter 9 and guidelines v3.0 |
| CONFLICT-003 | CONFLICT | Planning text spells the lecturer simulator owner both `rmisegal` and `rimesegal` | Local overview versus current public repository | Use public upstream `rmisegal/Game-P2P-Cop-Chase`; verify official book separately |
| CONFLICT-004 | CONFLICT | Existing configuration/reporting address claims must not be trusted; spelling and behavior are unresolved | Current TOML and secondary translation | Verify official Appendix/table and newer announcement |
| CONFLICT-005 | CONFLICT | Existing docs present exact MCP tools/messages that differ across planning text and simulator versions | PRDs/TODO versus pinned simulator | Verify official protocol requirements; choose no schema now |
| CONFLICT-006 | CONFLICT | Existing files describe `1.00`, `1.2`, and simulator `3.0.0` versions without a verified mapping | Config, planning docs, simulator | Verify book, template, and submission-version rules |
| CONFLICT-007 | CONFLICT | Cop repository contains `config/thief/`, while the requested runtime boundary is Cop-only | Repository layout versus audit task scope | Decide later whether examples are allowed; do not load them |
