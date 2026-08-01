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

The graded six-section report is below, under **Report**.

## Planning history

The active M0–M9 [plan](docs/PLAN.md) and Cop-only [TODO](docs/TODO.md) govern this
branch. The
635-task pre-audit backlog under `archive/pre-audit/documentation/` is historical
coverage only and will not be restored as an executable plan.

## Report

The graded report has six sections. Sections that need a completed match are marked
as blocked rather than filled with claims we cannot yet show.

### 1. The Dec-POMDP model

The game is a **decentralised, partially observable Markov decision process**. Each
of the three words is doing work.

- **Decentralised.** There is no server, no referee, and no shared memory. Each peer
  runs in its own operating-system process with its own configuration directory, and
  the two communicate only by message. Neither can read the other's state, so
  correctness cannot rest on trust — it rests on cryptography.
- **Partially observable.** The Cop never learns the Thief's position. What it
  actually observes each turn is: its own position, the barriers it placed, the scent
  intensity in the cells it can sense, the Thief's free-text hint, and a commitment
  hash. The hint may be a deliberate lie — the Thief declares an `intent` of truth or
  bluff, and that declaration is sealed inside the commitment, so it is verifiable
  only *after* the game. So the Cop reasons over a **belief** about where the Thief
  is, never a fact.
- **Markov decision process.** State is the pair of positions, the barrier field, and
  the step index. Actions are the five legal moves (`N`, `S`, `E`, `W`, `STAY`) or a
  barrier placement, exclusively — one per turn. Transitions are deterministic given
  both agents' actions. Rewards are the fixed Appendix F table: capture pays the Cop
  20 and the Thief 5; survival pays the Cop 5 and the Thief 10; a tie pays 2 each; a
  technical loss pays **zero to both sides**, which is why an audit failure is worth
  avoiding more than a loss is.

The asymmetry matters: the Cop places barriers and must corner an evader, while the
Thief moves first each turn and only needs to survive the step limit. The Cop is
therefore under time pressure the Thief is not.

### 2. The FastMCP communication dilemma

The dilemma is that the two agents **must** communicate to play, yet every message is
an opportunity for the opponent to cheat or to learn. Three problems, and what this
project does about each.

**Simultaneity without a referee.** If the Cop announced its move first, the Thief
could react to it; the reverse is equally unfair. There is no third party to hold
both moves. The answer is **commit-reveal**: each peer hashes its full private
decision with a fresh random nonce and sends only the 64-character digest. Neither
can change a decision after seeing the other's, because a changed decision produces a
different hash. Nonces stay secret until the end-of-game audit, where every
commitment is recomputed. A single mismatch is an automatic zero, with no appeal.

**How much to reveal, and when.** The book describes a per-turn phase in which peers
exchange their actual moves. The reference implementation sends **no move at all** —
the live message carries the hint, the scent grid, and the commitment hash, while the
move, the true position, the bluff verdict, and the nonce stay private until the
audit. This project follows the reference (`C-030`), because the wire is what a
classmate's agent must interoperate with, and nothing is lost: the move is still
revealed, just later.

**Trusting an unknown opponent's answers.** Our peers play classmates' agents, not
each other. Two decisions follow. Outbound, we are **liberal about what counts as an
acknowledgement** — any reply that does not explicitly refuse is accepted, because
the profile never fixed the opponent's reply shape and a peer answering
`{"status": "ok"}` is not refusing. Inbound, our tools **always acknowledge and
validate afterwards**, so a rejection is recorded as a game outcome rather than
thrown to the sender as a network error. Both choices follow the same rule: be strict
in what you send, generous in what you accept. Getting this wrong is not theoretical
— an earlier version demanded our own reply shape, which would have read every
successful delivery from a simulator-built classmate as a refusal and abandoned a
healthy game on turn one.

**Failure is a game state, not an exception.** Every turn runs through a declared
phase machine that refuses any transition not in the specification's table, so an
out-of-order or silent peer reaches a defined terminal state instead of deadlocking.
Silence is not patience: a peer that owes a turn and sends nothing ends the match.

**Bounded waiting (added 2026-08-01).** Every wait is now finite. The book is blunt
about why — *"Missing a Deadline is a Failure, Not Patience"* — and permits only two
outcomes when an expiry passes: retry, or declare a technical loss and clear the
queue. An un-expiring pending request is named as the direct path to freezing. So
each attempt carries its own expiry, retries stop at the agreed limit, and an attempt
that overruns its own deadline is **not** retried: the retry budget does not rescue a
missed deadline.

The four limits live in the **shared, signed** match object rather than private
configuration, which is the part worth noticing — a peer able to set its own timeout
could stall an opponent legitimately. Reading them from the agreed bytes makes that
impossible rather than merely impolite.

*Problems hit building it.* Three. The reference notebook froze twice and the query
had to be re-sent three times before it submitted — logged rather than skipped,
because a tool failure is not permission to skip a verification step. Re-reading the
ledgers first turned up two rows still marked open for work already finished, which
would have sent someone to redo it. And the book PDF contradicted our own parameter
baseline in a small way: Appendix F table 19 marks the watchdog timeout
**`Negotiation`**, not `Minimum` like the retry limits beside it — a distinction that
matters, since a `Minimum` may only be tightened while a negotiated value can move
either way. Both baselines were corrected.

**The Gatekeeper (added 2026-08-01).** Outbound calls now pass through a rate
limiter that queues overflow instead of refusing it. The guidelines are explicit -
*"Overflow is queued, not rejected"* - which inverts the usual instinct: a busy gate
tells the caller to wait and **keeps** the work, and only a genuinely full queue
fails, loudly, because silently discarding a call is worse than admitting defeat.
The limits (30 requests/minute, 2 concurrent, queue depth 100) come from the signed
match object, so neither peer can quietly give itself more room.

*Problems hit building it.* Two, both about scope rather than code. Idempotency was
already done - the receive-side intake had been deduplicating and rejecting replays
since an earlier milestone - so checking first turned a planned feature into a
verification. And the book narrowed it again: the Gatekeeper guards **outbound**
Gmail and LLM calls against rate-limit bans, not the inbound peer mailbox. Building
it as an inbound queue would have been a plausible and completely useless answer.

Worth recording: our own task title said *"FIFO queue depth"*, and the book turned
out never to say FIFO - it was our inference wearing a citation. The word was
removed. A task that credits the book for something the book never said is how an
invented requirement becomes permanent.

**The watchdog (added 2026-08-01).** The deadline bounds a single request; the
watchdog bounds *overall silence*. A peer can answer every individual call and still
go quietly dead between them, so a separate liveness timer trips when nothing has
happened for the agreed `watchdog_timeout_sec` (60 s, from the same signed match
object). The heartbeat that feeds it is not new plumbing: the turn loop already emits
one transition per phase for the log, and the watchdog simply subscribes to that
stream — every phase entered is a sign of life. On a trip the runtime **persists its
state first, then shuts down**, routing the declared phase machine to its one terminal
state (`TECHNICAL_LOSS`) using only transitions the table already allows; a peer that
is merely waiting steps through the same bridge the turn loop uses, never a
fabricated edge. The persist step is deliberately fail-closed: if saving the snapshot
fails, that is recorded and the game still ends, because a shutdown that could itself
hang is the exact failure the watchdog exists to catch.

*Problems hit building it.* One, and it was about tooling, not code. The standing
order is *consult both NotebookLM notebooks, then implement*, and this session had **no
way to reach NotebookLM at all** — the tool was absent, not merely slow. Rather than
relabel the work as if the notebooks had been read, the gap was surfaced and the
decision handed to the human, who authorised proceeding on authority a *previous*
notebook pass had already pinned: the 60 s timeout was recorded in the deadlines
module as an Appendix F value, the heartbeat/terminal duty as Appendix E rules, and
the `WATCHDOG_TIMEOUT` constant already existed, read by nothing. No schema, wire
message, or phase transition was invented. What is *not* yet built: the concrete
state-snapshot format and the coordinator that wires persistence to a real match are
left to the log manager and orchestrator milestones, so `persist_state` is an injected
seam today rather than a file on disk.

### 3. The implemented strategy

Movement is **pure Python and fully deterministic**. The language model never chooses
a move; it is confined to the text layer, and the shipped configuration uses a
zero-token template provider. Two agents given the same state always produce the same
move, which is what makes a match reproducible from its log.

The current Cop policy is a barrier-aware pursuit baseline that ranks candidate
actions **lexicographically** rather than by a weighted score — no calibration data
exists that would justify weights, and a strict criterion order is auditable in a way
that tuned coefficients are not. Barrier placement is a separate, exclusive intent:
the Cop either moves or places, never both in one turn.

This is deliberately the floor, not the deliverable. The graded strategy must beat it
using the belief map, and that work is `M6`.

### 4. Learning curves

**Not applicable.** No reinforcement learning is used. The movement policy is
deterministic by design, so there is no training run and no curve to plot. If RL is
adopted later, this section gains the curves; adding a chart now would be decoration.

### 5. Live belief map and "Verified OK" replay screenshots

**Still blocked, but for a narrower reason than before.** A bounded sub-game now runs
end to end and its audit is delivered: every turn and the final reveal cross a real
socket into a separate operating-system process, which validates each one — and a
*tampered* audit is rejected there, so rule 19 is enforced over a real carrier rather
than asserted locally.

What is still missing for a screenshot is a **second peer that plays back**. The
opponent's replies in those runs come from a local script, so there is no live belief
map to photograph yet, and there is no GUI. Both arrive with `M6` (belief) and `M7`
(two peers, mutual audit verification).

### 6. Companion repository

<https://github.com/SharbelMaroun/p2p-thief-agent> — the Thief-side peer, developed
independently.

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
