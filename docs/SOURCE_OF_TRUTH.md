# Source of Truth

## Status vocabulary

- `CONFIRMED`: direct authoritative evidence.
- `CONFLICT`: authoritative sources/examples differ and the difference is isolated.
- `UNKNOWN`: evidence or a required cross-team decision is still missing.
- `PROPOSED`: an ADR/contract choice offered for acceptance; not frozen.

## Authority order

1. Official assignment book `police_thief_p2p.pdf` v3.0.0, including Appendices.
2. Official course JSON templates/examples.
3. Lecturer simulator at exact commit
   `960499fd5e8777b4929625f5d8fdcf2ab4677b54`.
4. Dated lecturer/Moodle clarification.
5. Professional Software Submission Guidelines v3.0.
6. Cross-team ADR accepted by both peers.
7. Current active repository documents.
8. Archived documents, NotebookLM text, summaries, translations, and AI output.

Higher authority wins. Simulator behavior remains a reference rather than an
automatic assignment rule, and its educational-use EULA remains controlling for
reuse. An accepted ADR may select among permitted designs but cannot weaken a
confirmed rule or minimum.

## Directly inspected evidence

- Official book: 160 pages; SHA-256
  `7C9E1D7527582C3AEF9AFD71709981CEA50EA60B8FABEFE85EFCCAB0A5FDD02E`.
  Relevant Chapter 2/4/5/7/9 and Appendix B/C/E/F text was checked directly.
- Professional Guidelines v3.0: 39 pages; SHA-256
  `3F02DF37767C745EFC47646140C2E6AC7CAE3B9C87C92073DAF4EEF74BE09EBB`.
- Four official artifact examples: hashes and limits recorded in
  [ARTIFACT_TEMPLATE_BASELINE.md](ARTIFACT_TEMPLATE_BASELINE.md).

The template key sets are available; their complete formal required/optional,
type/enum, conditional, and compatibility rules are not. That distinction replaces
the former false statement that the official templates were unavailable.
