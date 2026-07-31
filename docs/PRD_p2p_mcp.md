# PRD — Peer-to-Peer FastMCP

Status: architecture and Option-B tool names are accepted for this project. Both
transport adapters exist — the server mailbox (M5-02) and the client connector
(M5-03) — and as of 2026-08-01 negotiation (M5-04), the declared phase machine
(M5-11a), and one turn of the loop (M5-11) drive them. A negotiate round trip has
crossed a real socket between two OS processes (M5-10b).

Still missing before a whole game runs over the wire: the sub-game driver and the
end-of-game mutual audit (M5-10d, M5-10e), deadlines and retry (M5-05), and the
watchdog (M5-06).

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
no configuration itself, so it has no path to the shared match JSON (ADR-004).
`shared/private_config.py` supplies that address from `[network].opponent_url` in
the private TOML and is the only door to one; `assert_no_network_address` is the
lock on the other, refusing a shared match object that carries an address by member
name or by value (M5-03f, closed 2026-08-01).

## The turn, as driven today

`orchestration/turn_loop.run_turn` performs one iteration in the reference's order,
confirmed 2026-08-01: **await the opponent, think, apply locally, seal, send**. A
peer must receive before advancing its own step, which is what makes the
alternation strict rather than two peers talking at once. Every step is a declared
transition through `orchestration/phases.PhaseMachine`, so an out-of-order peer is
refused instead of deadlocking `[AE-4]` `[AE-5]`.

A turn is sealed **exactly once**. If delivery then fails, the record is not
re-sealed — that would give one step two commitment hashes and hand the opponent an
audit mismatch, which is an automatic zero `[AE-19]` — so the peer keeps the
commitment it made and takes the declared terminal exit.

What crosses the wire is only `step`, `sender`, `hint`, `smell_grid`, `commit`,
`timestamp` and the optional claim members. The move, the true position, the bluff
verdict, and the nonce stay private until the post-game audit. The book's phase 3
describes a live move exchange; the reference sends none, and this project follows
the reference — see `C-030`.

Still absent: the sub-game driver and mutual audit (M5-10d, M5-10e),
deadlines/retry/idempotency (M5-05), watchdog (M5-06), and tunnel (M5-07).
