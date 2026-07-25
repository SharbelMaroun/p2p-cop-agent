# Official JSON Artifact Template Baseline

Status: the four supplied JSON examples are directly inspected and valid JSON. They confirm the
artifact families, schema version, exemplar key sets, cross-file identifiers, and filename
patterns. They are examples, not formal JSON Schema documents: required/optional status, complete
type constraints, enums, conditional rules, and compatibility behavior remain `UNKNOWN` until
the referenced in-code schemas or validation fixtures are available.

Source directory inspected:
`C:\Users\amrsa\OneDrive\Desktop\OrchAI\FinalProject\SimulatorEXM-Repo\Json-examples`

| Template | Bytes | SHA-256 | Scope |
|---|---:|---|---|
| `1-pre-game-declaration.json` | 3512 | `f0f54ada41b831fc666d18ba0605f656ec4ac21160a85653553bda8e574543e4` | Whole-series static declaration |
| `2-agreed-config.json` | 3746 | `4e7778d88bf53aa2d4dad0ad09c64764149d3ed0e521e578e77a3ab75773cba1` | Agreed per-sub-game configuration |
| `3-game-log.json` | 29631 | `00e783628585e85d9f7716faf337917090d5e4a5530d4bd10c239647002e71c2` | Per-peer, per-sub-game audit/replay log |
| `4-final-result.json` | 3075 | `397bf9f00cf5aa4dfc609b6add10336d267056f8c2ef333e4b32a03a85d8d204` | Whole-series final result |

All four examples use `schema_version: "1.1"` and join through `game_id`, `game_uid`, and the
`links` object. Match-level declaration/result filenames derive from `game_id`; config/log names
also include `sub_game_number`.

## Confirmed exemplar structure

- Declaration: identity, links, timezone/times, series counts/token cap, and two group objects
  containing members, Cop/Thief repositories, MCP server URLs, LLM model, hardware, and signature.
- Agreed config: board/agents, world/hints, movement/barriers, scoring, pheromones,
  network/league, Gatekeeper, identifiers, links, config filename, and `config_sha256`.
- Game log: identifiers/links, per-peer summary and audit, committed records containing payload,
  nonce, and commit, plus mutual agreement.
- Final result: identifiers/links, groups, sub-game results/roles/commits/tokens/scores/logs/audit,
  aggregate result, and mutual agreement.

## Authority boundaries

- Appendix F remains authoritative for binding parameter values and statuses.
- `network_and_league.num_games: 1` records this example run; it does not override Appendix F's
  fixed six-game series.
- `pheromone_min_center_intensity: 0.5` is present in the template but absent from Appendix F.
  It is recorded as template/simulator-specific, not promoted to a binding requirement.
- Exact MCP message names and wire payloads are not established by these reporting artifacts.
- No simulator behavior beyond what the templates directly encode is inferred.

