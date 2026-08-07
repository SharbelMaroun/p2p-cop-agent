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
`0.2.10-proposed`. The `0.1.0-proposed` bundle was rejected and is superseded.

Since then: the M6 scent field and belief map, the outbound FastMCP client, the M7
artifact/reporting pipeline (declaration, per-sub-game config and log, final result,
settlement, six-sub-game series) with the Gmail sender, and the M8 **replay verifier** —
which reaches `Verified OK` or `TAMPERED` on a saved log, including one this peer did not
write. Still absent: a public tunnel, an LLM provider, any GUI (`ui/` is an empty package),
and the replay *view* that would make the verifier's banner photographable. Gmail
credentials are deliberately not in the repository (rules 39–40), so the sender is built
but unexercised. **No live game against a real opponent has been played.**

The shared contract is `0.2.10-proposed` and **UNFROZEN**. It becomes frozen only
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
  bundle at `0.2.10-proposed` (Option B). It holds specifications, schemas,
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

The full academic report body — the formalism in LaTeX, every architectural decision with
what it cost, the measured results and the token/cost accounting — is in
[docs/ACADEMIC_REPORT.md](docs/ACADEMIC_REPORT.md). Quality evidence against ISO/IEC 25010
and the book’s four success metrics is in [docs/QUALITY_EVIDENCE.md](docs/QUALITY_EVIDENCE.md);
the scoring is in [docs/SELF_ASSESSMENT.md](docs/SELF_ASSESSMENT.md).

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

#### The play loop: driving the mailbox (`M5-17`, 2026-08-02)

The FastMCP server this peer runs is a **passive mailbox** — its four tools enqueue the
opponent's message, acknowledge it, and do nothing else. The turn loop is the mirror
image: it consumes a message and never looks for one. Nothing joined the two, which
meant every sub-game test had to hand the loop a *scripted* opponent, and a peer could
not play a match unattended. That gap was the real content of the "two-machine game is
blocked" row: it was never only about hardware.

The join is a polling turn source. Each wait drains the mailbox, hands back the next
turn the peer **accepted**, and is bounded — Appendix E rule 6 makes a deadline
mandatory "to prevent deadlocks while waiting for the opponent", so silence returns
`None` and the loop takes its one declared exit to `TECHNICAL_LOSS` instead of
blocking. The wait also **pulses the heartbeat every iteration**, because book §8.4.2
puts the watchdog on the main game loop and waiting for an opponent is precisely the
window in which a frozen peer and a patient one are indistinguishable.

Three behaviours in the mailbox side are there because each would otherwise break an
unattended match invisibly: a *rejected* turn is consumed (leaving it queued makes the
poller re-reject it forever and starve the real turn behind it), a *second* queued turn
is left in place (draining both discards the next step rather than playing it), and the
other three mailboxes are drained first (a control or audit message parked in front of
a turn stalls the game). A whole sub-game now plays with **no message fed in by hand**.

*Problems hit building it.* Two worth recording. First, the two notebooks appeared to
**contradict each other**: the reference drives its runtime by polling its own inboxes
at `poll_interval_seconds`, while the book mandates a strict state machine rather than
a loop. Treating that as a conflict would have meant choosing one and quietly dropping
the other; the actual resolution is that they answer different questions — polling is
only *how* a queued message is picked up, and the phase machine still decides what may
legally follow, so a message arriving out of turn is refused by the transition table
and not by the poller. Second, the first test run **failed on my own assumption**: the
harness had the Cop *opening* the game, when the book gives the first move of every
cycle to the Thief. The failure was in the test, but the same assumption in a launcher
would have deadlocked two correctly-written peers against each other.

*What is still not built.* The `serve` CLI (`M5-17e`). `build_server(...).run()` is a
blocking call, so launching a peer needs the server on a background thread plus
autonomous negotiation sequencing. A **passive** `serve` — one that mailboxes without
playing — was rejected on 2026-08-01 as proving connectivity rather than a game, and
shipping one now for the appearance of progress would contradict that. It is left
explicitly open, and it is no longer blocked on design: the loop it would drive exists.

*A blocker that got worse on inspection.* The book's stage-5 milestone requires
**screenshots from the Replay App showing "Verified OK", plus the Live GUI belief map**
as its evidence. Both are `M8` deliverables, so the two-machine game cannot be
*evidenced* even once the hardware and the CLI exist. The ledger previously recorded it
as hardware-only, which understated it.

#### Launching a peer: hosting and readiness (`M5-17e`, 2026-08-02)

With the play loop built, the next gap was the process to host it. Two mechanical
halves landed, both testable without a real match: `adapters/serving.py` puts the
mailbox on a **daemon** thread after a port pre-check, and `services/readiness.py`
waits — bounded — for an opponent that has not started yet.

**The bind address is the part worth reading.** The reference binds `127.0.0.1`. The
book prints `mcp.run(transport="http", host="0.0.0.0", port=8000)` with the comment
"Bind the server so a tunnel can expose it publicly", and rule 10 reads "Use tunnels
to expose the local server to the public internet. **Sanction: Inability to compete
against opponents**". The reference is not wrong — it runs both peers on one machine —
but copying it would produce a peer that passes every local test and is **invisible
through the tunnel**, failing only at the two-machine rehearsal where it reads as a
network fault rather than a one-word bug. The book outranks the simulator, so the
default is `0.0.0.0` and a test pins it, because nothing local would ever catch a
change back.

Two smaller decisions, each guarding a hang. The server thread is a **daemon**, so a
finished match cannot be kept alive by a mailbox nobody is reading — the failure the
watchdog exists to catch, reintroduced at the process level. And `ensure_port_free`
runs *before* the thread starts, so a stale peer still holding the port fails loudly
at launch instead of yielding a server that never binds while the game loop waits for
messages that cannot arrive.

Readiness is deliberately **not** `deadlines.py` or `watchdog.py`. Those exist to make
waiting a failure, because rule 6 requires it. Startup is the one phase where an
unreachable peer is expected and harmless: before the game exists there is nothing to
forfeit. Keeping it a separate module is what stops that leniency leaking into the
match. It still gives up after `connect_timeout_seconds`, and returns `False` rather
than raising — nobody having launched the other process is an operator situation, not
a protocol fault.

*Problem hit.* The first `ensure_port_free` set `SO_REUSEADDR` on its probe socket out
of habit, and **the check silently never fired**: on Windows that option lets a socket
bind a port another process already holds, which is exactly the condition the function
exists to detect. A test that held a port and asserted the raise caught it. A
detection probe wants the strictest bind available, not the most permissive.

*Since closed (`M5-17f`).* Negotiation-to-first-move sequencing now exists —
`orchestration/negotiation_handshake.py` and `orchestration/match.py` run the book's
pre-play order (negotiate → exchange and verify Step-0 → write and lock the
declaration → play), and `adapters/serve.py` wires the `serve` command onto it. The
paragraph that stood here said it was not built; that was true when written and is no
longer, which is exactly the drift this report exists to avoid.

#### Locking the scent model, and an unknown that no ruling could close (`M6-07`, 2026-08-05)

Appendix E rule 23 is short: *"Lock the cryptographic hash of the scent model before
the start of the game. Sanction: Deviation from the formula cancels the game."* We had
no lock at all, and the reason turned out to be more interesting than an unfinished
task.

The 5×5 emission field has 25 cells. Book Figure 4 names five radial classes — centre
`0.90`, cross `0.62`, diagonal `0.20`, mid-side `0.14`, corner `0.04` — and those cover
**17** of them. The remaining eight, the ring at offsets `(±1,±2)`/`(±2,±1)`, are named
by nothing. They had been recorded as an open unknown (`U-030`) and left **empty**,
waiting for a ruling, and the model lock was blocked behind them.

That wait could never have ended. A ruling needs something to rule on, and no source
states a value. Meanwhile the omission was itself a defect: the reference simulator
emits all 25 cells and its own tests assert a snapshot length of 25, so our eight empty
cells would reach an opponent as eight cells reading zero — a quieter agent than we
actually are, and a wrong one.

The book had already answered a different and better question (p. 31): the parties
**agree** the emission and decay model, confirm they interpret it identically against a
concrete numerical example, and lock the agreement with SHA-256. It even recommends
handing the opponent your scent source code. So the eight cells stopped being an
unknown and became a **negotiated parameter** — published with an explicit default that
carries no book authority, and sealed inside a hash covering the whole model: formula,
constants, field size, and all 25 cells. Comparing the three Appendix F constants could
never have caught this, because the formula and the radial profile never cross the wire
on their own.

**The lock is deliberately lenient in one direction.** A peer that publishes no lock is
still played; a peer that publishes a *different* one is refused. The reference
publishes none — it folds its pheromone terms into `config_sha256` — so demanding one
would refuse every simulator-built classmate over a message they never send, and rule
23 sanctions a *deviation from the formula*, not a silence. That is the same reasoning
already settled for `config_sha256` under `U-029`.

*The arithmetic correction, disclosed (`M6-07c`).* The locked formula reads `(1 − ρ)` as
**retaining** 90% of prior scent at ρ = 0.10. The book's p. 43 prose "reduced by 90%"
and its p. 46 claim that ρ approaching 1.0 *saturates* the board are arithmetic errors —
a decay rate near 1.0 erases the trail, it does not saturate it. Both are disclosed here
under the book's own p. 5 contradiction clause and are not implemented.

*Problem hit — and it is the one worth reading.* The standing process is: ask both
NotebookLM notebooks, **then** verify against `inst/`. The book notebook reported that
Figure 4 prints **all 25** cells, with diagonals at `0.42` and the unnamed ring at
`0.14`, and stated outright that no cell is left unspecified. It had been asked
explicitly not to infer or interpolate. The source
(`inst/police_thief_p2p_Summary.md:947-955`) contradicts every part of that: five
classes, 17 cells, diagonals `0.20`. Had the verification step been skipped as
redundant, a **correct** emission table would have been overwritten with an invented
one in both repositories — and the tests would have been rewritten to match it, so
nothing downstream would ever have caught it. A notebook is a search tool over sources.
It is not a source, and it ranks below one in `SOURCE_OF_TRUTH.md` for this exact reason.

*The evidence that the lock is worth anything.* The companion Thief peer, written
independently against the same book sections, produces the identical digest
`416a57e1…` from its own record. Two implementations agreeing is the only thing that
distinguishes a real interoperability contract from a number we hash locally and
believe.

#### Catching a lie: the reliability factor (`M6-02`, `M6-11`, 2026-08-06)

The Thief is *allowed* to lie — deception is the strategic layer this project is about.
What it cannot do is lie about where it has been, because scent is "an involuntary
byproduct of movement". Chapter 4.4's boxed case study is written from the pursuer's
side, which makes it this peer's specification almost verbatim: the Thief announces a
direction, the Cop computes the fresh trail it would expect there — "approximately 0.81
(calculated as 0.9 \* (1 − 0.1) = 0.81)" — measures 0.00 instead, "lowers the trust
coefficient assigned to the thief's verbal statements", and keeps tracking the real
scent.

That is now arithmetic rather than narrative. `expected_fresh_scent()` derives the 0.81
from the **locked** model's own constants instead of hard-coding it, so a renegotiated
scent model moves it too. `corroboration()` compares it against the strongest scent
actually measured where the hint points — the *strongest*, not the mean, because a
direction names a whole half-plane and averaging would dilute a real trail to nothing on
a large board. `apply_support()` then moves a running `TrustScore`, scaling the step by
how far the evidence sits from neutral — the study's *absolute* contradiction moves trust
at full rate, a marginal disagreement barely at all.

**Three design choices worth defending.** Trust runs *forward* between turns, because a
coefficient recomputed each turn forgives every lie immediately. A distrusted hint is
**ignored, never inverted** — a liar's claim is evidence of nothing, not evidence of the
opposite, since it may still happen to be true. And scent is applied to belief *before*
the hint is weighed against it, so the claim is judged against evidence the Thief could
not manipulate.

**What the book fixes, and what it does not.** It fixes the shape — "the agent applies
Bayes' rule to update the probabilities, incorporating a reliability factor for the
clue" — and the evidence. It states **no** starting trust, no step size, no decay rate
for repeated lies, and no bound, saying outright that translating scent and statement
into a numerical belief map is the agent's own business. So `NEUTRAL_TRUST = 0.5` and
`TRUST_UPDATE_RATE = 0.25` are marked PROJECT-PROPOSED, not cited. Belief never crosses
the wire, so unlike the scent model there is no opponent to disagree with them.

`TrustScore` moves by a bounded step *toward* a bound rather than clipping at it, so
trust approaches 1.0 and 0.0 without arriving: no opponent is ever granted certainty or
condemned past appeal. That matters here specifically because **bluffing is legal** — a
peer that lies four times and then tells the truth has to be able to climb back.

*The reference was checked too, and does none of this.* It never parses the opponent's
`hint` at all — the string is logged and displayed in the GUI, and `_pick_move` receives
the smell-driven belief grid but not the hint. So there is no interoperability
constraint here whatsoever; this is purely our own strategy, which is also why it is a
place we can actually beat a simulator-built opponent.

*Two implementations met in the middle.* This work and `hint_consumption.py` were
written on separate branches within a day of each other, both claiming `M6-11`, neither
aware of the other — a coordination failure rather than a technical one. They merged
without loss because they were complementary: that module's own docstring **defers**
exactly the two rows this one built. `receive_hint` became the front door, its
`TrustScore` the single trust type, and `corroboration` became the scent trigger it had
left open. The merge was net-positive in a way parallel work usually is not, because each
half caught something the other missed — and what it caught in mine was a real hole:
**an opponent smuggling `3,4` into a hint.** My decoder read that as ordinary text; the
guard refuses to parse it at all, so "our hints carry no coordinates" and "we never read
a coordinate channel" became one rule instead of two that drift. A refused hint costs the
peer no trust, though: declining to read a message is not the same as catching a lie.

#### The scent reaches the wire (`M6-08`, `M6-09`, 2026-08-06)

Found by inspection while about to start the reporting milestone: `serve.py` sent a
hard-coded `"smell_grid": {}` every single turn. Nothing parsed an opponent's grid
either, and the belief pipeline's `observed_scent` parameter had no supplier anywhere in
the codebase.

So this peer **emitted no scent at all** — while having just cryptographically locked an
emission model at negotiation. That is a deviation from the agreed model, which is what
rule 23 cancels a game for, and it denied the opponent the one channel the design
guarantees them. It also meant the entire belief, trust, and lie-detection layer built
the day before was **dead code in a live match**, because nothing ever fed it evidence.

The trail is now real, and the whole loop is proven end to end: emit, encode, cross the
wire, decode, and the belief argmax lands on the emitter's actual cell.

**Emission is involuntary by construction, not by discipline.** `ScentField.advance`
takes a **cell** and nothing else — a signature test asserts its only parameter is
`occupied`. There is no action, no flag, no provider a caller could set to stay quiet, so
a `STAY` deposits exactly as a move does. The book leaves no room here: the scent "is
emitted by the **movement or the stay itself**, and no agent can plant a misleading trail
— each side emits its own scent, and each side reads the scent field of its opponent
only." Suppression is not refused; it is unrepresentable.

**Where we follow the book against the reference.** The reference deposits scent and
*then* decays the whole field, which yields `(τ + Δτ)(1−ρ)` and quietly attenuates the
fresh deposit. The book's update is decay-then-add, so a cell just stepped on reads the
full `0.9` — which is exactly what chapter 4.4's worked example assumes when it predicts
`0.81` for a **one-turn-old** trail. Copying the reference here would have made our own
lie-detection arithmetic disagree with the book that specifies it.

*Problem hit — I shipped a parser that would have rejected our own emissions.* The
inbound parser capped intensity at the centre intensity, `0.9`. That reads as obviously
right and is obviously wrong: the update is **additive**, so an agent that stands still
keeps depositing onto a decayed prior, and our own two-turn trail already reaches
`1.458`. We would have refused ourselves, and every peer following the formula. My own
test caught it, because it asserted a behaviour **across turns** rather than one call —
a happy-path test would never have reached the case. The bound is now *derived*: the
fixed point of `τ = (1−ρ)τ + Δτ`, which is `Δτ/ρ = 9.0`. It tolerates any conformant peer
while still refusing a hostile `1e9`.

*Two ledger definitions turned out to be wrong, and were corrected rather than quietly
satisfied.* One said empty cells should be omitted; the reference includes them, and
interoperability follows the reference — so we send the full window and tolerate a
sparse peer. The other claimed byte-identical rounding is "the property the locked
scent-model hash depends on"; it is not. The lock covers the **model** — formula,
constants, radial profile — and never an emitted number, so rounding cannot invalidate
it. The companion Thief's ledger carried the same false claim and has been corrected too.

*A process failure worth recording.* The standing order is an eight-step gate, and on
this task I ran five of them. I read only one repository's ledger instead of both,
skipped the submission-guidelines file entirely, left this report untouched, and pushed
anyway — then reported the work as done. The gap was found by being asked, not by a
check. Closing it immediately surfaced something real: **the companion Thief had already
built this same wire layer**, and comparing the two exposed the false hash claim above.
Step 1 exists precisely to find that before the work starts, not after it ships.

*Problem hit — the specification is upside down (`C-032`).* Transcribing the case study
literally made **my own tests fail**, which is how it surfaced. The study places the
scent at `(1,4)`/`(1,3)` and calls that the **south-east** corner, then calls `(5,2)` a
**northern** cell. Under the Appendix F origin — top-left, row growing downward — `(1,4)`
is *north*-east and `(5,2)` is *southern*: north and south are swapped throughout. The
"lie" I had set up was in fact corroborated, and the test correctly refused it. Its
intensities are authoritative and are used verbatim; its cell labels are not. Copied
faithfully, it would have pinned an inverted board into the suite and the Cop would have
chased every lie instead of catching it.

#### What a hint is actually about (`M6-10`, `M6-10e`, 2026-08-06)

Until now this peer sent the same five words every turn: *"holding position"*. That is a
hint in name only — constant text carries no information, true or false, and the verbal
layer is half the game the book is about. A real hint now goes out each turn, its intent
alternating so both honesty and bluff are exercised, and sealed in the commitment so a
bluff cannot be denied at the audit.

**The interesting part is what a hint is a claim *about*.** Our own ledger said the place
descriptor should be "belief-derived" — that we should hint about where we think the
Thief is. That is wrong twice over, and both notebooks plus the book agree.

It would be **unfalsifiable**. Chapter 4.4's whole lie-detection mechanism works by
testing a verbal claim against *the claimant's own scent*: the Thief says "I am moving
North", the pursuer measures no scent there, and "the physical evidence contradicts the
verbal claim, revealing the thief's true location". You can only check a claim against
the scent of the peer who made it. A hint about the *opponent's* position could never be
tested by anyone, so it would carry no strategic weight at all.

And it would be **a leak**. A place computed from our belief argmax publishes our private
inference on the wire — exactly what the `M6-18` guard above exists to prevent. Asked
directly, the reference confirms its own `place` comes from the negotiated `setting` and
is "not derived from the belief heatmap".

So `place_for` takes **our own cell** and dresses it in a landmark from the agreed
`map_area`. When no area is agreed the book is explicit that generic bearings are used,
so an unset area is an ordinary supported configuration rather than a gap — as are an
unknown city, a malformed value, and a missing section. Every word in the vocabulary is
asserted coordinate-free, because a landmark that smuggled a digit would be the numeric
protocol rule 27 forbids, just wearing a nicer coat.

*A note on where the words came from.* The mechanism is the reference's; the vocabularies
are ours. Copying its landmark lists verbatim would be source reuse under `ADR-008`, and
the lists are the one part with no engineering content.

#### Keeping the guesses private (`M6-18`, 2026-08-06)

The belief map is not a secret in the cryptographic sense — nothing hashes it, nothing
hides it. That is precisely why it needed a *structural* guard: a `belief` field added to
a turn message would work perfectly, pass every test, and be caught by nothing.

Two properties are now pinned. The public turn schema's roster is fixed and carries no
belief, certainty, probability or trust member, and the existing guard against publishing
our own `position`/`move`/`nonce`/`intent`/`verdict` is pinned so it cannot quietly erode.
Then a walk over the wire and transport layers proves they import no inference module at
all — which catches the subtler case the roster test cannot: inference imported into the
wire layer and its output smuggled into a field that already exists, a hint or the scent
grid.

**The guard was verified to bite**, not merely to pass. Injecting
`from strategy.belief import Belief` into the wire layer fails it; the injection was then
reverted. A guard that has never been seen to fail is a guard nobody has tested.

**It deliberately does not over-reach.** `strategy.scent` and `strategy.scent_field` are
outside the ban, because emitting scent is an *obligation* — the model is hash-locked
under rule 23 and the book requires that "each side emits its own scent". A guard that
forbade the wire layer from touching scent would forbid the very thing we are committed
to doing.

*Worth correcting, because it is widely misquoted.* Appendix E rules 8 and 9 are usually
cited as the authority for this. Read verbatim, they are narrower: rule 8 is "**display**
true local information only in the **live user interface**" and rule 9 is "do not
**display** the full objective board state in the **live user interface**". They govern
the UI, which is a later milestone. The constraint on the *wire* comes from Zero-Trust
instead — sharing state creates "a 'backdoor' through which one agent might see the local
truth of its rival". Citing 8 and 9 here would have been an invented requirement wearing a
real rule number.

#### When the words and the world disagree (`M6-12`, `M6-12b`, 2026-08-06)

This closes the last `P0` in `M6`. The row had been deferred since 2026-08-03 on three
dependencies that all now exist, and it asks a question the whole verbal layer rests on:
when a hint says one thing and the scent says another, which wins?

Two sentences answer it and they ask for different things. `:508` states the obligation —
a contradicted hint means the agent "**must reduce their trust level and update their
map**", two clauses joined by *and*, so both are asserted separately. `:1020` states the
behaviour, and its verb is the precise one: the pursuer "**ignores** the verbal claim and
**continues** to track the actual scent source". Not *redirects* — **continues**. A lie
that merely failed to win would still have deflected the pursuit slightly; the book says
it does not bend at all. So the binding test compares the target under a lie against the
target from the same turn having heard **nothing**, and requires them identical.

**Then the tests passed on the first run, which is where the actual work started.**
Passing immediately is not evidence a test is good — it is equally consistent with a test
that cannot fail. Probing the implementation across its whole range showed the pursuit is
protected by something other than what the tests appeared to credit: a `0.04` trace, the
faintest value in the book's emission table, outweighs that lie held at **complete**
trust. A located peak concentrates likelihood on one cell; a bearing spreads it over half
the board. The dominance is structural, and those two headline tests would have passed
with the trust machinery entirely disabled.

They are not wrong — chapter 4.4's case study *is* that regime, an absolute
contradiction — but alone they would have overstated what they proved. So the ordering
itself is now pinned in `test_evidence_priority.py`, both halves of it: scent decides
wherever it can, and a hint decides only what scent leaves open. Given two equal peaks,
scent cannot choose and the claim breaks the tie. That second half matters as much as the
first: a hint that could never change any decision would be dead code dressed as
strategy, while one that could overrule scent would make the book's lie detector
pointless. The result is lexicographic, like every other policy here (`M6-04`).

**Both repositories reach the same ordering from different structures** — a mapping of
cells here, a grid of rows in the Thief — and both now test it. Belief never crosses the
wire (`M6-018`), so nothing in the protocol could ever detect the two sides drifting
apart on this; only a test in each repo can.

*What the sources do not say, checked rather than assumed.* No numbered Appendix E rule
with a sanction covers any of this — `:508` is body text, and the override falls out of
the Bayesian update rather than being decreed. Nothing defines a trust floor or an
"ignore a liar after N turns" rule, so our multiplicative decay and `[0, 1]` clamp are
engineering and are labelled as ours. A consequence we accept: decay approaches zero
without reaching it, so a distrusted peer can still break an exact tie. Inverting a
liar's claim would be worse — a liar's statement is evidence of nothing, not evidence of
the opposite, since it may still be true.

*The reference offered nothing to copy, and its own documentation is wrong about that.*
It never applies a hint to belief at all: no trust coefficient, the hint logged and
displayed but never entering the belief update — while its README describes a fusion of
scent and hints that its code does not perform.

*Two gates caught this batch before it shipped.* The file-length cap rejected the test
file at 217 lines, which is what split it into the two files above — a better shape than
the one it replaced. The secret scanner then flagged a test **name**: `outweighs_a_lie_…`
contains `gh` + `s` + `_` followed by twenty-five word characters, which is exactly the
GitHub token pattern. Renaming it was the right fix; an allowlist entry would have
weakened the scanner permanently to accommodate a cosmetic choice.

#### Does the smart strategy actually work? (`M6-17`, `M6-20`, `M6-20a`, `M6-20b`, 2026-08-06)

Everything above argues that belief-driven pursuit *should* beat a Cop with no model of
where the Thief is. `:3115` requires the report to present "the empirical evidence for
their success", and until now this repository had none for the strategy itself.

It specifies nothing else. No run count, no seed policy, no significance test — and no
baseline: the "shipped heuristic" appears only as a config comment (`:3028`, "else the
shipped heuristic runs"), meaning the bundled default when you supply no brain, not a
prescribed thing to measure against. So the protocol is ours, and is stated in full in
`docs/PRD_strategy.md` rather than summarised, because a number whose method is hidden is
not evidence.

**The design choice that makes the result mean something** is a *non-reacting* opponent.
The Thief is a seeded random legal walk that never looks at the Cop, so on a given seed
**every arm meets the identical trajectory**. That turns the comparison from two averages
into a **paired** one — we can ask "on this exact chase, which Cop caught it?" — and it
cost nothing but the decision to hold the opponent fixed.

The second choice is the **`oracle` arm**: a Cop that reads the Thief's true cell. It is
not a legal agent and could never be shipped. It is there because beating a random walk
is a low bar, and without a ceiling a reader cannot tell a good result from an easy one.

| arm | capture rate | mean turns | mean Cop score |
| --- | --- | --- | --- |
| `blind` (random legal move) | 26.7% | 32.4 | 9.0 |
| **`belief` (what we ship)** | **96.7%** | **12.5** | **19.5** |
| `oracle` (ceiling, illegal) | 100% | 12.2 | 20.0 |

Paired over 30 seeds: belief captured on **21** seeds the blind Cop lost, and lost **0**
that it won. Not "better on average" — better or equal on every single chase. It closes
**95.5%** of the blind→oracle gap, and the result is stable across sample size (belief
99.0% at n=100, 99.7% at n=300; blind 24.0% at both).

**And the caveat, because it changes how the number should be read.** Belief lands close
to a cheating Cop partly because the book's scent channel is *generous*: a 5×5 window
peaks at the emitter's own cell, so a fresh trail nearly identifies the Thief outright.
What this measures is that our pipeline exploits nearly all of the available signal. It
is **not** evidence that the policy would hold against a Thief that manages its trail
deliberately — no such opponent was run. The `oracle` row is in the table so that ceiling
is visible rather than implied, and this paragraph exists because a result presented
without its limits is a claim, not evidence.

`M6-20`'s condition was unusually sharp — "must beat the blind baseline **or be
reverted**" — which is only enforceable if something re-checks it. `test_strategy_quality.py`
does, with deliberately loose bounds so it fails on a real regression rather than on any
harmless retune, and with a wiring check (belief must never beat the oracle) so a
mis-plumbed harness cannot quietly produce a flattering table.

*The reference had nothing to copy:* it contains **no harness, script, or test** that
plays repeated matches to compare strategies, and no committed results table or learning
curve — only LLM token-cost benchmarks. Its seeding pattern was worth borrowing though:
a `seed` config key resolved into a `random.Random` instance passed to the brain, rather
than global `random.seed`. Each actor here gets its own stream for the same reason.

#### The bundle was telling strangers to do the retired thing (`X-03`, 2026-08-06)

Found by reading `shared_contract/` the way an opposing team would, rather than the way
its author does. Two lines — the bundle README's opening and `verify.py`'s header — still
said the bundle "can be copied into the Thief repository byte-for-byte". That model was
retired on 2026-07-28 under `THIEF-002`, and the companion repo's own checklist says it
"must not be revived". The withdrawal *was* recorded here — but only in a document marked
SUPERSEDED, so the **deliverable itself** contradicted the companion repository.

**The obvious fix would have been wrong.** Deleting the sentence would have implied
sharing is discouraged, and the book says close to the opposite. Chapter 6 **recommends**
publishing the scent model so both sides run identical logic. What Appendix E rule 2
prohibits — with the sanction "immediate disqualification due to data leakage" — is
sharing *memory or variables*, which the same chapter extends to importing "a shared
module that maintains live state". This bundle is specifications, schemas, fixtures,
vectors and a read-only verifier. It holds no state. Offering it to an opponent is the
**recommended** half of that distinction, not the prohibited one, and the bundle now says
so explicitly rather than leaving a reader to guess which side of the rule it sits on.

Three things were genuinely wrong, and they are different from each other:

1. **It named our companion Thief repo.** The book names that precise hazard: separation
   matters "specifically during the development stage, when one team builds on the same
   machine both the Police and the Thief" — which is exactly our situation.
2. **It implied copying establishes conformance.** The book's evidence of
   interoperability is a replay screenshot showing `Verified OK` for a real match (§7.4;
   the submission requirements in Appendix C). Appendix E rule 52 permits warm-up games
   for exactly this purpose. Byte-parity with one peer is evidence about that peer.
3. **It cited our own summary's line numbers** — `:705`, `:708`, `:1693`. This is the one
   file we write *for a stranger*, and a stranger has the book, not our summary. Every
   citation in the shared bundle is now by chapter and rule number.

Both files are controlled, so `G-18` forced a version bump and a regenerated manifest:
`0.2.6-proposed` → `0.2.7-proposed`, manifest `4dd5d18a…`.

**The bump found a second defect.** After bumping `CONTRACT_VERSION`, the manifest
verified clean — because it hashes bytes and the bytes were consistent. But **12 files
inside the bundle still declared `"x-contract-version": "0.2.6-proposed"`** in their own
JSON. A bundle whose version file says one thing and whose schemas say another would have
shipped, passing its own integrity gate the whole way. Nineteen current-state claims were
updated across the repo and three historical ones deliberately left, since a record of
what `0.2.6` changed should not be rewritten to claim it was `0.2.7`.

#### The Thief now has its own neutral peer (`M1-015`–`M1-017` cross-check, 2026-08-06)

This repository has had a conformance stub since `M5-03e`. The companion Thief did not —
its equivalent rows had been PENDING since the wire realigned to the simulator profile
and archived the old one. They are now closed, and deliberately **not** by copying
anything from here: `M1-015` requires a stub "sharing no source file with any peer
repository", and `THIEF-002` forbids that repository any access to this one. It authored
its own from its own profile document.

Two findings there are worth recording on this side.

**Ordering has no rule, and the reference does not enforce it.** Asked directly, the
reference does not gate message ingestion on step sequence — a duplicate or non-advancing
step stays queued for the peer loop rather than being refused on arrival. Our stub here
refuses one (`test_a_turn_that_does_not_advance_is_refused_by_the_stub`), which is
stricter than the reference. That is defensible for a test peer, but it is *our*
strictness and should not be read as a rule the wire imposes.

**Our version negative-vector sits one layer up.** `M1-017`'s categories include version
mismatch. This repository proves it in `tests/contract/` — against our own parser — not
across the stub wire, where the other six are proven. A refusal demonstrated at the
boundary by an independent implementation is stronger evidence than one demonstrated by
the code that also produced the message. Noted rather than fixed; it is a small gap, not
a hole.

#### The Thief's config-integrity guards, and one worth mirroring (2026-08-06)

The companion Thief closed its remaining `M1-017` vectors today with two guards this
repository does not have, and one of them is worth considering here.

**Duplicate JSON keys are unguarded by default, everywhere.** `json.loads` resolves
`{"a":1,"a":2}` to `{"a": 2}` silently, so a check on the parsed object can never see it.
Appendix E rule 11 (Mandatory) requires the configuration to be "identical, bit-for-bit,
on both sides"; a document with a repeated key cannot satisfy that, and a signature over
the raw bytes would verify a different object than the one parsed. The Thief now refuses
it in `object_pairs_hook`. This repository loads its bundle fixtures and match configs
with plain `json.loads` and has no equivalent — noted here rather than silently fixed,
because it belongs to a row that does not yet exist.

**Private fields in a shared config** are refused there too, against the classes the book
assigns to the private `config/game.toml` (`:2901`). Our `M6-18` guard keeps belief off
the *wire*; this is the neighbouring question of what may appear in the *negotiated
config*, which we do not currently check either.

Both are recorded as candidates rather than claimed as done here.

#### Completing the pre-game declaration (`M7-22a`–`M7-22e`, 2026-08-06)

The first M7 work in this repository, and step 1 reshaped it before a line was written.
The companion Thief already builds all four artifacts; this repository has no `reporting/`
package at all — so its M7 artifact rows are *build them*, not *emit them*, and `M7-14`
(validate every artifact against its schema) cannot mean anything until they exist.

It also turned out a declaration builder already existed, in `protocol/` rather than
`reporting/`, carrying groups, members, repo links, token limit and times with a
reproducible lock. Its own docstring names what M7 still owed: the schema envelope, file
emission, and the fields M5 could not compute.

`:2229` gives the authoritative roster — the declaration consolidates "both groups and
their members, addresses of the police and the bank, **addresses of the MCP server,
details of the hardware, language model**, agreed token limit, and start and end times".
Two of those were missing.

**MCP addresses, with a guard.** The declaration is committed to a public repository and
emailed as an attachment, and rule 39 (Prohibited) forbids pushing secrets — sanction
"severe security failure and project failure". A URL is the easiest way to leak one by
accident, so an address carrying a credential is refused outright. That guard took two
corrections to get right, and both are pinned: a key-bearing query parameter slipped
through a pattern anchored at the leading `?`, and once that was widened
`http://127.0.0.1:8000/mcp` was refused, because the port's colon read as `user:pass`.
A guard that rejects the commonest local address is a guard someone switches off.

**Hardware and model, read from the identity rather than passed in.** Rule 24 is
Mandatory — "perform a cryptographic hardware declaration before the start of the game",
sanction "denial of eligibility for computational bonuses". The first version threaded
`host_spec` and `llm_model` through `play_match` as new parameters. That was the wrong
shape: both are already members of the negotiated identity block, and a second source for
the same fact is a second thing that can disagree. They are read from the identity.

*What is not done, and the row says so.* `M7-22`'s parent stays open on **file emission** —
nothing here writes `declaration_<game_id>.json` to disk yet, and `:3600` fixes that name.
`M7-23` (config artifact) was claimed and returned to `DEFERRED` untouched rather than
left looking started. Emission, the config artifact, the log artifact and schema
validation are the next batch.

*The secret scanner fired twice on this work, both times on the credential detector
itself* — once on an explanatory comment containing an example parameter, once on a TODO
row quoting it. Reworded rather than allowlisted, on the same reasoning as before: an
allowlist entry weakens the scanner permanently to accommodate prose.

#### The artifact layer, and a schema that could only validate a template (`M7-23`, `X-04`, 2026-08-06)

`reporting/` now exists: the four filenames the book fixes at `:3600`, an atomic writer,
and the agreed-configuration artifact with both of its cryptographic locks.

**`M7-23`'s condition is sharper than it reads.** "The emitted config is the one actually
played, **not a template**." `fixtures/match_config.example.json` is a valid config that
describes no game — emitting it would produce an artifact that passes its own schema and
a casual read while documenting a match nobody played. So `build_config` takes the
negotiated game object and reads every section from it, and the test changes an agreed
value and asserts the artifact follows, rather than comparing against a constant.

**Two locks, because the book asks for two.** `config_sha256` covers the whole agreed
object — rule 11 (Mandatory), configuration "identical, bit-for-bit on both sides",
sanction "disqualification of the game due to lack of symmetry". `scent_model_sha256` is
separate — rule 23 (Mandatory): "Lock the cryptographic hash of the scent model before
the start of the game. Sanction: **deviation from the formula cancels the game**." A
parameter table pinning `0.9` and `0.10` does not pin the model those numbers feed, which
is exactly why the second lock exists.

**Then the artifact failed its own schema — and the schema was wrong.**
`per-subgame-config.schema.json` pinned `links.config` with `"pattern": "g<NN>"`. That is
a **literal**, not a placeholder: it matched the fixture's `config_x_g<NN>.json` and
**refused every real filename**. The schema could only ever validate a template — the
precise failure `M7-23` exists to prevent, sitting inside the contract that was supposed
to prevent it.

Corrected to `^config_.+_g\d{2}\.json$`, with the valid fixture given real filenames.
The *invalid* fixture needed fixing too: it exists to prove `sub_game > 6` is refused,
and it had been failing on the placeholder instead — passing for the wrong reason, which
would have masked the case it was written for the day someone relaxed that pattern. Both
files are controlled, so `G-18` forced a bump: `0.2.7-proposed` → `0.2.8-proposed`,
manifest `88df2089…`, and 18 current-state version claims updated while three genuinely
historical ones were left alone.

**Emission is transport-free by construction (`M7-25`).** "A disconnected game still
produces its artifact set", so `write_artifact` takes a directory and an object — no
socket, no peer — and a signature test pins that. It writes to a temporary file in the
same directory then `os.replace`, so the visible file is either the old one or the
complete new one, never a prefix. Same-directory matters: `os.replace` is only atomic
within a filesystem. A half-written artifact is indistinguishable from a tampered one
during rule 19's audit, whose sanction is "score of 0 for the falsifying group".

*What is not done.* `M7-02a`/`M7-02b` stay open on one thing: the builders exist and are
schema-valid, but nothing in `orchestration/match` calls them yet. Wiring emission into a
played match, the log artifact (`M7-24`) and validation (`M7-14`) are the next batch.

#### The log a stranger verifies, and a rule about *when* a byte exists (`M7-24`, 2026-08-06)

The artifact layer is now wired: the declaration and the agreed config are written to
disk **inside `play_match`, immediately after the declaration is locked and before the
first turn is sent**. That timing is `M7-22`'s actual requirement, so it is proven by
timing — a spy records whether the file existed at each outbound turn, and every one must
see it already there. A declaration emitted at the end could have been edited to suit the
result, which is precisely what locking it beforehand rules out.

The third artifact is the one an auditor actually uses. `M7-24` asks that "a third party
can re-verify **without our code**", and `:1690` gives the procedure: the replay viewer
"takes the Nonce and the move appearing in the log, re-encodes them, and compares the
result to the original Commitment value using the SHA-256 algorithm". So the binding test
recomputes every commitment from the emitted file with nothing but `hashlib`, and a
companion test alters one move and asserts the same recomputation fails.

**The interesting constraint is `M7-24b`, and it is a constraint about time.** Rule 18 is
Mandatory: "Keep the Nonce secret until the end of the game. Sanction: **Disqualification
due to risk of dictionary attack**." A log written step-by-step with its nonces inline
violates that the moment the file is shared or committed mid-game — and the finished
artifact is **byte-identical** either way. No inspection of the final file can detect it.

So the rule is made unrepresentable instead of observed: `build_log` refuses a step
carrying `nonce` or `payload` at all, and `reveal_log` is the only way they enter. The
forbidden intermediate state cannot be written with this module, whatever the caller
intends — which for a property that leaves no trace is the only enforcement available.

*Still open.* `M7-03a`'s consumer — feeding real per-turn records from the turn loop —
plus `M7-14` (validate all four against their schemas) and `M7-03b` (the result artifact,
the last builder).

#### The report that gets emailed, and the gate in front of it (`M7-03b`, `M7-14`, 2026-08-06)

The four artifact builders are complete. The last one is the only one that leaves the
machine — `:2241` calls it "a summary of the game results, including the score of each
group in all games and the cumulative result, for the lecturer to weigh the league score".

Three Mandatory rules land in that single file, so its checks refuse rather than warn:
rule 49's **exactly four** repository links (three means one side's submission is wrong),
rule 53's per-game commit hash (code may change between games, so a result that does not
say *which* code played it cannot be reproduced), and rule 54's tokens "for the game
**and in the sequence**" — two numbers, not one.

**The asymmetry that shaped the design.** Rule 35: "a conflicting report causes
disqualification of the game and a score of 0 for **both teams**." `:2584`: a side that
does not report "will not be credited". Not reporting costs us; reporting something
contradictory costs the opponent too. So an unagreed result is refused at build time —
there is no way to construct a report this repository is not entitled to send.

**`M7-14` is a requirement about placement.** "An artifact that fails its own schema is
never sent." A validator living in the test suite proves the artifacts were valid on a
developer's machine; it says nothing about a file hand-edited at midnight. So
`validated_write` sits between building and writing, and `play_match` calls it — an
invalid config raises and leaves no file behind for anyone to attach.

Two smaller decisions worth recording. An artifact kind with **no** controlled schema is
refused rather than accepted, so "validated" never quietly means "unchecked" — which is
how an unschema'd file ends up looking exactly as trustworthy as a checked one. And
`M7-14e` compares artifacts *to each other*: a set spanning two games is the one failure
no per-file schema can catch, because every file in it is individually valid.

*Still open, and the rows now say why.* `M7-14a`/`c`/`d` are blocked on a **schema, not
on code** — the bundle carries one for the per-sub-game config only, and authoring the
declaration, log and result schemas is a contract change in its own right.

#### Three gates in front of Gmail, and a limiter that was the wrong algorithm (`M7-04`, `M7-08`, 2026-08-06)

`:2096` fixes the flow and it is not ours to rearrange: "Outgoing report → **Quota
Manager** → **Token Bucket** → **DOS Detector** → Gmail API", with three distinct outcomes
(`:2098`) — "Rejected (quota full)", "Blocked (no token)", "LOCKED (anomaly)". Three names
because they differ in remedy: *try tomorrow*, *try shortly*, *the code is wrong*.

**The gap step 1 found.** A gatekeeper already existed here, and `M7-04b` looked like
bookkeeping. It was not: the existing limiter is a **sliding window** — it drops
timestamps older than sixty seconds and counts what remains. Rule 28 (Mandatory) asks for
"a rate-limiter based on asynchronous **tokens**", and `:2085` says why the difference
matters — a bucket prevents the **bursts** that "trigger an immediate block from the
provider". A window caps a *rate*; a bucket caps a *burst* and then refills. Those are
different algorithms with different behaviour in exactly the case that draws a 429.

**Why the DOS detector does not unlock itself.** `:2087` is specific about what it is
for: "a bug or an infinite loop **in the agent's code**" — our own runaway, not a hostile
peer. A lock that cleared after a quiet period would let the same loop resume the moment
it briefly looked calm, so it stays locked until a human looks.

**Fail-fast is correctness, not efficiency.** Each gate has a side effect, so a later gate
running after an earlier refusal corrupts the counters the gates exist to protect. Two
tests pin the consequences: a quota rejection must not consume a token, or a send that
never went out would throttle tomorrow's; and a token-blocked send must not register in
the DOS window, or a legitimately throttled burst would look like a runaway loop and lock
the pipeline — a self-inflicted outage. A transmitter that *raises* still counts against
every gate, because one that only counted successes would let a failing loop retry
without limit.

`M7-04a` — "no service calls an external API directly" — is a property of the call graph,
so `send` takes the transmitting callable rather than importing one. This layer cannot
name Gmail, and a module that cannot name the API cannot bypass the gates to reach it.

*One number worth flagging:* Appendix F makes the rate a `Minimum` of 30, so a negotiated
higher value is honoured rather than clamped back down. Clamping a minimum to its floor
is the classic misreading of that table.

#### Reporting: the rules here have unusually blunt sanctions (`M7-05`, `M7-16`, `M7-17`, 2026-08-06)

Most rules in this project cost a point or invite a review. The reporting ones do not:
rule 32 — "absence of reporting **disqualifies the game points**"; rule 34 — free text
instead of an attached JSON file "will be rejected and **result in a zero score**"; rule
35 — a conflicting report scores **0 for both teams**. So every check in this layer
refuses rather than warns, and the code says which rule it is refusing on behalf of.

**The body is not a place to be helpful.** Rule 34 prohibits free text, and a polite
covering note *is* free text. The body is a fixed pointer to the attachment, and the test
asserts the result's own values do not appear in it — a check that would fail the moment
someone "improved" the email by summarising the score.

**The subject is generated because a machine reads it.** Rule 45 ties automatic report
assignment to the eight-character team code, so the code and `game_id` appear in a fixed
order. A subject written per game would sort and assign inconsistently the first time
someone was in a hurry.

**The address is a confirmed source inconsistency, not a choice.** The book prints both
spellings — `:3040` has `rmisegal`, `:3605-3606` have `rimesegal` — and lecturer answer
`AF-020` settles it (`C-004`). It is a constant here rather than a configuration value:
the destination is not negotiable with an opponent, and a peer able to move it could
silence our reporting entirely.

**Three failures, three different answers.** A 429 retries with backoff from the Appendix
F `Minimum` of 5 seconds; a constructor asking for less is refused, because a minimum is a
floor to honour rather than a value to tune down. A non-429 is *not* retried — retrying a
400 spends quota on a request that will fail identically. A permanent failure raises
loudly, since a caller that could quietly continue would convert a lost game into a silent
one. And a second send for one game is refused outright.

*Nothing here imports a Google library.* `transmit` is injected and the credential path is
checked for presence but never read, so this module cannot reach the API by itself and
cannot leak a credential. Consistent with the gates: what a module cannot name, it cannot
bypass.

*Not claimed:* `M7-15a`/`b`/`d`, the OAuth consent flow and its setup guide. Running a
consent flow means handling a real credential for a real account — the user's action on
their own machine, not something to automate from here. The code path is built and fails
closed without a credential (`M7-15c`); creating the credential is not.

#### Two sanctions that punish different people (`M7-06`, `M7-18`, 2026-08-06)

This batch makes the reporting layer honest. `build_result` already refused
`mutual_agreement=False` — but nothing set it to `True` legitimately; it was a flag a
caller asserted. It now accepts a `Settlement`, whose `reportable` is only true after the
audit passed **and** both sides returned the same outcome.

**Rule 36 fixes the audit's position, not just its existence:** "Perform a comprehensive
mutual audit log at the end of every game. Sanction: **Mandatory condition before
agreement on the JSON result**." So `agree` takes the audit as its first argument. A
precondition a caller can forget is not a precondition.

**The distinction that shaped everything else.** Two rules, two different victims:

* **Rule 19** — a technical mismatch at audit is an "iron rule" scoring 0 for **the
  falsifying group**. One side, the guilty one.
* **Rule 35** — a conflicting report scores 0 for **both teams**.

Catching an opponent's forgery is therefore *not* a reason to race them to the lecturer
with our own number: that converts their loss into a shared one. So a failed audit and a
disagreed outcome are separate states with separate messages, and a test asserts the three
refusals never collapse into one — a conflict needs a human, an audit failure needs the
evidence preserved, and silence needs the *exchange* retried rather than the report.

**Silence is not consent.** An unanswered agreement is its own state; treating a missing
reply as agreement would let a peer that crashed decide our report for us.

**A disagreement is kept, not smoothed over.** The temptation is to adopt their number to
keep the peace. That files a result we do not believe and destroys exactly the evidence an
auditor would need, so both claims sit side by side in the log's `mutual_agreement` block.

One small thing worth naming: **an empty series does not pass the audit.** Auditing nothing
must not read as auditing successfully, which is the commonest way an audit gate ends up
bypassed in practice.

#### Six sub-games, and three numbers that could have been the count (`M7-01`, `M7-07`, 2026-08-06)

The role schedule is settled rather than inferred: `U-025` closed on 2026-07-31 with a
lecturer answer relayed by the coordinator — sub-games **1, 3, 5 natural, 2, 4, 6 swapped,
Thief moves first**. It is written out as constants rather than computed as an
alternation, because a formula is one refactor away from silently disagreeing with the
answer we were given. A test pins that the two sides are opposite in every sub-game, which
is exactly the error a computed alternation makes without complaining.

**The count took reading carefully.** Appendix F prints *two* rows under the same label
`[Number of Agents]`: `:3484` is "number of players in the race | 2 | Fixed", and `:3540`
is "number of agents **in a series against an opponent** | 6 | Fixed". The second is the
games count under a mistranslated label — its own description gives it away. And the
template at `:2963` carries `"num_games": 1`, a single-game default for the example file
rather than the league requirement. Three plausible numbers; only one is the series
length. Recorded as `X-05` so nobody re-derives it.

**What resets between sub-games.** Each is a fresh game — own barrier quota, own scent
field, own belief. Carrying belief across would be worse than a bug: our score in sub-game
4 would depend on inference gathered while we were playing the *other role*, which is not
a thing the rules contemplate. Only the series identity persists, so all fourteen
artifacts share one `game_uid`.

**`M7-07` is the first row that exercises everything together** rather than in isolation:
schedule → six per-sub-game configs, each schema-validated and atomically written →
cross-artifact identity check → settlement → result artifact. That ordering was deliberate
before mirroring M7 to the Thief — a design worth copying should be one that has run.

#### Closing a gap in the method itself (2026-08-06)

Eight M7 batches ran that day — the four artifacts, the three Gmail gates, the reporting
path, the settlement layer and the six-sub-game series — and each of them ran **seven** of
the eight method steps. Step 3 asks both notebooks; I asked only the book one. Steps 6 and
7 ask for docs in both repositories; I updated only this one, on the reasoning that the
work was "Cop-only", which is not an exemption the rule offers.

I did not notice. It was caught by being asked directly whether the method had been
followed. Recorded here rather than quietly backfilled, because a method that is
selectively applied is worth less than its record suggests.

**Asking the code notebook the skipped questions found three things.**

*Two where we are stricter than the reference, deliberately.* Its artifact writer
(`report/emit.py`) writes **non-atomically** — `path.write_text(json.dumps(...))` straight
to the destination, no temp file, no `os.replace`. And its log carries nonces **inline per
record**, added only at the end. Our atomic write and our separate `audit` section both go
further; the justification is rule 19's audit phase rather than conformance, and neither
is a claim that the reference does it this way.

*One that was an actual gap.* The reference's log carries `mutual_agreement` as a
top-level key. Ours did not — while `settlement_record`'s own docstring described itself
as "the `mutual_agreement` block for the log artifact". The producer had been built and
the consumer never wired. `reveal_log` now accepts it, and it stays optional, because a
game that ended without agreement still needs its reveal written: that log *is* the
evidence of what happened.

That last one is the argument for the rule. Seven batches of correct work, and the eighth
step would have caught a dangling producer within minutes of writing it.

#### The artifacts were the wrong shape, and both notebooks had already said so (`X-06`, 2026-08-06)

Three mismatches against the lecturer's four artifact templates, all in this repository
and none in the companion Thief — so the two of us were emitting **different shapes for
the same game**, which is the first thing an auditor comparing them would notice.

* **Config**: missing `agreed_between` (`inst/:2928`) and `config_name`, and calling the
  sub-game key `sub_game` where the template and `:3019` say `sub_game_number`.
* **Log**: a `steps` array plus a separate `audit` section, where the template uses one
  **`records[]`** whose entries gain `payload` and `nonce` once the game ends. Same rule 18
  timing guarantee — the nonce still cannot exist early — but our own structure, invented
  for no gain, made the artifact diff as though fields were missing.
* **Declaration**: `links` held four repository URLs. The template's `links` names the four
  **artifact filenames**; rule 49's "four links in the JSON files of the two teams" is a
  *separate* requirement about repositories. Two requirements collapsed into one field —
  a conflation, not a shortcut, and both are now carried separately.

Our own `per-subgame-config` schema had required `sub_game`, so the correction cost a
bundle bump: `0.2.8-proposed` → `0.2.9-proposed`, manifest `245c10f1…`.

**The uncomfortable part is that this was already answered.** The code notebook had given
the exact config roster — `sub_game_number`, `config_name` and all — days-old advice from
earlier the same day. It was read off a screenshot and the significance did not register.
That is the second concrete cost of that habit within one session, after the dangling
`mutual_agreement` producer. The method now says to read answers with `read_page`; this is
why.

#### The rehearsal, and what it caught (`M7-20`, 2026-08-06)

A clean end-to-end run already existed. It proves the pieces fit; it proves nothing about
the states the rules attach sanctions to, and those are the expensive ones. So the
rehearsal runs the full six sub-games twice more — once with a **technical loss**, once
with a **tampered audit**.

**A technical loss still produces its artifacts.** Sub-game 3 ends badly and both its files
are still written, the log records the outcome, the file count is unchanged, and the series
settles and reports with 0/0 for that sub-game. That is the case a happy-path pipeline
quietly stops covering, and it is exactly when the evidence matters most.

**A tampered audit is two behaviours, not one.** The forgery in sub-game 4 is detected and
named — and then `require_reportable` refuses to report. Rule 19 costs *them* the sub-game;
filing our own contradicting report over the top would invoke rule 35 and cost us **both**
the game. A rehearsal that only proved detection would have left the expensive half
untested. The artifacts stay on disk throughout, because a failed audit is evidence rather
than a reason to withhold it.

**And it caught something the unit tests could not.** The wire role vocabulary is
`police`/`thief` (`OB-003`), while `series.Role` is an internal `cop`/`thief`. Feeding a
real audit payload through the real schema surfaced the difference immediately —
`require_wire_role` refuses `cop`. Nothing was broken, because the internal enum never
reaches the wire, but the rehearsal is the only place that distinction is visible, which
is the argument for having one.

#### What finishing the Thief's M7 found here (`X-07`…`X-12`, 2026-08-07)

The Thief's M7 closed on 2026-08-07 — 42 rows in three waves — and four of the defects it
found are **in this repository too**. Recorded here rather than silently fixed, because they
are Cop-owned rows and the batch that found them was a Thief batch; the eight-step method
wants both ledgers updated, and the one time that was skipped on "this work is Cop-only"
grounds cost two later batches a rediscovery.

**Rule 53's commit hash is missing entirely** (`X-07`). `github_commit` appears nowhere in
`src/p2p_cop_agent/`. The declaration names who played, on what hardware and with which
model, and never *which code* — the single field that makes a later audit reproducible.
Every row about the declaration passes; the field nothing asked for is the one that was
absent.

**`build_log` has no `ended_at` guard** (`X-08`), and this is the uncomfortable one: `M7-24`
already wrote down the reasoning. Rule 18's secrecy is about *when a byte exists*, a finished
log is byte-identical either way, so the only enforceable point is refusing to build the
intermediate state. The reasoning was recorded and the guard was not. In the Thief the same
guard broke thirteen existing fixtures, which is what a guard that bites looks like.

**Nothing requires a settlement before a report is composed** (`X-09`). Neither
`reporting/send_report.py` nor `reporting/gmail_message.py` mentions an agreed state.
`require_reportable` exists and is correct — but it is a call a caller can forget, and the
Thief's fix was to make the settlement record a *required argument* of the composer, on the
same argument that put the audit first in `agree(audit, ours, theirs)`.

**Configs are still not committed** (`X-10`, and `M7-27` is this repository's own deferred
row for it). `.gitignore` excludes `/logs/`, `/reports/generated/` and `/results/generated/`,
so an artifact written under any of them lives on one laptop and nowhere Appendix F
obligation 4 can see. The Thief's fix is worth copying in design: a `games/` directory that
is deliberately not ignored, a store that *refuses* an ignored destination, and a test that
reads the real `.gitignore` — because the way this regresses is somebody tidying the tree.

**One thing was already right** (`X-12`): `gmail_message.py` uses `urlsafe_b64encode` and
keeps its padding. Recorded so it is not re-derived. The two traps are worth knowing anyway —
the two base64 alphabets differ in exactly two characters, so most messages encode
identically under either and a casually chosen fixture cannot tell them apart; and the
padding-stripping idiom comes from JWT, where padding is forbidden, which is a different
specification for a different field.

#### M9 begins with the scan that gets more expensive every commit (`M9-04b`, 2026-08-07)

`check_secrets.py` answers "is there a secret in the files that exist now". At submission
that is the wrong question: rule 39 forbids secrets being *in the repository*, and a
credential deleted three commits ago is still in every clone. `scripts/scan_git_history.py`
walks every blob reachable from any ref.

**It found one thing, and it is a false positive that can never be edited.** A
`docs/PROMPT_LOG.md` blob contains my own prose describing a dummy test vector built by
string concatenation. The working-tree copy was rephrased the day the file-level scanner
flagged it — correctly — but that blob is in 2350 objects' worth of history and in every
clone.

The resolution is the interesting part. Rewriting history over a false positive would
invalidate every clone and change every commit hash after it, **including hashes already
recorded in emitted artifacts under rule 53** — a cost only worth paying for a real leak. An
allowlist was refused for the reason it is always refused here: a pattern suppression turns
off a rule everywhere and forever, including on a credential committed tomorrow.

So the finding is pinned by **blob SHA**. A content address is the hash of exact bytes a
human read; different content is a different SHA and fires again, so a secret cannot hide
behind the entry without producing a collision. `test_history_scan.py` holds that distinction
in place: pins must be full 40-hex SHAs, must carry a written reason and a review date, must
point at a blob history still contains, and the table must stay small enough to re-read. The
Thief has no such table and a test asserts it stays absent — an unused suppression mechanism
is one somebody eventually reaches for.

`X-11` closed on the way: `line_findings(line)` is split out of `findings(path, root)`, so
the detection rules can be tested directly *and* applied to a blob that no longer exists on
disk. Without the split the history scanner would have restated the patterns, and two copies
of a security rule drift in exactly one direction.

#### What the Thief's M9 batch found for here (`X-13`…`X-17`, 2026-08-07)

Five rows, recorded rather than fixed — they are Cop-owned, and the batch that found them was
a Thief batch. One of them is a correction to reasoning, not to code.

**A nonce argument used in both repositories is wrong** (`X-13`). The Thief's `games/README.md`
justified excluding game logs from the repository because committing them would publish
nonces, "and git history has no end". Rule 18 (`inst/:3354`) keeps a nonce secret **until the
end of the game**, and the book defines Step 4 as the Final Reveal: "Only at the end of the
game are all values, including the Nonce, revealed for a full mutual audit" (`inst/:1136`).
The obligation *expires* — revealed nonces are precisely what lets a third party recompute
every commitment. Worth checking whether the same wrong reason appears here.

**The commit obligations differ per artifact** (`X-14`), and `M9-27` reads as though they do
not. Config is mandatory (Appendix F obligation 4); the log has no explicit commit duty but is
needed for the Replay threshold; the result's duty is email. A checker demanding all four
would fail a submission that satisfies the rules.

**`M9-09c`'s wording overclaims** (`X-15`). "Record proof that each report was sent" invites a
delivery claim, and the book's decisive layer is receipt at the lecturer's address (p.78/183)
— which a sender cannot observe. The Thief named its type `SendReceipt` rather than
`ProofOfDelivery` and writes the limit into every record.

**Two gates are missing here** (`X-16`, `X-17`). A clean-clone runner — the Thief's caught two
failures on its first run with every gate green in the working tree, because a clone holds
only what was committed. And a replay of a match read back **off disk**: every replay test in
both repositories builds records in memory, `json` round-tripping is not identity, and the
commitment is over canonical bytes, so an in-memory-only verifier can pass forever while every
stored log fails.

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

**The belief layer now exists** (`M6-01`…`M6-03`). Scent emission and multiplicative
decay are implemented and hash-locked (see the `M6-07` section above); `strategy/belief.py`
maintains a Cop-local probability distribution over the Thief's position, updated by
Bayes from observation only, and `strategy/belief_pursuit.py` aims the policy at
`argmax b(s)` rather than at a last-known cell. The belief is Cop-private and never
crosses the wire.

**The hint layer closed on 2026-08-06** (see the `M6-02`/`M6-11` section above).
`strategy/hint_decode.py` turns an opponent's free text into a directional likelihood,
`strategy/trust.py` carries the reliability factor and the lie test, and
`strategy/consume.py` folds one turn of scent and one hint into belief in the book's
order. The Cop now reads a hint as *evidence weighted by how honest that opponent has
proved so far*, never as an instruction.

What remains open is named rather than glossed: the optional **LLM adapter** (`M6-05`)
behind the zero-token template provider, and wiring hint generation into every turn
(`M6-10`). Neither changes how a move is chosen — the movement decision is pure Python
and stays that way `[AE-25]`.

This is still the floor rather than the deliverable — but it is no longer the *blind*
floor it was, and it is no longer credulous either.

### 4. Learning curves

The book requires learning curves **"if RL was used"** (p.81/189). This policy is
deterministic and weight-free — a fixed lexicographic ranking, nothing fitted from data —
so there is no convergence to plot, and asked directly, the book is silent on a substitute.

In its place, [`docs/RESEARCH-REPORT-Performance-Analysis.md`](docs/RESEARCH-REPORT-Performance-Analysis.md)
answers the question a learning curve answers — *is this policy actually better, and by how
much* — by measurement over **40 paired seeds**:

![Capture rate and mean score by strategy arm](assets/chart-strategy-comparison.svg)

| Arm | Capture rate | Mean turns | Mean Cop score |
|---|---|---|---|
| blind | 0.225 | 32.83 | 8.38 |
| **belief** | **0.975** | **12.83** | **19.62** |
| oracle (illegal ceiling) | 1.000 | 12.10 | 20.00 |

Belief closes **96.8%** of the blind-to-oracle gap, wins **30 of 40** paired seeds and
**loses none**.

![Cop score distribution by arm](assets/chart-strategy-distribution.svg)

The distribution is where a mean alone would have misled: the blind arm's median score is
**5.0**, with Q1 = Q3 = 5.0. It is not a weak pursuer — it is almost always a *non*-pursuer
that occasionally stumbles into a capture, and its 8.38 mean is that rarity averaged over
many failures.

**Two sweeps came back flat, and probing them found more than the sweeps did.** The barrier
quota is identical to four decimals at every value — not because the quota is irrelevant,
but because this arm places **zero barriers in 501 decisions**; the squeeze machinery exists
and is tested but is not wired into it. Board size is flat because on a 12×12 board the
Thief never reaches past index 7 of 11 within the horizon, so the extra ranks are space
nobody visits. Both are recorded as findings about our own agent rather than as parameter
conclusions.

Nine charts, all SVG, all regenerable:

```text
uv run python scripts/run_experiments.py
uv run python scripts/render_charts.py
```

### 5. Live belief map and "Verified OK" replay screenshots

**The verifier behind the `Verified OK` stamp now exists; the screen that shows it does
not yet.** That is a narrower gap than before, and worth stating precisely because rule 20
is Mandatory with the sanction "threshold condition for confirmation of logs and submission
of the project" (p. 129/272) — this is the one deliverable whose absence is a rejected
submission rather than a lost mark.

`src/p2p_cop_agent/replay/` loads a saved log, recomputes every SHA-256 commitment from the
file's own bytes, and reaches one of exactly two verdicts. `:1753` decides the scope: one
altered step invalidates the entire match, so the banner is a match verdict, not a per-step
annotation. The cursor steps forward, back, jumps to a step, and jumps straight to the
first divergence — and the verdict is **recomputed on every one of those moves**. It is a
property with nowhere to cache; a stamp computed once at load and painted thereafter would
be a claim about the past tense, which is not what a submission screenshot should be.

**It verifies logs we did not write.** Rule 36 mandates a "comprehensive mutual log audit"
as a necessary condition for agreement (p. 131/276), and p. 39/102 spells it out: "each
side presents its full log … each side reconstructs the opponent's data through the
revealed nonces". The test fixtures are therefore built by a writer that imports nothing
from this package and emits a deliberately foreign shape — an unknown `schema_version`,
keys we never write. A verifier fed only its own output would confirm that our writer
agrees with our reader, which it always will.

**A test we nearly wrote as a formality found a real hole.** Forging a log by copying a
real record and changing only its *visible* `step` passed cleanly: the commitment binds the
sealed payload and says nothing about the `step` and `move` keys a viewer actually paints
on the board. A forger could leave the seal untouched, rewrite only the display, and
collect a green stamp over a game nobody played. `:1691` closes it — the viewer re-encodes
"the Nonce and the move **appearing in the log**" — and the verifier now cross-checks every
visible field against the sealed one.

**A structural hole the first batch shipped, found by reading the other repository's
requirement list.** Every commitment covers a single record, so a log with its records
shuffled, one deleted, or one duplicated survives every digest. Measured directly against
the shipped verifier: all three came back `Verified OK`. Both repositories carried a
"detect a reordered log" row; only one list was read in full, and the row that was never
claimed is precisely the one that shipped broken.

The fix deliberately does **not** turn those into a red banner. Rule 19 is "any mismatch
**in the digest**" (p.129/271), so structural damage is a different rule with a different
sanction — a gap makes the two peers' reports contradictory under rule 35 (p.131/275),
which scores zero for **both** teams, and shows an illegal state jump under rule 5. Neither
the book nor the reference checks ordering at all; the reference verifies each record "with
no reference to its place in the sequence". So an opponent's log that is merely ordered
differently is not evidence of forgery, and red-bannering it would be a false accusation
carrying "no appeal process". Findings are reported with the rule they answer to and left
for settlement, where both logs are actually compared. Recorded as `U-032`.

One test also had to be replaced rather than extended: it asserted that its own fixture had
a gap and never that the verifier noticed, so it would have passed against no
implementation at all.

What remains for the screenshot is the **view**: a window that paints the banner, plus the
belief map from a live two-peer run. The `Verified OK` capture belongs "within the README.md
academic report" (p. 81/189, "absolute mandatory"); the exact filename and directory are
**not specified** by Appendix E or the submission checklist, so that will be a recorded
project choice rather than an inferred one.

### The replay viewer

![Replay viewer showing a green Verified OK stamp over an eight-step log](assets/replay-verified-ok.png)

*`assets/replay-verified-ok.png` — the mandatory submission capture (`:1769`; "absolute
mandatory" at p.81/189). Every commitment in `log_verified_ok.json` was recomputed from the
file's own bytes at the moment the picture was taken.*

The screen shows what the book asks a replay viewer to show: for each entry the `nonce`,
the `move` and the original `commit` (p.56/142); a verdict indicator — a green
`Verified OK` stamp or a red `TAMPERED` banner; and controls to move "back and forth in
time" (p.56/141). It does **not** draw the board, because the board is not a requirement
and the belief map belongs to the live GUI, where the book puts it.

![Replay viewer showing a red TAMPERED banner with step 5 highlighted](assets/replay-tampered.png)

*`assets/replay-tampered.png` — the detection path. Not a mandatory submission item; asked
directly, only `Verified OK` is. It is captured anyway because a viewer shown only passing
is a viewer that might not be checking anything.*

Both images are regenerated from committed fixtures rather than kept as session artefacts,
which is `M8-05d`'s condition — "a grader can regenerate them":

```text
uv run python scripts/capture_replay_screenshots.py
```

They are real screen captures of the real widget tree, photographed through the Windows
GDI. Drawing a picture of what the app *would* look like would be a fabricated exhibit,
which is the one thing a verification screenshot must never be.

**The widgets contain no logic.** `M8-06` requires that "no widget touches domain or
protocol code directly", so `replay/view_model.py` turns a cursor into frozen,
display-ready values and `ui/replay_app.py` reads nothing else. That boundary is what makes
the screenshot testable: a Tk window cannot be asserted about in CI, but the frame behind
it can, so the stamp text and colour in these pictures are pinned by
`test_replay_view_model.py` rather than by someone having looked once. The reference
simulator draws the same boundary — its widgets are dumb components handed ready-made
strings.

Two things about the capture were not free. The first attempt came out shifted, with a
strip of desktop down one edge and the title bar along the top, because Tk reports logical
pixels while the GDI works in physical ones — on a scaled display every window coordinate
is wrong by the scale factor. Declaring the process DPI-aware is what makes the output a
function of the fixture rather than of the machine's display settings.

### The live GUI

![Live GUI showing a belief heatmap with a green YOUR TURN banner](assets/live-gui-belief-map.png)

*`assets/live-gui-belief-map.png` — the second mandatory submission capture (p.81/189,
"absolute mandatory"). Taken during a live match: a second operating-system process was
started, turns crossed a real socket, and the heat map is whatever this agent believed at
step 2. Asked directly, a reconstructed state would not satisfy the requirement — that is
the replay viewer's separate exhibit.*

**The opponent is a scripted local peer, not a classmate.** A second agent that plays back
is still open work, so this is a live match against a stub and is described as such rather
than implied to be a league game.

**What the screen can never contain.** Rule 8 (Mandatory) — "display true local information
only", sanction "disqualification due to data breach". Rule 9 (Prohibited) — "do not display
the full objective board state", sanction **project disqualification**. That is the whole
project, not a game, so it is enforced structurally rather than by discipline: `LocalTruth`
has a closed field set with nowhere to hold the opponent's real position, and
`test_local_truth_boundary.py` fails if anyone adds a field or if the live package imports
anything that knows one. The reference does the same — its snapshot fixes what crosses to
the GUI, so its window "is incapable of drawing" the opponent.

The `T?` mark is not a leak. It is *our inference* from scent, which is what a trust map is
for; `:1647` forbids showing the objective board, not showing a guess.

**Colour is not the only signal.** Every believed cell also prints its probability, and the
most likely one is marked in text, so a greyscale print or a red-green deficiency loses
nothing.

Two findings came out of producing this picture rather than out of building the widget.
The first capture rendered sixty-three cells as `0%` and one as `100%`: belief converges
fast because scent evidence is strong and consistent — measured at peak 0.28 after one
update, 0.32 after two, 0.86 after three and 0.99 by the fourth. Capturing "later in the
match" is not more impressive, only less informative, so the script captures at step 2 where
the inference is still visibly an inference. The second is that rounding a diffuse belief to
`0%` prints a board claiming the opponent is nowhere, which is the opposite of what the
number is for; below one percent the label now reads `<1%`.

Both images regenerate from committed inputs:

```text
uv run python scripts/capture_replay_screenshots.py
uv run python scripts/capture_live_gui_screenshot.py
```

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
