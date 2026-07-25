# ADR-002 — Message Envelope and Idempotency

Status: **PROPOSED — UNACCEPTED**

## Context

Explicit state transitions and duplicate-safe network handling require a shared
envelope/idempotency design. The book does not prescribe fields such as
`message_id`, `sequence`, `idempotency_key`, timestamps, acknowledgement objects, or
error codes.

## Decision required

Both peers must agree on the minimum envelope, ordering scope, duplicate response,
acknowledgement semantics, validation errors, and replay/expiry behavior. Candidate
fields remain examples until that decision is recorded.

## Acceptance

- Exact schema and state-machine mapping are byte-identical.
- Tests cover missing/extra fields only to the accepted strictness.
- Duplicate delivery never double-applies an action.
- Illegal transitions and unsupported versions fail deterministically.

No invented envelope member is currently a mandatory book field.
