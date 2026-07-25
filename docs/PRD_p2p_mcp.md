# PRD — Peer-to-Peer FastMCP

Status: structural architecture `CONFIRMED`; exact runtime contract blocked by `UNKNOWN`.

## Confirmed structure (cited)

- Each peer is simultaneously a **FastMCP server and client** (`SR-005`; book Ch.2 §2.3).
- Runtime is coordinated by a **single Orchestrator gateway**; subsystems (MCP connector,
  decision module, log manager, deadline tracker, watchdog) never link directly — all traffic
  passes through the gateway (`SR-009`; Appendix E rule 3).
- Game state is driven by an explicit **state machine** that **rejects illegal transitions**
  (`SR-009`; rules 4, 5). A disconnect mid-turn routes to a terminal technical-loss state
  rather than deadlocking.
- A **watchdog** and **deadline tracker** guard against freezes: past a deadline a request is a
  failure (retry or technical loss); the watchdog persists state and shuts down cleanly on
  silence (rules 6, 7).
- The local server is exposed publicly through a **tunnel** (ngrok/Localtonet) (rule 10).
- Every incoming move is verified before it is accepted; an unverified move is never trusted.

## Pending / UNKNOWN

- Exact MCP **tool names**, message fields, acknowledgement flow, and ordering — `U-003`
  (needs official protocol evidence or the centralized simulator export).
- Response timeout (30 s) and watchdog threshold (60 s) are directly confirmed in
  [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md). Exact ports, retry semantics, and schemas
  remain `UNKNOWN`.
- Concrete transport/serialization schema — pending official templates.

No FastMCP runtime, tool, or transport code is authorized until the above are `CONFIRMED`.
