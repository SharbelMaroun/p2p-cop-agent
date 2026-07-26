# P2P Cop Agent

This repository is the **Cop peer** for the “Distributed Cops-and-Robbers over a
Peer-to-Peer Network” final project.

> Companion Thief repository: <https://github.com/SharbelMaroun/p2p-thief-agent>

## Current milestone

This branch establishes the M0–M1 contract and package scaffold. The independently
installable Python package is `p2p_cop_agent`; it deliberately contains no game,
network, LLM, Gmail, GUI, or replay behavior.

The shared contract is `0.1.0-proposed` and **UNFROZEN**. It becomes frozen only
after the Thief repository accepts the same controlled files byte-for-byte and both
repositories pass the parity checks. Historical statements that parity was already
achieved were disproved by the hash comparison in
[docs/PARITY_REPORT.md](docs/PARITY_REPORT.md).

Evidence and decisions are tracked in:

- [requirements ledger](docs/REQUIREMENTS_LEDGER.md);
- [unknown requirements](docs/UNKNOWN_REQUIREMENTS.md);
- [specification conflicts](docs/SPECIFICATION_CONFLICTS.md);
- [source inventory](docs/SOURCE_INVENTORY.md);
- [ADRs](docs/adr/).

## Confirmed project boundary

- Cop and Thief are separate, independently runnable processes and repositories.
- They share no live memory, variables, database, runtime filesystem, or private truth.
- Each peer is both a FastMCP server and client; exact MCP names and envelope fields
  are proposed only through ADR-001 and ADR-002.
- The played-game shared configuration must be byte-identical at both peers.
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

- `config/game.json` and `config/rate_limits.json` are proposed shared files.
- `config/game.toml.example` is Cop-local and is not parity-controlled.
- `.env-example` contains dummy, provider-neutral placeholders only.

The shared configuration uses schema `1.2`; the observed reporting-artifact fixtures
remain schema `1.1`. They are separate contracts under
[ADR-003](docs/adr/ADR-003-schema-version-discrepancy.md), not silently normalized.
Both shared JSON files also carry the independent configuration revision `1.00`
required by the submission guidelines.

## Cop scope

Confirmed Cop concerns include legal pursuit, a Cop-local belief about the Thief,
Thief-scent observation, legal and disclosed barrier placement, capture, and Cop-local
strategy and verbal behavior. Exact runtime interfaces and strategy weights remain
future decisions. The safe default is deterministic movement; Appendix E rule 25 is
a recommendation, not a mandatory sanction against every LLM-assisted policy.

## Submission facts

- The final release requires an annotated Git tag; the literal tag name remains
  subject to current Moodle instructions.
- Repository sharing/general contact: `rmisegal@gmail.com`.
- Automated final-game reports: `rmisegal+uoh26finalgame@gmail.com`.
- A final report is a JSON attachment; a free-text final-report body is not accepted.

The graded README report has six sections: (1) Dec-POMDP model, (2) FastMCP
communication dilemma, (3) implemented strategy, (4) learning curves if RL is used,
(5) live-belief-map and “Verified OK” replay screenshots, and (6) the companion
repository link. Sections requiring runtime results remain pending; section 6 is the
link at the top of this README.

## Planning history

The active [plan](docs/PLAN.md) and [TODO](docs/TODO.md) govern this branch. The
635-task pre-audit backlog under `archive/pre-audit/documentation/` is historical
coverage only and will not be restored as an executable plan.

## License

The repository MIT license covers team-authored material where legally valid.
Lecturer-provided simulator material is governed by its own educational-use EULA and
is not automatically relicensed. The simulator is a learning and interoperability
reference, not a submission skeleton; substantial source reuse requires the
provenance/license decision in ADR-008 or explicit permission.
