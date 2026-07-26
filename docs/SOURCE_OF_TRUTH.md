# Source of Truth

## Status vocabulary

- `CONFIRMED`: direct authoritative evidence.
- `CONFLICT`: authoritative sources/examples differ and the difference is isolated.
- `UNKNOWN`: evidence or a required cross-team decision is still missing.
- `PROPOSED`: an ADR/contract choice offered for acceptance; not frozen.

## Authority order

1. Final Project Book `police_thief_p2p.pdf` v3.0.0.
2. Appendix F.
3. Appendix E.
4. Authenticated official JSON templates, when provenance is available.
5. Current Moodle instructions or dated lecturer clarification.
6. Software Submission Guidelines v3.0.
7. Lecturer simulator at exact commit
   `960499fd5e8777b4929625f5d8fdcf2ab4677b54`.
8. Lecture and assignment material.
9. Team notes, translations, archived documents, summaries, and AI reports.

Higher authority wins. Simulator behavior remains a reference rather than an
automatic assignment rule, and its educational-use EULA remains controlling for
reuse. Repository ADRs are design records, not external authorities. An accepted ADR
may select among permitted designs but cannot weaken a confirmed rule or minimum.

## Directly inspected evidence

- Official book: 160 pages; SHA-256
  `7C9E1D7527582C3AEF9AFD71709981CEA50EA60B8FABEFE85EFCCAB0A5FDD02E`.
  Relevant Chapter 2/4/5/7/9 and Appendix B/C/E/F text was checked directly.
- Professional Guidelines v3.0: 39 pages; SHA-256
  `3F02DF37767C745EFC47646140C2E6AC7CAE3B9C87C92073DAF4EEF74BE09EBB`.
- Four local JSON artifacts: exact bytes and hashes are recorded in
  [ARTIFACT_TEMPLATE_BASELINE.md](ARTIFACT_TEMPLATE_BASELINE.md). They are
  byte-identical to generated simulator output, so their claimed official provenance
  is `NEEDS_MANUAL_REVIEW`.
- Project-owner transcription dated 2026-07-27:
  [LECTURER_DIRECTION_2026-07-27.md](LECTURER_DIRECTION_2026-07-27.md). It records
  current lecturer direction as supplied by the owner and distinguishes direct
  book/file corroboration from claims still needing an original Moodle/lecturer
  source.

The observed key sets are useful non-authoritative evidence. They do not establish
formal required/optional, type/enum, conditional, or compatibility rules. Only an
authenticated course handoff can promote them to official-template evidence.
