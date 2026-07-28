# Option-B Protocol Profile

Contract version: `0.2.1-proposed`
Status: **PROPOSED / UNFROZEN**

This is the normative wire specification for the Option-B interoperability profile,
pinned to lecturer simulator commit `960499fd5e8777b4929625f5d8fdcf2ab4677b54`. The
JSON Schemas in `schemas/` and the fixtures in `fixtures/` are the machine-checkable
form of this document.

## FastMCP tools

Each peer exposes these FastMCP tools; every tool takes a single JSON object and
returns `{"ok": true}` on successful transport acknowledgement.

| Tool | Argument | Required | Purpose |
|---|---|---|---|
| `negotiate` | `message` | yes | agree per-match terms before play |
| `receive_turn` | `message` | yes | deliver one opponent turn |
| `submit_audit` | `payload` | yes | deliver the end-game audit (exposed endpoint) |
| `receive_control` | `message` | optional | out-of-band control channel |

Naming discipline:

- `submit_audit` is the exposed MCP endpoint. `exchange_audit` is only the
  client-side transport method name and is never exposed as an MCP tool.
- `receive_move` is **not** part of this profile.
- Wire role values are `"police"` and `"thief"`. The internal package role `"cop"`
  never appears on the wire.
- `{"ok": true}` is a transport acknowledgement, not a game result.

## Messages

### `negotiate` message

Public per-match agreement: `terms` (the per-match game object projection),
`nonce`, `signature`, and `identity`. See `schemas/negotiate.schema.json`.

### `TurnMessage` (`receive_turn`)

Public event only. Required: `step`, `sender`, `hint`, `smell_grid`, `commit`,
`timestamp`. Optional public events: `barrier_placed`, `capture_claim`,
`claim_response`, `win_claim`. See `schemas/turn-message.schema.json`.

A `TurnMessage` never exposes the true position, the move, intent/verdict, or the
nonce. Those are revealed only after the game in the `AuditPayload`. There is no
separate live reveal tool.

### `AuditPayload` (`submit_audit`)

Post-game reveal: `sender`, `records`, and `result_claim`. Each audit `record`
carries `payload`, `nonce`, and `commit`. See `schemas/audit-payload.schema.json`
and `schemas/audit-record.schema.json`.

### `ControlMessage` (`receive_control`, optional)

Optional control channel; see `schemas/control-message.schema.json`.

## Commit-reveal

A commitment binds a hidden payload with a secret nonce:

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

- The domain-separation delimiter is the single literal character `"|"`.
- The nonce is 16 cryptographically random bytes rendered as 32 lowercase hex
  characters, kept outside the JSON payload and never disclosed before the audit.
- At audit time, each record's `payload` + `nonce` must reproduce its `commit`.

## Duplicate safety (adapter behavior)

This behavior is an adapter concern and does not change the mandatory v3 wire
payload; exact v3 opponents never send extra envelope fields:

- Duplicate with the same `sender`/`step`/`commit`: acknowledge with
  `{"ok": true}` without applying the effect twice.
- Same `sender`/`step` with a different `commit`: a deterministic protocol
  conflict.
- A duplicated audit or negotiation payload: deduplicate by canonical digest.

Do not invent mandatory envelope fields such as `protocol_version`, `message_id`,
`idempotency_key`, or `sequence`; exact v3 opponents will not send them.
