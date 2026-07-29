# ADR-001 — MCP Contract Names

Status: **ACCEPTED FOR THIS PROJECT — Option B (simulator-v3 profile), 2026-07-28**

## Context

The book requires each peer to be both FastMCP server/client, with public reachability,
state/deadline controls, and verified moves. It does not mandate concrete tool names.
The pinned lecturer simulator exposes candidate names `negotiate`, `receive_turn`,
`submit_audit`, and `receive_control`.

## Decision

Under the accepted [Option-B decision](../OPTION_B_DECISION.md), this project adopts
the pinned interoperability profile at simulator commit
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`. These are a documented project choice
where the book left the names open; they are not cited as Appendix E requirements.

Exposed FastMCP tools and their single `dict` argument:

- `negotiate(message)` — required.
- `receive_turn(message)` — required.
- `submit_audit(payload)` — required; the exposed audit endpoint.
- `receive_control(message)` — optional.

Naming discipline: `submit_audit` is the exposed endpoint, while `exchange_audit`
is only the client-side transport method (never an MCP tool). `receive_move` is
not part of this profile. Wire role values are `"police"`/`"thief"`, never `"cop"`.
A successful call returns `{"ok": true}`. Payloads are specified by the
`0.2.5-proposed` schemas and fixtures.

## Acceptance

- Accepted for this project by the 2026-07-28 coordinator decision.
- Positive/unknown-tool/invalid-transition conformance tests pass against a
  role-neutral stub (WP6).
- The accepted names/argument names are locked in the `0.2.5-proposed` bundle;
  contract freeze remains a separate, later gate.
