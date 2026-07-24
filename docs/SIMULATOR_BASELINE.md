# Simulator Baseline

## Pin

- Upstream: <https://github.com/rmisegal/Game-P2P-Cop-Chase>
- Branch observed: `master`
- Commit: `960499fd5e8777b4929625f5d8fdcf2ab4677b54`
- Commit title/date: “Release v3.0.0 — align code and guidelines-book versions to 3.0.0”, 2026-07-12
- Inspection date: 2026-07-24

The GitHub commit page and repository tree were inspected remotely. No simulator files were copied into this repository.

## Relevant observed files and symbols

The pinned repository exposes `config/`, `docs/`, `src/police_thief/`, and `tests/`. Its README points to `cli.py`, `sdk/sdk.py`, `sdk/series.py`, `peer/runtime.py`, `peer/handshake.py`, `infra/mcp_server.py`, `infra/mcp_client.py`, `domain/protocol.py`, `domain/crypto.py`, `domain/board.py`, `domain/rules.py`, `domain/brains.py`, and `report/artifacts.py`. It names simulator tools/messages such as `negotiate`, `receive_turn`, `submit_audit`, `receive_control`, `TurnMessage`, `ControlMessage`, and `AuditPayload`.

These names and shapes are simulator observations only.

## Test baseline

No checkout of the pinned simulator was available inside this repository, so no test command was run during this audit. The local secondary overview reports an earlier `uv run pytest -q` result of `246 passed, 7 failed`, but lacks a recorded commit and is therefore not reproducible evidence for the pinned baseline.

## Example-only behavior

Treat all simulator defaults—including ports 8801/8802, one sub-game, grid 7, timeouts, rate limits, configuration schema, filenames, model/provider names, and tool names—as illustrative until official sources confirm them. The simulator README itself calls the repository a learning aid and says the book and binding table win on differences.

## Known comparison conflicts

The simulator ships `num_games = 1` while its README calls six book-mandated; this repository cannot resolve that without direct Appendix F evidence. Current local documents also use incompatible version numbers and protocol terminology.
