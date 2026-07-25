# Source of Truth

## Status vocabulary

- `CONFIRMED`: supported by direct authoritative evidence.
- `CONFLICT`: authoritative or candidate sources disagree.
- `UNKNOWN`: direct evidence is missing, incomplete, or unresolved.

Only `CONFIRMED` entries may guide implementation.

## Priority

1. Official final-project book v3.0.0.
2. Appendix F for binding numerical values and modes.
3. Appendix E for mandatory rules.
4. Official JSON templates.
5. Newer Moodle instructions and lecturer announcements.
6. Professional Software Submission Guidelines v3.0.
7. Lecturer simulator at a recorded commit.
8. NotebookLM answers as navigation aids only.
9. Summaries, translations, existing PRDs/plans, and AI notes.

Simulator behavior is not automatically a project requirement. NotebookLM, summaries, and translations do not independently confirm requirements.

## Directly inspected sources

- `Material/reference/police_thief_p2p.pdf`, 160 pages, SHA-256 `7C9E1D7527582C3AEF9AFD71709981CEA50EA60B8FABEFE85EFCCAB0A5FDD02E`. Text was extracted directly with `pypdf` during this remediation. Structural evidence was checked in Chapter 2, Chapter 9, Appendix C, and Appendix E.
- Professional Software Submission Guidelines v3.0, 39 pages, local course-material copy SHA-256 `3F02DF37767C745EFC47646140C2E6AC7CAE3B9C87C92073DAF4EEF74BE09EBB`. Pages 7–20 were inspected directly.
- Planning repository `AmrSafadi/AI-Agent-Orchestration-FinalProject` at commit `0c751942fc133a4bbd7a1a3348f95800e73c81e3` was used for navigation and dependency inventory only.

The official JSON templates and newer Moodle/lecturer materials were not available. Appendix F
tables 13–19 and the two addresses in table 20 were directly verified; official schemas, exact
MCP messages, and unverified simulator details remain incomplete.
