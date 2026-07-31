# PRD — Peer-to-Peer FastMCP

Status: architecture and Option-B tool names are accepted for this project. Both
transport adapters now exist — the server mailbox (M5-02) and the client connector
(M5-03) — but no negotiation, deadline, watchdog, tunnel, or turn loop drives them,
so no game has yet been played over the wire.

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

## Client connector contract (M5-03)

`adapters.FastMCPClient` is the outbound half and implements `peer.PeerTransport`.
It is one of only two modules that import `fastmcp`; a guard test walks `src/` and
fails on any other importer.

**Call shapes.** One tool, one argument, no envelope. The keyword comes from
`peer.TOOL_ARGUMENTS`, so the inbound handler and the outbound client cannot drift
apart:

| Tool | Argument |
|---|---|
| `negotiate` | `message` |
| `receive_turn` | `message` |
| `submit_audit` | `payload` |
| `receive_control` | `message` |

**Fault mapping.** Two disjoint exception types, neither inheriting the other:

| Condition | Raised | Meaning |
|---|---|---|
| Unreachable host, timeout, carrier error | `TransportError` | The exchange failed. Retry, or declare a technical loss |
| Reply is not a JSON object | `TransportError` | The peer did not speak the wire |
| Reply is a JSON object that is not `{"ok": true}` | `PeerRejectionError` | The peer was reached and declined. A **game outcome** under ADR-002, never a retry |

Keeping these separate matters: collapsing them would make a peer that legitimately
refuses look like a flaky network, and a retry loop would then hide a lost game.
Appendix E rules 6/7 require the opposite — failures must surface, not be waited out.

**Statelessness.** Each call opens and closes its own session, and `__slots__`
leaves nowhere for per-turn state to hide, so no turn can leak context into the
next one.

**Configuration boundary.** The client receives its `target` explicitly and reads
no configuration itself, so it has no path to the shared match JSON (ADR-004). The
private-TOML loader that will supply the opponent URL is not built yet, so `M5-03f`
stays open.

Still absent: negotiation logic (M5-04), deadlines/retry/idempotency (M5-05),
watchdog (M5-06), tunnel (M5-07), and the turn loop (M5-11). The server adapter
mailboxes and acknowledges; the client sends and classifies. Nothing yet drives
them as a game.
