# Proposed Shared Contract Rules

Contract version: `0.1.0-proposed`
Freeze status: **PROPOSED / UNFROZEN**

This bundle is a Cop-authored review candidate. Local manifest verification proves
only Cop-local integrity. It becomes frozen only after Thief accepts the same files
byte-for-byte, both repositories verify locally, and read-only cross-root comparison
reports identical controlled bytes plus an identical separate manifest hash. The
bundle contains no peer-private settings, ports, credentials, tokens, nonces, model
selection, tunnel credentials, or provider keys.

## Authority and scope

The source order is: Final Project Book v3.0.0; Appendix F; Appendix E;
authenticated official JSON templates; current Moodle or dated lecturer
clarification; Software Submission Guidelines v3.0; lecturer simulator at
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`; lecture/assignment material; team notes
and AI reports.

The book's Appendix B example uses profile 1.2. Local generated artifacts use 1.1,
and the simulator runtime uses 1.3. No compatibility or normalization among these
observations is frozen. The local artifacts remain `NEEDS_MANUAL_REVIEW`.

JSON Schema identifiers, root revision fields, and closed-object policy remain
project proposals rather than formal artifact rules. Local `rate_limits.json` is
outside match-byte parity.
See `LEAGUE_CONTRACT.md`, `MATCH_CONFIGURATION.md`, and
`PRIVATE_CONFIGURATION.md` for the three-layer boundary.

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
| Book-defined artifact names are `declaration_<game_id>.json`, `config_<game_id>_g<NN>.json`, `log_<game_id>_g<NN>.json`, and `result_<game_id>.json`. | Appendix F table 20, PDF p.157 |

Rule 47's interaction with the fixed `STAY` action still needs a cross-team interpretation. This
bundle does not invent trapping behavior.

## Shared field registry

`Minimum` values may be raised by mutual agreement but not lowered. `Fixed` values
cannot change. `Negotiation default` values may change by agreement; the listed value
applies otherwise. Ownership and status are normative semantics; repository values
are a neutral proposed match instance.

| JSON path | Proposed value | Status | Direct authority |
|---|---|---|---|
| `game.version` | `"1.00"` | **PROPOSED** configuration revision | Software Submission Guidelines v3.0 section 8.1; exact root placement unconfirmed |
| `game.schema_version` | `"1.2"` | Profile marker | Appendix B shared-config example, PDF p.129; ADR-003 |
| `game.agreed_between` | two ordered public group IDs | Mandatory representation; agreed order preserved | Appendix B example; owner-supplied lecturer direction dated 2026-07-27 |
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
| `game.network_and_league.response_timeout_sec` | `30` | Negotiation default | Appendix F table 19, PDF p.155 |
| `game.network_and_league.watchdog_timeout_sec` | `60` | Negotiation default | Appendix F table 19, PDF p.155 |
| `game.network_and_league.num_games` | `6` | Fixed | Appendix F table 18, PDF p.154 |
| `game.network_and_league.diversity_reward` | `10` | Fixed | Appendix F table 18, PDF p.154 |
| `game.network_and_league.min_games_to_pass` | `2` | Fixed | Appendix F table 18, PDF p.154 |
| `game.network_and_league.max_games_per_team` | `10` | Fixed | Appendix F table 18, PDF p.154 |
| `game.network_and_league.token_budget_per_series` | `200000` | Negotiation default | Appendix F table 18, PDF p.154 |
| `game.rate_limiter_gatekeeper.requests_per_minute` | `30` | Minimum | Appendix F table 19, PDF p.155 |
| `game.rate_limiter_gatekeeper.concurrent_requests` | `2` | Minimum | Appendix F table 19, PDF p.155 |
| `game.rate_limiter_gatekeeper.retry_backoff_sec` | `5` | Minimum | Appendix F table 19, PDF p.155 |
| `game.rate_limiter_gatekeeper.max_retries` | `3` | Minimum | Appendix F table 19, PDF p.155 |
| `game.rate_limiter_gatekeeper.queue_depth` | `100` | Minimum | Appendix F table 19, PDF p.155 |
| `rate_limits.version` | `"1.00"` | **PROPOSED** operational-config revision | Software Submission Guidelines v3.0 section 8.1 |
| `rate_limits.rate_limiter_gatekeeper.*` | local non-weakening mirror of the five shared Gatekeeper values | Local operation | Simulator `ConfigManager`; shared authority remains `game.json` |

Field names are drawn from Appendix B where present and otherwise remain explicit
project proposals or local-artifact observations. Strict known-field schemas with
an extension container, root revision placement, and manifest mechanics remain
proposed. The operational rate-limit file is local and outside parity.

## Artifact key-set evidence

Four key-set fixtures under `tests/fixtures/contracts/` preserve local generated
artifact observations. Each records its source filename, byte hash, observed 1.1
profile, and object key sets. They deliberately omit all example values; `["*"]`
denotes redacted/dynamic map-member names, not a literal required key. Their official
provenance and every formal schema constraint remain unproven.

## Decisions deliberately not frozen

- MCP tool names and payloads: ADR-001.
- Message envelope and idempotency fields: ADR-002.
- Cross-profile 1.1/1.2 compatibility: ADR-003.
- Commit-reveal canonical bytes, Unicode treatment, and nonce length: ADR-006.
- Allowed participant-ID syntax beyond ordered non-empty text.
- Detailed artifact identity formats and complete formal schemas.
- Exact game-ID/UUID protocol and exhaustive artifact schemas, deferred to M7.
- Private Cop TOML fields: ADR-004.
- Gmail draft/send workflow: ADR-010.

No gameplay, network transport, LLM, Gmail, GUI, replay, or cryptographic runtime behavior is
implemented by this bundle.
