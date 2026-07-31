# P2P Cop Agent

This repository is the **Cop peer** for the “Distributed Cops-and-Robbers over a
Peer-to-Peer Network” final project.

> Companion Thief repository: <https://github.com/SharbelMaroun/p2p-thief-agent>

## Current milestone

This branch implements M2 core domain rules and M3 Cop-local state, history,
scoring, transport-free rules harness, and deterministic move-or-barrier baseline.
It also implements the M4 commit-reveal primitives (per-turn commitment, audit
reveal, Step-0 attestation) and the inbound FastMCP tool surface. It contains the
M1.5 Option-B contract repair: a role-neutral `shared_contract/` bundle at
`0.2.5-proposed`. The `0.1.0-proposed` bundle was rejected and is superseded.
There is still no outbound peer client, public tunnel, scent field, belief map,
LLM, Gmail, GUI, or replay runtime, so no live game has been played.

The shared contract is `0.2.5-proposed` and **UNFROZEN**. It becomes frozen only
after the coordinator accepts it and Thief independently consumes and verifies
identical controlled bytes (`shared_contract/verify.py --compare-root`). Option B is
a documented academic-freedom interoperability choice pinned to simulator commit
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`; see
[docs/OPTION_B_DECISION.md](docs/OPTION_B_DECISION.md) and
[docs/OPTION_B_HANDOFF.md](docs/OPTION_B_HANDOFF.md). Historical parity claims were
disproved by [docs/PARITY_REPORT.md](docs/PARITY_REPORT.md).

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
- A counted series has six sub-games. The role schedule is confirmed: sub-games 1, 3,
  and 5 use the natural role, 2, 4, and 6 the swapped role, and the Thief moves first
  (`U-025`, closed on a coordinator-relayed lecturer answer). Runtime orchestration
  still stays role-agnostic so the schedule remains a configuration input.
- Legal movement is north, south, east, west, or stay; diagonals are illegal.
- Barrier placement is disclosed. A barrier on the Thief’s current cell captures the
  Thief, and a Thief with no legal move is captured.
- SHA-256 commit-reveal, secret per-turn commitment nonces until final reveal,
  illegal-transition rejection, public tunnels, deadlines, and watchdogs are
  mandatory. The pre-play `negotiate.nonce` is a distinct public challenge.
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
uv run python shared_contract/verify.py
```

`shared_contract/verify.py` is the role-neutral, read-only bundle verifier;
`scripts/generate_shared_manifest.py` is the Cop-owner-only manifest generator.

These are verification commands, not claims that a live Cop peer is runnable yet.
The code/CLI version is exactly `1.00` from
`src/p2p_cop_agent/shared/version.py`; Python distribution metadata canonically
displays the equivalent PEP 440 form `1.0`.

## Configuration

- The stable, role-neutral shared contract is the top-level `shared_contract/`
  bundle at `0.2.5-proposed` (Option B). It holds specifications, schemas,
  fixtures, vectors, and the read-only verifier only — no active match.
- A per-match shared game object and local rate-limit enforcement mirror are each
  supplied at runtime by explicit path; neither loader has a repository or example
  fallback.
  `shared_contract/fixtures/match_config.example.json` is an example template; its
  exact file SHA-256 is
  `70758af55f178a049a438b81eb5f9acd389c568214cb3006358c66f8d10abd06` and its
  canonical object SHA-256 is
  `adac9efe6d51b9487c400a04c2e185af9fb3622e1a7d74f18d400425656d82db`. Changing
  opponent IDs or game identity never edits a stable controlled file.
- `config/rate_limits.json` is an example local enforcement mirror. Its shared
  Gatekeeper object must exactly equal the agreed match configuration, but its bytes
  and local extensions are not parity-controlled.
- `config/game.toml.example` is Cop-local and is not parity-controlled.
- `.env-example` contains dummy, provider-neutral placeholders only.

The bundle accepts only source profile `1.2`. Local generated artifacts observe
`1.1`, and the simulator runtime observes `1.3`; no translation or compatibility is
inferred. Exact artifact identity/schema rules and Step-0 attestation remain M7
work. See [docs/OPTION_B_HANDOFF.md](docs/OPTION_B_HANDOFF.md) for the controlled
inventory and hashes.

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

## Usage

The peer is not yet runnable as a live agent; what exists today is the SDK, the
protocol layer, both transport adapters, negotiation, and one turn of the loop.
So the honest usage surface is the CLI version probe and the verification suite:

```text
uv run p2p-cop --version          # 1.00
uv run python -m p2p_cop_agent --version
```

To exercise a turn crossing a real socket between two operating-system processes —
the book's stage-2 milestone — run the localhost integration tests, which spawn a
genuinely separate interpreter and read back the transcript it wrote:

```text
uv run pytest tests/integration/test_localhost_two_processes.py -v
uv run pytest tests/integration/test_localhost_negotiation.py -v
```

To check this peer's call shapes against an implementation that shares no source
with it:

```text
uv run pytest tests/conformance/ -v
```

This section will gain the live `peer` invocation, its flags, and replay
screenshots once `M5-10d` (a full sub-game over the wire) lands.

## Contributing

Code standards are enforced by the gates above, not by convention, so a change that
passes CI already meets them. In summary:

- **Style and linting.** `ruff check .` must pass with no findings. Line length,
  import order, and naming follow the configuration in `pyproject.toml`; do not
  add per-file ignores to silence a finding.
- **File length.** No source or test file may exceed **150 lines**
  (`scripts/check_file_lengths.py`), per the submission guidelines. Split by
  responsibility rather than trimming explanatory comments.
- **Tests.** `pytest --cov --cov-branch --cov-fail-under=85` must pass. New
  behaviour needs tests that would fail without it; prefer tests that pin a rule to
  the document that states it, so a silently edited constant fails locally rather
  than in a match.
- **Secrets.** `scripts/check_secrets.py` must report zero findings. Credentials,
  tokens, ports, and the opponent URL belong in the git-ignored `config/game.toml`
  or `.env`, never in a tracked file and never in shared JSON.
- **The controlled bundle.** `shared_contract/` is byte-controlled. Do not edit it
  to make a check pass; `shared_contract/verify.py` is read-only and only
  `scripts/generate_shared_manifest.py` regenerates the manifest. A change there is
  a contract revision and needs the coordinator.
- **Commits.** Stage explicit paths, never `git add .`. Commit messages state what
  changed and *why*, including the authority (book section, Appendix E/F rule, or
  ADR) when the change encodes a rule.
- **Documentation.** A behaviour change updates `docs/TODO.md` and any document
  that asserts the old behaviour. `docs/PROMPT_LOG.md` records significant
  AI-assisted steps, including the problem found and the lesson drawn.

## License

The repository MIT license covers team-authored material where legally valid.
Lecturer-provided simulator material is governed by its own educational-use EULA and
is not automatically relicensed. The simulator is a learning and interoperability
reference, not a submission skeleton; substantial source reuse requires the
provenance/license decision in ADR-008 or explicit permission.
