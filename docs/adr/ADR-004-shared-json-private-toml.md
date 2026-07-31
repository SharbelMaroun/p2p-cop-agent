# ADR-004 — Shared JSON and Private TOML

Status: **ACCEPTED BOUNDARY — SHARED GAME JSON; LOCAL TOML/RATE FILE**

## Context

Appendix B directly separates byte-identical agreed JSON from local per-peer TOML.
The peers must enforce the same game physics without exposing private settings or
sharing a runtime filesystem.

## Decision

- Supply one per-match game JSON object by explicit runtime path as the authoritative
  shared constitution, including timeouts and Gatekeeper limits. Stable
  `shared_contract/` files remain specifications, schemas, fixtures, and vectors.
- Supply the per-run local rate-limit mirror by a separate explicit path. Its
  Gatekeeper object must exactly equal the authoritative shared values, while its
  local extensions and bytes remain excluded from match-byte parity.
- Put the guidelines-required configuration revision `version: "1.00"` at the root
  of each split shared JSON file and validate it independently of `schema_version`.
- Keep only Cop-local `config/game.toml.example`; never add Thief-private config here.
- Shared values override overlapping local defaults.
- Exclude secrets, ports, local opponent-URL storage, provider/model choices,
  credentials, tunnels, per-turn commitment nonces, emails used as credentials, and
  strategy tuning from the shared bundle. The public `negotiate.nonce` challenge is
  protocol data, not private configuration.

## Acceptance

- Config tests prove both paths are mandatory, the shared/private boundary, and the
  exact operational mirror.
- Private TOML and `.env` are absent from the parity manifest.
- Cop and Thief accept identical shared bytes independently.

## Settled since (2026-08-01, `M5-03f`)

The private `[network]` keys are no longer open. Confirmed against the reference and
book page 131: each peer reads its own `config/<role>/game.toml` — police and thief
from **separate directories** — and takes the opponent's address from
`[network].opponent_url`. The section also carries `my_port`, `turn_timeout_seconds`,
`poll_interval_seconds`, `connect_timeout_seconds`, `retry_interval_seconds`, and
`audit_send_timeout_seconds`. `config/game.toml.example` was realigned from an
invented `[local]` section to that skeleton.

Asked directly whether the shared negotiated JSON ever carries a URL, port, host, or
any network address, the answer was **no**: local settings must not "leak into the
agreement". `shared/private_config.py` is the only door to an opponent address, and
`assert_no_network_address` is the lock on the other — it refuses a shared match
object carrying an address either by member **name** or by **value**, because either
check alone is easy to slip past. The controlled `match_config.example.json` is
asserted clean by test.
