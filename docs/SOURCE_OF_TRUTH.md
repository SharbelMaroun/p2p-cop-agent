# Source of Truth

## Status vocabulary

- `CONFIRMED`: supported by direct authoritative evidence.
- `CONFLICT`: authoritative or candidate sources disagree.
- `UNKNOWN`: direct evidence is missing, unreadable, secondary, or insufficiently precise.

Only `CONFIRMED` entries may guide implementation.

## Priority

1. Official final-project book v3.0.0.
2. Appendix F for binding numerical values and modes.
3. Appendix E for mandatory rules.
4. Official Moodle JSON templates.
5. Newer official Moodle instructions and lecturer announcements.
6. Professional Software Submission Guidelines v3.0.
7. Lecturer simulator at a recorded commit.
8. Project-book NotebookLM, for navigation only.
9. Simulator-code NotebookLM, for navigation only.
10. Translations, summaries, team notes, current repository content, and AI plans.

Simulator behavior is evidence about the simulator, not automatically a project requirement. NotebookLM and translations never confirm a requirement by themselves.

## Current evidence boundary

The repository contains a binary file named `Material/reference/police_thief_p2p.pdf`, SHA-256 `7C9E1D7527582C3AEF9AFD71709981CEA50EA60B8FABEFE85EFCCAB0A5FDD02E`. Its title/version and contents could not be independently extracted during this audit because the available MiKTeX PDF tools require an unavailable first-run configuration. The adjacent translation is explicitly unverified. Consequently, claims located through that translation remain `UNKNOWN`.

The lecturer simulator was inspected as a lower-priority implementation reference at commit `960499fd5e8777b4929625f5d8fdcf2ab4677b54`; see [SIMULATOR_BASELINE.md](SIMULATOR_BASELINE.md).
