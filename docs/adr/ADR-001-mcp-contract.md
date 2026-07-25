# ADR-001 — MCP Contract Names

Status: **PROPOSED — UNACCEPTED**

## Context

The book requires each peer to be both FastMCP server/client, with public reachability,
state/deadline controls, and verified moves. It does not mandate concrete tool names.
The pinned lecturer simulator exposes candidate names `negotiate`, `receive_turn`,
`submit_audit`, and `receive_control`.

## Proposed direction

Use the pinned names only if both peers accept them as an interoperability choice.
Do not cite them as Appendix E requirements. Signatures and payloads remain coupled
to ADR-002 and the contract fixtures.

## Acceptance

- Cop and Thief approve the same names/signatures.
- Positive/unknown-tool/invalid-transition contract tests pass in both repositories.
- The accepted bytes and hashes enter a frozen contract version.

Until then, no FastMCP handler/client behavior is authorized.
