# PRD — Peer-to-Peer FastMCP

Status: architecture and Option-B tool names are accepted for this project. Both
transport adapters exist — the server mailbox (M5-02) and the client connector
(M5-03) — and as of 2026-08-01 negotiation (M5-04), the declared phase machine
(M5-11a), and one turn of the loop (M5-11) drive them. A negotiate round trip has
crossed a real socket between two OS processes (M5-10b).

As of 2026-08-01 a bounded sub-game also runs end to end and reveals its audit
(M5-10d, M5-10e), with both crossing a real socket into a separate OS process.

Still missing before a *match* runs: a second peer that plays back and mutual
verification of the opponent's audit (M7), deadlines and retry (M5-05), and the
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

## Pre-game identity and the config lock (M5-04h)

The book requires the negotiation exchange to carry the team's members, repository
URLs, MCP server URLs, hardware spec, and LLM model, and both teams to lock the
agreed values with a `config_sha256`. Under the 2026-08-01 "populate ours, tolerate
theirs" decision (`C-031`), this is one-directional: `build_offer` assembles the full
identity (`protocol/identity.py`, from injected config sources — never hard-coded),
refuses to ship an incomplete one, and attaches `config_sha256` over the *whole* game
object — the same digest the artifacts use, distinct from the signed terms projection.
`verify_offer` is unchanged, so a peer that omits these still negotiates: requiring
them would refuse a simulator-built peer that keeps them in artifacts, not on the
wire, which is a contract change reserved for the coordinator (`U-029`). The identity's
URLs live on the negotiation wire precisely because the book mandates sharing them —
a different object from the shared, signed match config, which still forbids any
network address `[AE-10]`.
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

## A whole sub-game, and how it ends

Over the wire nothing can referee, because neither peer sees the other. So
termination is **claimed, answered, and only later proven**. The Cop names a cell in
`capture_claim`; only the Thief knows whether it stood there, so its `claim_response`
decides; a `win_claim` ends it the other way; and silence past the deadline is a
technical loss. Verified against the reference 2026-08-01, whose own precedence reads
capture "when a cop's `capture_claim` is **confirmed by the thief**", survival at the
threshold, then timeout.

`orchestration/sub_game.run_sub_game_over_wire` plays bounded turns, stops the moment
the game is decided, and then reveals every sealed record. The audit goes out **once
per sub-game, after the loop** — matching the reference — and is sent even when this
peer is taking the technical loss, because a withheld reveal cannot be checked and the
whole point is that the opponent recomputes it.

## Bounded waiting (M5-05a, M5-05b)

`services/deadlines.py` makes every wait finite. Book §8.4.1's boxed note is the
design — *"Missing a Deadline is a Failure, Not Patience"* — and it permits exactly
two outcomes on expiry: retry, or declare a technical loss and clear the queue.

Each attempt gets its own expiry; retries stop at `max_retries`; and an attempt that
overruns its own expiry is **not** retried, because the retry budget does not rescue
a missed deadline. Running out raises, so the caller decides rather than hanging.

The four limits are read from the **shared, signed** match object — not private
config — so neither peer can grant itself a longer rope:
`network_and_league.response_timeout_sec` (30), `.watchdog_timeout_sec` (60),
`rate_limiter_gatekeeper.retry_backoff_sec` (5), `.max_retries` (3). Key names
confirmed against the reference 2026-08-01. Time is injected, so timeouts are tested
by passing a number rather than sleeping.

## Watchdog and controlled shutdown (M5-06)

The deadline bounds one request; the watchdog bounds *overall silence*. A peer can
answer every call and still go dead between them, so `services/watchdog.py` is a
separate liveness timer that trips when nothing has happened for the agreed
`network_and_league.watchdog_timeout_sec` (60, `[AF-t19]`, `Negotiation`). Its trip is
**sticky** and its clock injected, matching `Deadline`. The heartbeat that feeds it
reuses the loop's existing per-phase `on_transition` stream (M5-11d) via
`heartbeat_on_transition` — every phase entered is a sign of life — so no new plumbing
threads through the turn loop.

`orchestration/shutdown.py` owns the trip response the book names: `persist_state()`
**then** `controlled_shutdown()`. It guarantees the ordering and, above all, is
fail-closed — a failing `persist_state` is recorded (`ShutdownReport.persisted=False`)
and the game still ends, because a shutdown that could hang is the failure the
watchdog exists to catch. Routing to `TECHNICAL_LOSS` uses only declared transitions:
a direct edge from `AWAITING_REVEAL`/`COMPUTING_MOVE`, the documented
`COMPUTING_MOVE` bridge from `WAITING_FOR_OPPONENT`, and a refusal (`ShutdownError`)
in the synchronous phases where bridging would fabricate a reveal `[AE-7]`.

The concrete snapshot **format** is the log manager's (M5-12) and the **wiring** of
persistence to a live match is the orchestrator's (M5-08); `persist_state` is an
injected seam until then.

Still absent: mutual verification of the *opponent's* audit (`M7`), the orchestrator
gateway (M5-08), the log manager (M5-12), and tunnel (M5-07).
