# P2P Cop Agent

This repository is the **Cop peer** for the “Distributed Cops-and-Robbers over a
Peer-to-Peer Network” final project.

> Companion Thief repository: <https://github.com/SharbelMaroun/p2p-thief-agent>

## Current milestone

This branch provides a corrected, reviewable M1 contract candidate and the
independently installable `p2p_cop_agent` scaffold. It deliberately contains no
game, network, cryptographic runtime, LLM, Gmail, GUI, or replay behavior. The
controlling audit keeps M2 blocked.

The shared contract is `0.1.0-proposed` and **UNFROZEN**. It becomes frozen only
after P0 contract questions are resolved, the coordinator accepts the candidate,
and Thief independently consumes and verifies identical controlled bytes. The local
checker proves Cop-local integrity only unless `--compare-root` is explicitly used.
Historical parity claims were disproved by
[docs/PARITY_REPORT.md](docs/PARITY_REPORT.md).

Evidence and decisions are tracked in:

- [requirements ledger](docs/REQUIREMENTS_LEDGER.md);
- [unknown requirements](docs/UNKNOWN_REQUIREMENTS.md);
- [specification conflicts](docs/SPECIFICATION_CONFLICTS.md);
- [source inventory](docs/SOURCE_INVENTORY.md);
- [candidate handoff](docs/CONTRACT_CANDIDATE_HANDOFF.md);
- [ADRs](docs/adr/).

## Confirmed project boundary

- Cop and Thief are separate, independently runnable processes and repositories.
- They share no live memory, variables, database, runtime filesystem, or private truth.
- Each peer is both a FastMCP server and client; exact MCP names and envelope fields
  are proposed only through ADR-001 and ADR-002.
- The played-game shared configuration must be byte-identical at both peers.
- A counted series has six sub-games. Each peer plays its natural role on odd games
  and the opposite role on even games.
- Legal movement is north, south, east, west, or stay; diagonals are illegal.
- Barrier placement is disclosed. A barrier on the Thief’s current cell captures the
  Thief, and a Thief with no legal move is captured.
- SHA-256 commit-reveal, secret nonces until final reveal, illegal-transition
  rejection, public tunnels, deadlines, and watchdogs are mandatory.
- The live GUI may display local truth only.

Confirmed values and their `Fixed`, `Minimum`, or `Negotiation` status are recorded
in [docs/PARAMETERS_BASELINE.md](docs/PARAMETERS_BASELINE.md). Four inspected local
JSON artifacts preserve generated key-set observations, but their claimed official
provenance is `NEEDS_MANUAL_REVIEW`; book table 20 independently establishes the
filename patterns. See
[docs/ARTIFACT_TEMPLATE_BASELINE.md](docs/ARTIFACT_TEMPLATE_BASELINE.md).

## Installation and checks

Use `uv` only:

```text
uv sync --frozen
uv run ruff check .
uv run pytest --cov --cov-branch --cov-fail-under=85
uv run python scripts/check_file_lengths.py
uv run python scripts/check_secrets.py
uv run python scripts/check_shared_contracts.py
```

These are verification commands, not claims that a live Cop peer is runnable yet.
The code/CLI version is exactly `1.00` from
`src/p2p_cop_agent/shared/version.py`; Python distribution metadata canonically
displays the equivalent PEP 440 form `1.0`.

## Configuration

- `config/game.json` is the authoritative shared constitution. Its complete parsed
  object has canonical SHA-256
  `adac9efe6d51b9487c400a04c2e185af9fb3622e1a7d74f18d400425656d82db`.
- `config/rate_limits.json` is an operational mirror whose Gatekeeper values must
  match the signed game configuration.
- `config/game.toml.example` is Cop-local and is not parity-controlled.
- `.env-example` contains dummy, provider-neutral placeholders only.

The candidate accepts only book-example profile `1.2`. Local generated artifacts
observe `1.1`, and the simulator runtime observes `1.3`; no translation or
compatibility is inferred. Root revision `1.00`, operational-mirror parity scope,
and closed known-field schemas remain explicitly proposed.

## Cop scope

Confirmed Cop concerns include legal pursuit, a Cop-local belief about the Thief,
Thief-scent observation, legal and disclosed barrier placement, capture, and Cop-local
strategy and verbal behavior. The graded strategy must replace the simple baseline
with smarter pure-Python move logic. LLM movement is disabled unless a future shared
contract revision is mutually agreed; optional banter remains a separate local
layer. Exact runtime interfaces and strategy weights remain future decisions.

## Submission facts

- The final release requires the annotated Git tag `v1.0-submission`, with a final
  current-Moodle verification immediately before tagging.
- Repository sharing/general contact: `rmisegal@gmail.com`.
- Automated final-game reports: `rmisegal+uoh26finalgame@gmail.com`.
- A final report is a JSON attachment; a free-text final-report body is not accepted.
- Both teams independently send a byte-identical copy of their mutually agreed
  result artifact.

The graded README report has six sections: (1) Dec-POMDP model, (2) FastMCP
communication dilemma, (3) implemented strategy, (4) learning curves if RL is used,
(5) live-belief-map and “Verified OK” replay screenshots, and (6) the companion
repository link. Sections requiring runtime results remain pending; section 6 is the
link at the top of this README.

## Planning history

The active M0–M9 [plan](docs/PLAN.md) and Cop-only [TODO](docs/TODO.md) govern this
branch. The
635-task pre-audit backlog under `archive/pre-audit/documentation/` is historical
coverage only and will not be restored as an executable plan.

## License

The repository MIT license covers team-authored material where legally valid.
Lecturer-provided simulator material is governed by its own educational-use EULA and
is not automatically relicensed. The simulator is a learning and interoperability
reference, not a submission skeleton; substantial source reuse requires the
provenance/license decision in ADR-008 or explicit permission.
