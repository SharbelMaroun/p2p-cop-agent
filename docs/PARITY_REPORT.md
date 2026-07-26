# Baseline Cross-Repository Parity Report

Status: **NO PARITY ESTABLISHED**.

Comparison:

- Cop commit: `72c05a18ba7a9a7fe14dad2ecb85034c64fa310a`
- locally available Thief `origin/main`:
  `119fa911d5b1a5aecdaa9531d0912e5c6f9ab32f`
- method: SHA-256 over the exact committed Git blob payload returned by
  `git cat-file blob <commit>:<path>`. These are not working-tree hashes and are not
  affected by checkout newline conversion.

| Path | Cop Git-blob SHA-256 | Thief-main Git-blob SHA-256 | Result |
|---|---|---|---|
| `docs/SHARED_REQUIREMENT_BASELINE.md` | `11a0b823722e94e7b14a641d5bc9af34e07a2fcc39c24b6849dd71529fe797e7` | `eee8bbc89b1d32f02aea480ea5bbc95157418f346afb2728d83134632fef72af` | Different |
| `docs/SPECIFICATION_CONFLICTS.md` | `889a29d59c397a150f222f22feb9c8d909b3336665ddabbc7b31ce7462589ac9` | `298e6cf913dab6d850e74f7f392989eaeae36f139925cf8328cc794f3a3d8882` | Different |
| `docs/SUBMISSION_CHECKLIST.md` | `25ce38808dfe479e4d67e620f97fd28f39a0d369b4d7a6ea49240dd0c20857f6` | — | Missing on Thief main |
| `docs/DOCS_COMPLETENESS.md` | `c9ab30103cd725d85576a77a161a7516bfcd2c7688b22d7835eef93a34ea96fe` | — | Missing on Thief main |
| `docs/REQUIREMENTS_LEDGER.md` | `5a89d2c01bab5f2a4849cebf734c0036503d5d92d7662b2c4affdfe229729651` | `324055f9f9437123198951160a4b9fad34c30900afe00112bd365a3ee5fc59c7` | Different |
| `docs/UNKNOWN_REQUIREMENTS.md` | `4863432b1859ac00b7d5fea637f284be9ff8f5d110a5d473d17831af0b8ff8d4` | `d06661ac588d574649c69bb2344184983c8b2eaa2ba75916d7c8065b8c91d277` | Different |

## Material semantic differences

- The Cop shared baseline contains `SR-007`–`SR-010` and `PS-010`; the Thief
  baseline at the compared commit does not.
- Cop resolves the six-section README mapping; Thief still marks it conflicted.
- Thief’s ledger has fine-grained Appendix E/F and JSON-template entries not present
  under the same IDs/wording in the Cop ledger; Cop uses coarser `SR-011`–`SR-013`.
- Thief still lists the README-section and tag requirements as unknown; Cop records
  them as directly confirmed.
- Two Cop documents that claimed byte identity do not exist on the compared Thief
  main.

This report disproves historical parity claims; it is not the manifest for the new
bundle. The proposed `0.1.0-proposed` contract stays **UNFROZEN** until the Thief
repository accepts its exact controlled-file list and both repositories produce
matching hashes.
