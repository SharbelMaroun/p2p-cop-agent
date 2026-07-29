# PRD — Peer-to-Peer FastMCP

Status: architecture and Option-B tool names are accepted for this project;
runtime envelope error/order details remain M4 work and transport remains M5.

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

The project accepts `negotiate`, `receive_turn`, `submit_audit`, and optional
`receive_control` under ADR-001's Option-B profile. They are project interoperability
choices, not book-mandated names. ADR-002 owns the remaining runtime
envelope/idempotency semantics. Official reporting-artifact templates do not define
the MCP wire schema.

Appendix F confirms 30-second response and 60-second watchdog negotiation defaults.
Ports and retry/watchdog transport behavior remain M5 work. Successful acknowledgement
and duplicate keys are fixed by the Option-B profile; deterministic error mapping and
state-machine ordering remain M4 work.

Contract fixtures/models are allowed now; no FastMCP handler, client, tunnel, or
transport runtime is implemented.
