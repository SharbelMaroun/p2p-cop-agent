# ADR-002 — Message Envelope and Idempotency

Status: **ACCEPTED FOR THIS PROJECT — Option B (simulator-v3 profile), 2026-07-28**

## Context

Explicit state transitions and duplicate-safe network handling require a shared
envelope/idempotency design. The book does not prescribe fields such as
`message_id`, `sequence`, `idempotency_key`, timestamps, acknowledgement objects, or
error codes.

## Decision

Under the accepted [Option-B decision](../OPTION_B_DECISION.md), the envelope is
**minimal**: the wire payload of each tool call is exactly the message defined by
its `shared_contract/schemas/*` schema, with no extra mandatory envelope member.
Concretely:

- No `protocol_version`, `message_id`, `idempotency_key`, or `sequence` is required
  or sent; exact v3 opponents do not send them, and inventing them would break
  interoperability.
- **Ordering** is carried by the message's own `step` field per `sender`; a turn's
  step must strictly advance for that sender.
- **Idempotency is adapter behaviour, not a wire field.** Duplicate delivery of the
  same `(sender, step, commit)` is acknowledged with `{"ok": true}` without applying
  the effect twice. The same `(sender, step)` with a different `commit` is a
  deterministic protocol conflict. Audit and negotiation payloads deduplicate by
  canonical digest. This behaviour never changes the mandatory v3 payload.
- **Errors are deterministic.** A message that fails its schema or a transition rule
  raises a stable `ProtocolError` (transport-neutral); the FastMCP adapter (M5) maps
  that to a transport error. A successful call returns `{"ok": true}`.

This is a documented Option-B project choice, not an Appendix E requirement. It does
not add or modify any controlled `shared_contract/` file; the message schemas already
express it.

## Acceptance

- Accepted for this project by the 2026-07-28 coordinator decision, consistent with
  the already-accepted Option-B profile and `PROTOCOL_PROFILE.md`.
- The transport-neutral message surface validates every Option-B message against its
  schema and rejects malformed messages with `ProtocolError` (M4-01).
- Duplicate delivery never double-applies; illegal transitions and conflicting
  commits fail deterministically (M4-03/M4-04).
- No invented envelope member is a mandatory wire field.
