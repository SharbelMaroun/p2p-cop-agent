# Verification Policy

## Admission rule

A requirement is `CONFIRMED` only when its wording and scope are tied to an
authoritative source version and an exact page/table/section/template path or
commit-pinned symbol. A design choice unsupported by such wording must be marked
`PROPOSED` and owned by an ADR.

- Appendix F confirms numeric values and `Fixed`/`Minimum`/`Negotiation` status.
- Appendix E and the book body confirm mandatory/recommended behavior.
- Official course JSON examples confirm observed key sets and filename patterns, not
  unobserved formal-schema constraints.
- A simulator observation requires the exact pinned commit and remains a candidate
  when the book does not mandate it.

## Evidence record

Each record states status, authority/version, exact locator, peer/scope,
repository/test impact, and interpretation limit. Conflicts are recorded rather than
silently normalized.

## Change gates

1. Confirm the source-backed portion of the affected subsystem.
2. Isolate unresolved evidence and design decisions in the unknown register/ADR.
3. Add tests that assert only proven constraints.
4. For shared files, generate deterministic hashes and obtain independent Thief
   acceptance.
5. Freeze only after cross-repository parity succeeds.

Unresolved runtime details block only their affected runtime behavior. They do not
block source-backed documentation, fixtures, configuration models, or the
behavior-free package scaffold.
