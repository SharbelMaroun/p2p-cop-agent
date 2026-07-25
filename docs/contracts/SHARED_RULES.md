# Proposed Shared Contract Rules

Contract version: `0.1.0-proposed`
Freeze status: **PROPOSED / UNFROZEN**

This bundle is a review candidate for the Cop and Thief repositories. It becomes frozen only
after the Thief team accepts the same files byte-for-byte and both repositories pass the parity
checker. The bundle contains no peer-private settings, ports, credentials, tokens, nonces, model
selection, tunnel credentials, or provider keys.

## Authority and scope

The source order is: project book v3.0.0; supplied artifact examples; lecturer simulator at
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`; dated lecturer/Moodle clarification; Professional
Software Submission Guidelines v3.0; accepted cross-team ADR; repository documents.

The shared configuration profile is the Appendix B `config/game.json` profile
(`schema_version` 1.2). The supplied reporting-artifact examples use 1.1. These are distinct
profiles, not a single silently normalized schema. See ADR-003. The simulator's runtime
`game.json` 1.3 is reference behavior only and is not adopted.

Each shared configuration JSON also has revision `version: "1.00"`, as required by
Professional Software Submission Guidelines v3.0, section 8.1. This revision is independent of
the shared-config schema profile, the reporting-artifact schema profile, and the package's code
version. Because this milestone splits the book's shared sections across two JSON files,
ADR-004 places the required revision at the root of each file.

## Mandatory shared rules

| Rule | Authority |
|---|---|
| Cop and Thief are separate processes and share no live memory, variables, database, runtime filesystem, or private truth. | Book Ch.2; Appendix E rules 1-2, PDF pp.142-143 |
| Both peers load byte-identical shared game terms for a played game. | Appendix E rule 11, PDF p.144; Appendix F mandatory rule 1, PDF p.156 |
| Movement is `N`, `S`, `E`, `W`, or `STAY`; diagonals are illegal. | Appendix E rules 13-14; Appendix F table 15 |
| Barrier placement is disclosed truthfully. A barrier on the Thief's current cell captures; a Thief with no legal move is captured. | Appendix E rules 15-16 and 46-47 |
| SHA-256 commit-reveal is mandatory; nonces remain secret until the end-game audit; a mismatch is a technical loss worth zero. | Appendix E rules 17-19 |
| Scent uses the multiplicative update `tau_ij(t+1) = max(0, (1-rho) * tau_ij(t) + delta_tau_ij)`; the simulator's subtractive variant is not adopted. | Book Ch.4, PDF pp.43/47; ADR-005 |
| A single orchestrator entry point, explicit state machine, illegal-transition rejection, deadlines, watchdog, and public tunnel are mandatory runtime requirements. | Appendix E rules 3-7 and 10 |
| A live GUI may display local truth only. | Appendix E rules 8-9 |
| Final reports are JSON attachments; a free-text final-report body is prohibited. | Appendix E rules 32-35 |
| The repository-sharing address is `rmisegal@gmail.com`; automated reports go to `rmisegal+uoh26finalgame@gmail.com`. | Appendix F table 20, PDF p.157 |
| Official artifact names are `declaration_<game_id>.json`, `config_<game_id>_g<NN>.json`, `log_<game_id>_g<NN>.json`, and `result_<game_id>.json`. | Appendix F table 20, PDF p.157 |

Rule 47's interaction with the fixed `STAY` action still needs a cross-team interpretation. This
bundle does not invent trapping behavior.

## Shared field registry

`Minimum` values may be raised by mutual agreement but not lowered. `Fixed` values cannot change.
`Negotiation default` values may change by agreement; the listed value applies otherwise.

| JSON path | Proposed value | Status | Direct authority |
|---|---|---|---|
| `game.version` | `"1.00"` | Configuration revision | Professional Software Submission Guidelines v3.0 section 8.1; ADR-004 |
| `game.schema_version` | `"1.2"` | Profile marker | Appendix B shared-config example, PDF p.129; ADR-003 |
| `game.board_and_agents.grid_size` | `7` | Minimum | Appendix F table 13, PDF p.152 |
| `game.board_and_agents.num_agents` | `2` | Fixed | Appendix F table 13, PDF p.152 |
| `game.board_and_agents.axis_origin_corner` | `"top-left"` | Negotiation default | Appendix F table 13, PDF p.152 |
| `game.board_and_agents.axis_start_index` | `0` | Negotiation default | Appendix F table 13, PDF p.152 |
| `game.board_and_agents.thief_start` | `[3,3]` | Negotiation default | Appendix F table 13, PDF p.152 |
| `game.board_and_agents.cop_start` | `[0,0]` | Negotiation default | Appendix F table 13, PDF p.152 |
| `game.world.map_area` | `"New York"` | Negotiation default | Appendix F table 14, PDF p.152 |
| `game.world.hint_max_words` | `15` | Negotiation default | Appendix F table 14, PDF p.152 |
| `game.movement_and_barriers.move_set` | `["N","S","E","W","STAY"]` | Fixed | Appendix F table 15, PDF p.153 |
| `game.movement_and_barriers.max_barriers` | `14` | Minimum | Appendix F table 15, PDF p.153 |
| `game.movement_and_barriers.max_moves` | `35` | Minimum | Appendix F table 15, PDF p.153 |
| `game.movement_and_barriers.survival_threshold` | `35` | Minimum | Appendix F table 15, PDF p.153 |
| `game.pheromones.pheromone_center_intensity` | `0.9` | Fixed | Appendix F table 16, PDF p.153 |
| `game.pheromones.pheromone_decay` | `0.10` | Fixed | Appendix F table 16, PDF p.153 |
| `game.pheromones.pheromone_grid_size` | `5` (a 5x5 field) | Fixed | Appendix F table 16, PDF p.153 |
| `game.scoring.capture_cop` / `capture_thief` | `20` / `5` | Fixed | Appendix F table 17, PDF p.154 |
| `game.scoring.survival_cop` / `survival_thief` | `5` / `10` | Fixed | Appendix F table 17, PDF p.154 |
| `game.scoring.tie_score` | `2` each | Fixed | Appendix F table 17, PDF p.154 |
| `game.scoring.technical_loss` | `0` | Mandatory outcome | Appendix E rules 19 and 48 |
| `game.network_and_league.num_games` | `6` | Fixed | Appendix F table 18, PDF p.154 |
| `game.network_and_league.diversity_reward` | `10` | Fixed | Appendix F table 18, PDF p.154 |
| `game.network_and_league.min_games_to_pass` | `2` | Fixed | Appendix F table 18, PDF p.154 |
| `game.network_and_league.max_games_per_team` | `10` | Fixed | Appendix F table 18, PDF p.154 |
| `game.network_and_league.token_budget_per_series` | `200000` | Negotiation default | Appendix F table 18, PDF p.154 |
| `rate_limits.version` | `"1.00"` | Rate-limit configuration revision | Professional Software Submission Guidelines v3.0 section 8.1; ADR-004 |
| `rate_limits.schema_version` | `"1.2"` | Profile marker | Appendix B shared-config example; ADR-003/ADR-004 split |
| `rate_limits.rate_limiter_gatekeeper.requests_per_minute` | `30` | Minimum | Appendix F table 19, PDF p.155 |
| `rate_limits.rate_limiter_gatekeeper.concurrent_requests` | `2` | Minimum | Appendix F table 19, PDF p.155 |
| `rate_limits.rate_limiter_gatekeeper.retry_backoff_sec` | `5` | Minimum | Appendix F table 19, PDF p.155 |
| `rate_limits.rate_limiter_gatekeeper.max_retries` | `3` | Minimum | Appendix F table 19, PDF p.155 |
| `rate_limits.rate_limiter_gatekeeper.queue_depth` | `100` | Minimum | Appendix F table 19, PDF p.155 |
| `rate_limits.rate_limiter_gatekeeper.response_timeout_sec` | `30` | Negotiation default | Appendix F table 19, PDF p.155 |
| `rate_limits.rate_limiter_gatekeeper.watchdog_timeout_sec` | `60` | Negotiation default | Appendix F table 19, PDF p.155 |

The field names are observed in Appendix B and the supplied agreed-config example. Separating
Gatekeeper values into `config/rate_limits.json`, strict bundle schemas, and parity mechanics are
proposed by ADR-004 and this milestone mandate.

## Artifact key-set evidence

The four fixtures under `tests/fixtures/contracts/` are safe key-set snapshots of the supplied
examples. Each records its source filename, byte hash, observed 1.1 profile, and object key sets.
They deliberately omit all example values; `["*"]` denotes redacted/dynamic map-member names,
not a literal required key. They do **not** establish formal required/optional status, complete
types, enums, conditional constraints, or compatibility.

## Decisions deliberately not frozen

- MCP tool names and payloads: ADR-001.
- Message envelope and idempotency fields: ADR-002.
- Cross-profile 1.1/1.2 compatibility: ADR-003.
- Commit canonical bytes, Unicode treatment, and nonce length: ADR-006.
- Private Cop TOML fields: ADR-004.
- Gmail draft/send workflow: ADR-010.

No gameplay, network transport, LLM, Gmail, GUI, replay, or cryptographic runtime behavior is
implemented by this bundle.
