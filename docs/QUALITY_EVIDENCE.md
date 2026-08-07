# Quality evidence — the four metrics, ISO/IEC 25010, seams, concurrency

Covers `M9-08`, `M9-08a`, `M9-08b`, `M9-08c`, `M9-15`, `M9-15a`…`M9-15d`.

Two frameworks apply, from **different sources**, and the difference is worth stating:

* **The four success metrics** are the book's, Table 4 (p.94/211). They are what the project
  is judged on.
* **ISO/IEC 25010's eight characteristics** come from the *submission guidelines* §13.1
  (`inst/software_submission_guidelines-V3_Summary.md:816`). The term appears nowhere in the
  book — asked directly, the book notebook returned `NOT-SPECIFIED-IN-BOOK`, offering chapter
  11.3 (p.93/209) as the nearest equivalent: "professional code is written so it can be read,
  tested and reproduced by others".

Weak evidence is marked weak below. A self-assessment at full marks is a claim, not evidence.

## The book's four success metrics (Table 4, p.94/211)

### Coordination — `M9-15a`

*The book's wording:* a P2P protocol over FastMCP, turn management and synchronisation
between two autonomous agents with no central server and no external referee (chapter 2).

| Evidence | Where |
| --- | --- |
| A launchable peer that plays a real match | `p2p-cop serve`, `adapters/serve.py` |
| Two OS processes over localhost | `tests/integration/test_localhost_two_processes.py` |
| Turn ordering and negotiation refusal | `orchestration/phases.py`, `test_localhost_negotiation.py` |
| The shared wire bundle this repository owns | `shared_contract/`, `scripts/generate_shared_manifest.py` |

**Asymmetry worth naming.** This repository can be launched; the companion Thief cannot —
its CLI is a scaffold (`M9-025` there). A counted game needs both, so coordination is proven
between two *Cop-side* processes and against a synthetic peer, not yet between the two real
agents from a terminal.

### Adaptation — `M9-15b`

*The book's wording:* two symmetric agents under uncertainty — a belief map over the
opponent's position, the opponent's verbal hints, and a scent-trail network (chapters 4, 6).

| Evidence | Where |
| --- | --- |
| Belief distribution updated by Bayes from observation only | `strategy/belief.py`, `strategy/belief_pursuit.py` |
| Policy aims at `argmax b(s)`, not a last-known cell | `strategy/belief_pursuit.py` |
| Scent emission and decay, hash-locked under rule 23 | see the `M6-07` section of the README |
| Belief is Cop-private and never crosses the wire | `test_belief_privacy.py` |

### Integrity — `M9-15c`

*The book's wording:* preventing forgery through SHA-256 commit-reveal, and a full log-audit
phase at end of game (chapter 5).

| Evidence | Where |
| --- | --- |
| Commit-reveal over canonical bytes | `protocol/commit.py` |
| Audit precedes agreement structurally | `orchestration/settlement.py` |
| Two sanctions kept distinct — rule 19 vs rule 35 | `require_reportable`, and its README section |
| A stored match re-verifies off disk | `tests/integration/test_replay_of_stored_match.py` |
| No secret in history | `scripts/scan_git_history.py` — 2363 objects, 1 reviewed, 0 unreviewed |

### Architecture — `M9-15d`

*The book's wording:* the Orchestrator and Gatekeeper patterns, and failure-resistant code
(chapters 8, 10).

| Evidence | Where |
| --- | --- |
| One gatekeeper for every external call | `services/gatekeeper.py` |
| The orchestrator owns the series | `orchestration/series.py`, `orchestration/match.py` |
| Artifacts survive a dead transport | `reporting/emit.py` (atomic write, no socket) |
| A technical loss and a forged audit both still emit | `test_rehearsal_invariants.py`, `test_rehearsal_tampered.py` |

## ISO/IEC 25010, guidelines §13.1 — `M9-08a`

| Characteristic | Evidence | Where it is weak |
| --- | --- | --- |
| **Functional suitability** | Rules with sanctions have named tests; `docs/REQUIREMENTS_LEDGER.md` maps rule → code → test | Provisional under `U-019`; the artifact field set may still move |
| **Performance efficiency** | `docs/RT-Performance-Analysis`, `scripts/bench_decision.py`, `scripts/experiment_arena.py` | No profiling against an adversarial peer |
| **Compatibility** | `shared_contract/` bundle with a manifest; unknown wire fields tolerated after `X-02` | Never validated against a classmate's agent |
| **Usability** | `p2p-cop serve` runs a real match; live GUI and replay app; `docs/USAGE.md` | No user testing |
| **Reliability** | Atomic writes, watchdog, deadline tracker, backoff, bounded queues | Mid-series crash recovery untested |
| **Security** | Send-only OAuth scope, private-field guard by key name, secret scan over tree and history | No threat model. One reviewed history false positive, pinned by blob SHA |
| **Maintainability** | 150-line cap, 97.48% branch coverage, a PRD per mechanism | Coverage is lower than the Thief's 99%; some modules split for the cap, not cohesion |
| **Portability** | `uv.lock` frozen install, `scripts/verify_clean_clone.py` | **Windows only**; `M9-12a` (second machine) open |

## Extension seams — `M9-08b`

* **Strategy.** `strategy/baseline.py` and `strategy/belief_pursuit.py` share a call shape;
  the policy is injected into the orchestrator rather than selected inside it. Movement is
  pure Python and deterministic, so a new strategy is testable without a model.
* **Verbal provider.** The shipped default is a zero-token template provider, which is why
  the suite is deterministic and needs no API key. A live model substitutes at that seam.
* **Transport.** `adapters/` is injected at every use site; tests pass recording doubles
  through the same seam a real provider would use.

## Concurrency — `M9-08c`

| Where | What runs | Why it is safe |
| --- | --- | --- |
| `adapters/serve.py` | The peer's event loop | One loop owns the mailbox; a full queue refuses rather than blocking or growing |
| `services/watchdog.py` | Deadline supervision | Time is injected — no background thread; a test advances a number instead of waiting |
| `tests/integration/localhost_peer.py` | A second interpreter | A real subprocess with no shared memory |

**No shared mutable state crosses a thread boundary in `src/`.** The belief map, the scent
grid and the ledgers are each owned by one agent.

That is deliberate rather than incidental: rule 2 (Prohibited) forbids sharing memory or
variables between parties at all, with immediate disqualification for data leakage as the
sanction. The safest concurrency story available is the one where there is nothing to share,
and the design was chosen so that is true — not so it could be argued afterwards.
