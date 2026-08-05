# Option-B Interoperability Decision

Status: **ACCEPTED PROJECT DECISION — dated 2026-07-28**

## Summary

The project exercises the course's academic-freedom rule and selects **Option B**:
the `simulator-v3` interoperability profile. Where the Final Project Book leaves a
concrete wire choice open and authoritative sources conflict, this profile fixes
one precise, interoperable answer so that two independently written peers can play.

This is a documented **project/lecturer decision for interoperability**. It does
**not** assert that the lecturer simulator repository is generally more
authoritative than the book. The book remains authority 1; Option B only selects
among designs the book left open (tool names, message envelope, move-commit bytes).

## Pinned upstream baseline

The interoperability profile is pinned to lecturer simulator commit:

```
960499fd5e8777b4929625f5d8fdcf2ab4677b54
```

Behavioural parity is measured against this exact commit. The simulator is a
reference for the wire profile only; its source is not copied into this repository
(ADR-008 still governs reuse).

## Selected FastMCP tools

| Tool | Argument | Role | Required |
|---|---|---|---|
| `negotiate` | `message: dict` | agree per-match terms | yes |
| `receive_turn` | `message: dict` | receive an opponent turn | yes |
| `submit_audit` | `payload: dict` | exposed end-game audit endpoint | yes |
| `receive_control` | `message: dict` | optional control channel | optional |

Naming rules that must not be confused:

- `submit_audit` is the **exposed MCP endpoint**.
- `exchange_audit` is **only the client-side transport method name**; it is not an
  MCP tool and is never exposed as one.
- `receive_move` is **not** part of the selected full profile.
- Wire role values are `"police"` and `"thief"`. The internal package role
  `"cop"` is never sent on the wire.
- A successful FastMCP tool call returns `{"ok": true}` as the transport
  acknowledgement; it is not a game result.

## Commit-reveal behaviour

- A `TurnMessage` exposes only public event fields: `hint`, `smell_grid`,
  `commit`, and the allowed optional public events.
- True position, move, intent/verdict, and the per-turn commitment nonce are
  revealed **only** in the `AuditPayload` after the game. There is **no** separate
  live reveal tool.
- Per-turn commitment uses the exact canonicalization:

  ```python
  canonical = json.dumps(
      payload,
      sort_keys=True,
      ensure_ascii=False,
      separators=(",", ":"),
      allow_nan=False,
  )
  commit = sha256((canonical + "|" + nonce).encode("utf-8")).hexdigest()
  ```

  The delimiter between canonical payload and nonce is the single literal
  character `"|"`.

## Nonce domains

- The per-turn commitment nonce is 16 cryptographically random bytes, rendered as
  32 lowercase hexadecimal characters, kept outside the committed JSON payload,
  and never disclosed before the final audit.
- `negotiate.nonce` is a separate public pre-play challenge. It uses the same
  32-lowercase-hex wire shape but is not a commitment nonce and is not secret.
- The commitment nonce is generated independently and must not reuse or derive from
  the public challenge. Sharing a wire shape does not merge their lifecycles.

## M1.5 configuration boundary confirmation

- The stable `shared_contract/` bundle contains specifications, schemas, fixtures,
  vectors, and verification tooling only. It contains no active match.
- Every real match object is supplied explicitly; the example fixture is never a
  runtime default.
- Every run also supplies a local rate-limit enforcement mirror explicitly. The
  signed match object's Gatekeeper block is authoritative and the local mirror must
  equal it exactly; mirror bytes and local extensions are not parity-controlled.

## Role alternation — UNKNOWN, NOT BINDING

Status: **UNKNOWN** (`U-025`, `OB-005`). Withdrawn from the contract bundle in
`0.2.1-proposed`.

Confirmed: a counted series has six sub-games, group identity is stable, and
scores aggregate per group (Appendix F table 18).

**Not** confirmed: the role schedule within the series. The observed pattern —
each group plays its natural role on odd sub-games (1, 3, 5) and the opposite
role on even sub-games (2, 4, 6) — appears in the pinned simulator only. The
book does not state it, and the recorded lecturer direction of 2026-07-27 is a
transcription, not an authenticated Moodle announcement or original lecturer
message. Under this project's own source-authority rules, simulator behaviour is
a compatibility reference and cannot make a rule binding.

Until an authenticated lecturer answer or a direct book citation arrives, series
orchestration must stay role-agnostic and no normative test may assert the
schedule.

## Acceptance scope

- ADR-001 (FastMCP tool names) is **accepted for this project** under Option B.
- The per-turn-commit portion of ADR-006 (canonicalization, `"|"` delimiter, and
  commitment-nonce profile) is **accepted for this project** under Option B.
- The rejected `0.1.0-proposed` bundle is superseded by `0.2.0-proposed`, then by
  `0.2.1-proposed`, `0.2.2-proposed`, `0.2.3-proposed`, `0.2.4-proposed`, and
  `0.2.6-proposed`; copying or freezing any earlier bundle is not authorized.
- Role alternation is **not** accepted under Option B. It is recorded as `U-025`
  and carries no contract status.

See [../shared_contract/PROTOCOL_PROFILE.md](../shared_contract/PROTOCOL_PROFILE.md)
for the normative wire specification, [OPTION_B_HANDOFF.md](OPTION_B_HANDOFF.md) for
the controlled inventory, and the ADRs for the design rationale.
