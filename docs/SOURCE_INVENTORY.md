# Source Inventory

| Source | Availability / identity | Use and limit |
|---|---|---|
| Official project book `police_thief_p2p.pdf` v3.0.0 | Directly inspected; SHA-256 `7C9E1D7527582C3AEF9AFD71709981CEA50EA60B8FABEFE85EFCCAB0A5FDD02E` | Highest authority for rules; Appendix B/E/F and table 20 directly checked |
| Dated lecturer/Moodle clarifications | Not present in this checkout | Needed only for recency-sensitive unresolved questions |
| Professional Software Submission Guidelines v3.0 | Direct 39-page PDF previously inspected; SHA-256 `3F02DF37767C745EFC47646140C2E6AC7CAE3B9C87C92073DAF4EEF74BE09EBB` | `PS-001`–`PS-010` |
| Lecturer simulator | Public upstream pinned to `960499fd5e8777b4929625f5d8fdcf2ab4677b54` | Lower-priority learning/interoperability reference; behavior is not automatically mandatory |
| Simulator educational-use EULA | Present upstream; redistribution/adaptation restricted | ADR-008/license review before substantial reuse; no source-copy authority inferred |
| Four local JSON artifacts | Directly inspected and hashed in `ARTIFACT_TEMPLATE_BASELINE.md`; byte-identical to generated simulator logs | `NEEDS_MANUAL_REVIEW`; observed 1.1 key sets only, with no authenticated official provenance |
| Cross-team ADR accepted by both peers | None accepted for the proposed bundle yet | Project design evidence only; may decide permitted choices, never override an external authority |
| Planning repository at `0c751942fc133a4bbd7a1a3348f95800e73c81e3` | Inspected for navigation | Secondary inventory only |
| `DEV-SPEC.md`, summaries, translations, NotebookLM/AI output | Available as derived material | Navigation/cross-check only; cannot independently confirm a requirement |
| Archived repository documents | Preserved under `archive/pre-audit/` | Historical coverage only; never active implementation authority |

Direct verification already closes Appendix F values/statuses, the rule-25
recommendation status, six README sections, annotated-tag requirement, both email
addresses, the semantic shared-JSON/private-TOML override, and artifact filename
patterns stated in book table 20. The formal artifact shapes and provenance of the
four local files remain open.
