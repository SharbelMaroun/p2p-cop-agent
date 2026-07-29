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
- **Errors are deterministic, and separate from transport** (clarified 2026-07-29
  from reference-server inspection). Validation is transport-neutral: a message that
  fails its schema or a transition rule raises a stable `ProtocolError` in the
  peer/SDK layer. The FastMCP receive tools, however, are pure **mailboxes**: they
  enqueue the message and always return `{"ok": true}` as a transport
  acknowledgement, matching the interoperable reference wire behaviour
  (`infra/mcp_server.py`). A `ProtocolError` surfaced when the runtime **drains and
  validates** a queued message is a **game-level outcome** (rejection / technical
  loss), not a transport error. Mapping it to a transport error would be wrong twice
  over: a peer that retries on any transport exception would abort the exchange, and
  a tampered audit would never be recorded as its sender's technical loss.
  `{"ok": true}` is only a transport ack, never a validation or game result.

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
- The FastMCP server tools enqueue-and-acknowledge only; validation runs on drain
  through `InboundPeer`, so a rejection is a game outcome, not a transport error
  (M5-02).
- No invented envelope member is a mandatory wire field.
