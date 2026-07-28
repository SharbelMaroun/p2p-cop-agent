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
- True position, move, intent/verdict, and nonce are revealed **only** in the
  `AuditPayload` after the game. There is **no** separate live reveal tool.
- Move/negotiation commitment uses the exact canonicalization:

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

## Nonce profile

- 16 cryptographically random bytes.
- Rendered as 32 lowercase hexadecimal characters.
- Kept outside the JSON payload.
- Never disclosed before the final audit.

## Role alternation

A counted series has six sub-games. Group identity is stable; the played role
alternates: each group plays its natural role on odd sub-games (1, 3, 5) and the
opposite role on even sub-games (2, 4, 6). Scores aggregate per group.

## Acceptance scope

- ADR-001 (FastMCP tool names) is **accepted for this project** under Option B.
- The move-commit portion of ADR-006 (canonicalization, `"|"` delimiter, nonce
  profile) is **accepted for this project** under Option B.
- The rejected `0.1.0-proposed` bundle is superseded by a new `0.2.0-proposed`
  contract; copying or freezing `0.1.0-proposed` is not authorized.

See [../shared_contract/PROTOCOL_PROFILE.md](../shared_contract/PROTOCOL_PROFILE.md)
for the normative wire specification, [OPTION_B_HANDOFF.md](OPTION_B_HANDOFF.md) for
the controlled inventory, and the ADRs for the design rationale.
