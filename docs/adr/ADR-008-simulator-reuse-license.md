# ADR-008 — Simulator Reuse and License

Status: **PROPOSED — NO SUBSTANTIAL COPY**

## Context

The lecturer simulator at commit
`960499fd5e8777b4929625f5d8fdcf2ab4677b54` is a learning/interoperability
reference. Its educational-use EULA is not the MIT license used for team-authored
repository material and restricts redistribution/adaptation.

## Proposed decision

- Inspect and execute behavior/tests for learning and interoperability evidence.
- Record every adopted observation with commit/file/symbol provenance.
- Reimplement from authoritative requirements and accepted contracts.
- Do not copy substantial source, publish derivatives, or treat it as a submission
  skeleton without documented license review and, where required, written permission.

## Acceptance

- Clean-room/provenance check finds no copied simulator runtime.
- Any future reuse lists exact source, license basis, attribution, and permission.
- Book/template behavior wins over simulator deviations.
