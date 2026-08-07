# `simulator-v3.0.0` Compatibility Profile

Contract version: `0.2.10-proposed`
Status: **PROPOSED / UNFROZEN**

This document records the project's `simulator-v3.0.0 compatibility profile`,
source-derived from the pinned simulator snapshot at
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`. It is a compatibility target only,
not an authenticated course handoff, book requirement, or lecturer mandate. The
JSON Schemas in `schemas/` and the fixtures in `fixtures/` are its
machine-checkable form.

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

Public agreement: `terms` (the exact `terms_from_config()` projection), a public
32-lowercase-hex `nonce` challenge, a 64-lowercase-hex SHA-256 `signature`, and
`identity`. The required term names are `board_size`, `smell_grid_size`,
`decay_per_step`, `emit_intensity`, `max_steps`, `barriers_max`, `setting`,
`hint_max_words`, `axis_origin_corner`, `axis_start_index`, `thief_start`,
`cop_start`, and `num_games`. `min_center_intensity` is an optional
simulator-profile field only: Appendix F table 16 fixes center intensity `0.9`,
decay `0.10`, and the 5×5 field but defines no such floor, so it is tolerated when
a peer sends it and never required.

The source identity fields are `group_id`, `group_name`, `members`, `repos`,
`mcp_servers`, `llm_model`, and `spec`; it does not carry a role. Identity is not
covered by the signature and the compatibility schema does not invent mandatory
identity subfields. The negotiation challenge is sent before play and is not a
per-turn commitment nonce. See `schemas/negotiate.schema.json`.

### `TurnMessage` (`receive_turn`)

Public event only. Required: `step`, `sender`, `hint`, `smell_grid`, `commit`,
`timestamp`. Optional public events: `barrier_placed`, `capture_claim`,
`claim_response`, `win_claim`. `smell_grid` is a cell map such as
`{"2,3": 0.6}`, not a matrix. Barrier and capture claims are coordinate pairs or
null; claim responses and win claims are objects or null. Source serialization
includes absent optional events as explicit null values. See
`schemas/turn-message.schema.json`.

A `TurnMessage` never exposes the true position, the move, intent/verdict, or its
per-turn commitment nonce. Those are revealed only after the game in the
`AuditPayload`. There is no separate live reveal tool.

### `AuditPayload` (`submit_audit`)

Post-game reveal: `sender`, `records`, and `result_claim`. Each audit `record`
carries `payload`, its revealed per-turn commitment `nonce`, and `commit`. See
`schemas/audit-payload.schema.json` and `schemas/audit-record.schema.json`.
`result_claim` is exactly one of the simulator-v3.0.0 wire strings `capture`,
`survival`, or `timeout`, so a conforming peer's audit is never rejected on this
field. The book's Tie outcome (Appendix F table 17) is a scoring result, not a wire
value — it is modelled in the scoring layer, not claimed here. Technical loss is
adjudicated from a commit-reveal mismatch (Appendix E rules 19/48), not
self-claimed, so it is not a `result_claim` value.

### `ControlMessage` (`receive_control`, optional)

Optional out-of-band control channel; see `schemas/control-message.schema.json`.
Per ADR-001 this tool is optional, not required.

## Commit-reveal

A per-turn commitment binds a hidden payload with a secret commitment nonce:

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
- The commitment nonce is 16 cryptographically random bytes rendered as 32
  lowercase hex characters, kept outside the JSON payload and never disclosed
  before the audit. It is distinct from the public `negotiate.nonce` challenge.
- At audit time, each record's `payload` + `nonce` must reproduce its `commit`.

## Golden compatibility data

`fixtures/simulator-v3.0.0-wire.golden.json` records source-derived negotiation,
normal-turn, claim-turn, and audit wire objects. The normal turn includes all four
optional event fields as null. Capture and win data are kept in separate,
role-appropriate turn examples.

`vectors/simulator-v3.0.0-commit.golden.json` records exact ASCII and non-ASCII
commitment hashes. The non-ASCII vector includes its unescaped canonical JSON so
the `ensure_ascii=False` behavior is checked directly. Both files are explicitly
labelled `simulator-v3.0.0` and are compatibility evidence only.

## Duplicate safety (adapter behavior)

This behavior is an adapter concern and does not change the compatibility-profile wire
payload; exact v3 opponents never send extra envelope fields:

- Duplicate with the same `sender`/`step`/`commit`: acknowledge with
  `{"ok": true}` without applying the effect twice.
- Same `sender`/`step` with a different `commit`: a deterministic protocol
  conflict.
- A duplicated audit or negotiation payload: deduplicate by canonical digest.

Do not invent mandatory envelope fields such as `protocol_version`, `message_id`,
`idempotency_key`, or `sequence`; exact v3 opponents will not send them.
