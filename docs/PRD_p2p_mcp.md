# PRD — Peer-to-Peer FastMCP

Status: architecture is confirmed; names, envelope, idempotency, and transport
details are proposed only through ADR-001/002.

## Confirmed behavior

- Each peer is both a FastMCP server and client.
- A single Orchestrator gateway coordinates the local connector, decision service,
  log manager, deadline tracker, and watchdog.
- An explicit state machine rejects illegal transitions. Deadline/disconnect paths
  cannot silently deadlock.
- A watchdog monitors silence and terminal failure handling.
- Each local server is exposed through a public tunnel. `ngrok` and `Localtonet` are
  examples, not mandated providers.
- Incoming moves are verified before acceptance.

Sources: book Ch. 2/8; Appendix E rules 3–7/10; `SR-005`/`SR-009`/`SR-017`.

## Contract boundary

The pinned simulator names `negotiate`, `receive_turn`, `submit_audit`, and
`receive_control` are interoperability candidates, not book-mandated names.
ADR-001 selects tool names; ADR-002 selects envelope/idempotency semantics. Official
reporting-artifact templates do not define the MCP wire schema.

Appendix F confirms 30-second response and 60-second watchdog negotiation defaults.
Ports, retry semantics, error/ack fields, ordering, serialization, and duplicate
handling remain unfrozen.

Contract fixtures/models are allowed now; no FastMCP handler, client, tunnel, or
transport runtime is implemented.
