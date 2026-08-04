> **KEEP WITH WARNING.**
> This document records development provenance.
> Prompts and AI outputs are not authoritative requirement evidence and cannot independently change a requirement to `CONFIRMED`.
> Historical output statements are time-scoped. P-011 records corrections where later
> direct evidence disproved parity/candidate/schema claims.

# PROMPTS — Prompt Engineering Log ("Prompt Book")

- **Document version:** 1.00 · **Status:** LIVING DOCUMENT — update with every significant AI-assisted step (guidelines §8.3)
- **Purpose:** record all significant prompts used to build the project: context/goal, the prompt, output received, refinements made, and best practices derived.

> Entry template:
> **P-###** · date · tool/model · **Goal** · **Prompt (essence)** · **Output** · **Refinement** · **Lesson**

---

## P-001 — Source-document digestion
- **Date:** 2026-07-23 · **Tool:** Claude (agentic CLI)
- **Goal:** make the 160-page rulebook PDF usable as build context.
- **Prompt (essence):** "Analyze `police_thief_p2p_Summary.md`" → then "pass page after page and make a summary for each single page, so a builder model won't lose context because the file is too big."
- **Output:** `Material/police_thief_p2p_PerPage_Condensed.md` — 160 pages compressed ~6× (262 KB → 43 KB) with page anchors (P1–P160), a master quick-reference of binding Appendix-F parameters, and all formulas/code kept verbatim.
- **Refinement:** front-loaded a "Master Quick-Reference" section so a builder that reads only the top still gets every binding value and disqualification trap.
- **Lesson:** for long specs, per-page anchors + a front-loaded binding-values table beat prose summaries; keep formulas and config exact, compress narration.

## P-002 — Reference-simulator analysis
- **Date:** 2026-07-23 · **Tool:** Claude (agentic CLI)
- **Goal:** understand what the lecturer's `Game-P2P-Cop-Chase` engine provides vs. what remains our work.
- **Prompt (essence):** "Analyze the SimulatorEXM-Repo the lecturer gave us"; "run it so I can see it"; "how does the LLM work inside it without an API key?"
- **Output:** full architecture map (sdk/peer/domain/infra/shared/gui layers); a live headless match (thief survival 35 steps, audit 36/36 verified, 0 tokens); the finding that the default banter provider is a zero-token template and the LLM is never used for moves.
- **Refinement:** identified deviations where the book wins (subtractive vs. multiplicative scent decay) — later codified as ADR-5.
- **Lesson:** run reference code and read its config before designing; explicitly log where a reference deviates from the binding spec.

## P-003 — Core documentation suite
- **Date:** 2026-07-24 · **Tool:** Claude (agentic CLI)
- **Goal:** produce the mandated pre-code docs (guidelines §2.2, §2.5).
- **Prompt (essence):** "Should we start building the requested md files?" + decision answers: *clean reimplementation*, *core docs first*.
- **Output:** `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md` v1.00 (requirements, C4 architecture + ADRs, phased roadmap).
- **Refinement:** the approach decision (clean reimplementation vs. build-on-engine) was asked explicitly before writing — it changes the whole PLAN.
- **Lesson:** resolve architecture-defining decisions with the human *before* generating docs, not after.

## P-004 — Work-breakdown expansion (620 tasks)
- **Date:** 2026-07-24 · **Tool:** Claude (agentic CLI)
- **Goal:** granular, checkable task list for the whole project.
- **Prompt (essence):** "Rebuild all the md files under docs so the TODO has 600+ tasks."
- **Output:** `TODO.md` v2.00 — 620 sequential tasks (T001–T620), 9 phases, per-area "Done when" gates, priorities P0/P1/P2; PRD gained a traceability matrix; PLAN gained a module→task inventory.
- **Refinement:** IDs made globally sequential and grep-verifiable (`grep -c '^- \[ \] \*\*T'`); count checked mechanically, no duplicates.
- **Lesson:** make generated task lists mechanically verifiable (stable IDs, one task per line) so completeness claims can be checked, not trusted.

## P-005 — Per-mechanism PRDs
- **Date:** 2026-07-24 · **Tool:** Claude (agentic CLI)
- **Goal:** the specialized PRDs required per algorithm/mechanism (guidelines §2.3).
- **Prompt (essence):** "Write the 5 per-mechanism PRDs" + "what else did the instructions ask for?" (surfaced the prompt-log requirement → this file).
- **Output:** `PRD_commit_reveal`, `PRD_scent_belief`, `PRD_strategy`, `PRD_p2p_mcp`, `PRD_gatekeeper_reporting` — each with theoretical background, requirements, I/O contract, metrics, constraints, alternatives-considered, success criteria, test scenarios.
- **Lesson:** mirror the rubric's required section list exactly; verify with a section-presence grep.

## P-006 — Review pass against sources (v2.10)
- **Date:** 2026-07-24 · **Tool:** Claude (agentic CLI)
- **Goal:** re-read Material sources and audit docs for gaps.
- **Prompt (essence):** "Read the md files under Material, check docs, enhance/fix what you find."
- **Output:** four confirmed gaps fixed across all docs: (1) the **Acknowledge** step of the commit-reveal sequence (Commit→Ack→Reveal→Final-Reveal) was missing; (2) **barrier-on-thief-cell capture** + honest capture answer missing from FR-4; (3) **NL-only hint rule / no coordinate protocols** (Appendix E rules 26–27) missing; (4) official **series = 6 sub-games** (Appendix F Table 18) + league integrity rules (one counted game per opponent, conflicting reports → 0/0) missing. Also added: mermaid state/sequence diagrams, threading model, coding/testing standards, `world` config section, addendum tasks T621–T632.
- **Lesson:** always re-audit generated docs against the binding source with targeted greps on suspected weak spots (protocol steps, fixed parameters, prohibition rules) — summaries drop steps that "feel" implicit, like an ack.

## P-007 — Full compliance audit vs. all three sources (v2.11)
- **Date:** 2026-07-24 · **Tool:** Claude (agentic CLI)
- **Goal:** verify every doc claim against the condensed spec, the full rulebook translation, and the submission guidelines.
- **Prompt (essence):** "Check if everything is made according to `police_thief_p2p_PerPage_Condensed.md`, `police_thief_p2p_Summary.md` and `software_submission_guidelines-V3_Summary.md`."
- **Output:** rule-by-rule sweep of Appendix E (55 rules) + Appendix F tables + guidelines §1–20 against PRD/PLAN/TODO/5 PRDs. Three confirmed gaps fixed: (1) **rule 49** — the game-end JSON needs **four** repo links (two per team), docs said "both"; (2) **rule 23** — the scent-model pre-game crypto-lock was only implicit in the signed `game.json`, now explicit in NET-7 + scent PRD; (3) guidelines **§10** UI documentation (workflows, accessibility, Nielsen heuristics) had no task. Plus stale "620-task" references reconciled to 635. New tasks T633–T635 (Addendum B).
- **Lesson:** suspicious grep targets for audits are *counted things* ("both", "two", "all") — a source that says "four links" while the doc says "both links" is exactly the class of bug summaries introduce; verify every quantity against the primary source, not the derived one.

---

## P-008 — Requirements audit and legacy-document remediation

- **Date:** 2026-07-24 · **Tool:** Codex
- **Goal:** prevent pre-verification plans from being mistaken for approved requirements.
- **Prompt (essence):** audit every repository file, quarantine unsupported configuration, confirm only directly supported structural requirements, and remove active-looking legacy planning documents.
- **Output:** the first repository audit created evidence ledgers and quarantine notices; the remediation moved unsafe configuration drafts, confirmed the structural baseline, archived the complete legacy PRD/PLAN/TODO/mechanism documents, and replaced active copies with short verified-phase stubs.
- **Mistake corrected:** quarantine warnings alone were insufficient, especially when large documents could be read partially or when warnings were not encountered before implementation details.
- **Lesson:** unsafe historical plans belong in an explicit archive; active documentation should expose only current verified status and link to evidence.

---

## P-009 — Documentation completeness pass (Repos agent + Supervisor setup)
- **Date:** 2026-07-24 · **Tool:** Claude (agentic CLI)
- **Goal:** confirm the `docs/` folder satisfies the guidelines' mandatory-documentation list, and stand up the two-agent (Repos + Supervisor) workflow requested by the team.
- **Prompt (essence):** "Check the docs folder and all its md files against `software_submission_guidelines-V3_Summary.md` so the lecturer will not deduct points; verify the TODO is not the 600+-task version; add a Report section to the README noting the supervisor + repos agents."
- **Output:** `docs/DOCS_COMPLETENESS.md` — a §2-by-§2 matrix showing every mandatory document is present (README, PRD, PLAN, TODO, five mechanism PRDs, PROMPT_LOG, companion cross-link) with per-file content status. At that commit the active `docs/TODO.md` was described as a 16-task verified-phase stub while the full 635-task plan stayed under `archive/pre-audit/documentation/TODO.md`; the active count later changed and P-011 supersedes the count claim. Added a `## Report` section to `README.md` (development work log + Supervisor/Repos two-agent note).
- **Refinement:** kept requirement-dependent stubs unchanged rather than padding them — a stub is a deliberate verified-phase state, and inventing content would break the source hierarchy.
- **Lesson:** "completeness" for a submission means *every mandatory file exists*; content depth is a separate, later gate driven by `CONFIRMED` evidence. Prove presence explicitly in a checked-in matrix so the grader sees nothing is missing.

---

## P-010 — Batch-2 requirements enrichment + gap closure
- **Date:** 2026-07-25 · **Tool:** Claude (agentic CLI, Repos agent)
- **Goal:** stage confirmed structure and candidate parameters from the three sources, resolve open conflicts, and close the mandatory-requirement gaps found by a full guidelines/book scan — without inventing any value.
- **Prompt (essence):** "Fix everything needed" after a two-agent scan of `software_submission_guidelines-V3_Summary.md` and `police_thief_p2p_Summary.md` surfaced ~12 mandatory items missing from the active docs.
- **Output (six commits):** (1) `PARAMETERS_BASELINE.md` — Appendix F candidates, flagged pending at that time; (2) resolved `C-001`/`C-002`, pruned `U-011`/`U-012`, added `SR-007`–`SR-010` + `PS-010`, and claimed the shared registers had converged byte-identically; P-011 later disproved that parity claim with Git-blob hashes; (3) enriched the five mechanism PRDs with cited confirmed structure and added `PRD_gui.md` + `PRD_replay.md` (the missing mandatory GUI/replay deliverables); (4) `SUBMISSION_CHECKLIST.md`, Tier-2 deferred deliverables into the TODO, methodology-doc updates, fixed the false `.env-example` "neutral" claim; (5) neutralized the Thief `.env-example`; (6) this log.
- **Refinement:** every numeric value was initially routed to `PARAMETERS_BASELINE.md` with a "pending official confirmation" flag; the later direct Appendix-F pass closed that status. Only structural/rule shapes carrying an Appendix E rule citation were promoted to `CONFIRMED` (Rule A); externals (MCP tool names, formal JSON schemas, Ruff, team identity) stayed `UNKNOWN` (Rule C).
- **Lesson:** the 635-task backlog archived earlier hid mandatory deliverables (architecture, GUI, replay, version tracking) from the active set; re-audit the *active* docs against the primary rule list, not just the file inventory.

---

## P-011 — M0–M1 contract/scaffold correction

- **Date:** 2026-07-25 · **Tool:** Codex multi-agent implementation
- **Goal:** correct active documentation, create a source-backed proposed shared
  contract, and add a behavior-free independently installable Cop scaffold.
- **Prompt (essence):** verify primary sources and current Git state; do not invent
  requirements; keep the contract unfrozen until Thief acceptance and hash parity.
- **Output:** corrected the false cross-repository parity claims; promoted directly
  verified Appendix-F values from “candidate” status; separated known 1.1 artifact
  key sets from unknown formal constraints and Appendix-B shared config 1.2; added
  ADR-001–010; replaced blanket blocking with explicit gates.
- **Correction to P-009/P-010:** the active TODO had grown beyond the earlier
  “16-task” description, the active mechanism inventory is seven PRDs, and Git-blob
  hashes proved that the named shared documents were not byte-identical. Exact
  baseline evidence is in `docs/PARITY_REPORT.md`.
- **Simulator boundary:** pinned behavior is a candidate/reference only; the
  educational-use EULA prevents treating it as an MIT submission skeleton.
- **Refinement:** contract `0.1.0-proposed` remains **UNFROZEN**; no MCP,
  envelope/idempotency, or commit-canonicalization runtime choice was silently
  frozen.
- **Lesson:** distinguish confirmed rule/value, observed template key, simulator
  candidate, ADR proposal, and byte-parity evidence as five different claim types.

---

## P-012 — Coordinator-directed M1 contract revision

- **Date:** 2026-07-26 · **Tool:** Codex implementation agent
- **Goal:** correct the Cop-owned shared-contract candidate from exact base
  `84339c210c8e3293d972bccec5912abf519d502c` without merging PR #6 or beginning M2.
- **Prompt (essence):** apply the controlling cross-repository audit; correct source
  hierarchy/provenance; separate league, match, and private configuration; validate a
  neutral participant agreement; distinguish local integrity from optional
  cross-root comparison; add rejection vectors, CI, and an M0–M9 Cop roadmap.
- **Output:** contract remains `0.1.0-proposed` and unfrozen; local artifacts are
  `NEEDS_MANUAL_REVIEW`; `config_sha256` remains `null` behind a P0 canonicalization
  blocker; 17 controlled files and a separate manifest self-hash are recorded in the
  candidate handoff.
- **Lesson:** local manifest success is not cross-repository parity, and structural
  hash-shape validation is not semantic canonical-hash verification.

---

> **Provenance note for P-013 … P-017.** These entries were reconstructed on
> 2026-08-01 from the commit record, the documents each step produced, and the
> `Co-Authored-By` trailers, because the log had fallen behind between 2026-07-26 and
> 2026-07-31. They are **not transcribed from the original sessions**: each
> "Prompt (essence)" line records the evident task and the human's stated intent, not
> verbatim wording. P-018 onward were written in the sessions that performed them.

## P-013 — Hardening the contract before letting any code depend on it
- **Date:** 2026-07-26 → 2026-07-27 · **Tool:** Claude (agentic CLI) · *reconstructed*
- **Goal:** make the shared contract safe to build on: correct provenance, separate the three configuration scopes, and stop treating a local check as external agreement.
- **Prompt (essence):** apply the cross-repository audit; fix the source hierarchy so a simulator observation can never outrank the book; split league-wide, per-match, and private configuration; add rejection vectors and CI.
- **Output:** canonical shared-configuration lock; league/match/private separation; neutral negotiated-configuration validation; cross-root comparison and rejection vectors; enforced quality gates in CI; M1 marked ready for external parity review.
- **Refinement:** an initial claim that the bundle was "ready" was walked back to *locally verified, externally unfrozen* — the distinction that the contract checker still enforces by failing closed.
- **Lesson:** "our checks pass" and "the other side agrees" are different claims, and a document that blurs them will be believed later by someone who cannot re-derive the difference.

## P-014 — Building the domain under an explicit authorization
- **Date:** 2026-07-28 · **Tool:** Claude (agentic CLI) · *reconstructed*
- **Goal:** implement M2 (coordinates, board geometry, legal movement, barriers, capture) and M3 (scoring, local state, rules harness, deterministic pursuit) while the contract stayed unfrozen.
- **Prompt (essence):** proceed with the work that does not depend on the frozen contract, under the coordinator's authorization, and keep it reachable only through the SDK.
- **Output:** immutable domain types, barrier-aware movement, capture conditions, the fixed scoring table with the technical-loss sanction, immutable Cop-local state with reproducible history, a single-process rules harness, and a deterministic barrier-aware pursuit baseline.
- **Refinement:** two rules were corrected after implementation — a Police barrier on its **own** cell is legal, and role alternation was withdrawn from the contract and recorded as the open unknown `U-025` rather than left as an assumption.
- **Lesson:** withdrawing a claim into a numbered unknown is cheaper than defending it. `U-025` was later closed by an actual lecturer answer, which would have been impossible if the guess had stayed buried in code.

## P-015 — Commit-reveal, and proving it against something other than itself
- **Date:** 2026-07-28 → 2026-07-29 · **Tool:** Claude (agentic CLI) · *reconstructed*
- **Goal:** close M4 — message surface, canonical bytes, commit-reveal, replay/idempotency rejection, tamper detection, and Step-0 attestation.
- **Prompt (essence):** implement the cryptographic layer so that any tampering is detected, and prove the hashing reproduces across independent implementations rather than merely agreeing with itself.
- **Output:** the Option-B message surface; cross-implementation hash reproduction tests; the commit-reveal round trip through the SDK; replay and idempotency conflict rejection on intake; tamper detection with technical-loss outcomes; Step-0 host and code attestation binding the exact running Git commit.
- **Refinement:** the neutral stub was written to re-implement canonicalization and hashing from the profile text rather than import ours, so a shared bug could not cancel out.
- **Lesson:** a hash test that calls the same function twice proves nothing. The only useful question is whether a *different* implementation reaches the same bytes.

## P-016 — Re-basing the wire onto the reference simulator
- **Date:** 2026-07-29 · **Tool:** Claude (agentic CLI) · *reconstructed*
- **Goal:** replace the self-authored Option-B wire with the reference simulator's, because league play is against unknown classmates.
- **Prompt (essence):** align the schemas to simulator v3.0.0; reconcile the resulting profile against the book and Appendix F rather than adopting simulator defaults wholesale.
- **Output:** schema alignment, a book/Appendix-F reconciliation pass, `result_claim` narrowed to the simulator's wire set, three bundle revisions to `0.2.5-proposed`, the transport-neutral peer interface (`M5-01`), and the FastMCP mailbox server (`M5-02`) with `ADR-002` amended.
- **Refinement:** the reconciliation was the substantive half. Where the simulator and the book disagreed, the book won and the divergence was recorded — the profile is a compatibility target, not an authority.
- **Lesson:** interoperability forces you to speak someone else's wire, but adopting their wire is not the same as adopting their rules, and conflating the two silently imports their bugs.

## P-017 — An audit pass against the official sources
- **Date:** 2026-07-31 · **Tool:** Claude (agentic CLI) · *reconstructed*
- **Goal:** check the whole repository against `inst/` and the submission guidelines before building further.
- **Prompt (essence):** check the instruction documents and both repositories deeply for anything unaligned or incomplete — the lecturer will not forgive missing points — then fix what is found.
- **Output:** ledger and registers reconciled; two unknowns closed that the book already answered; the commit construction pinned to **real reference-implementation output**; the FastMCP client connector (`M5-03`); the acknowledgement-shape fix; the book's stage-2 localhost milestone closed; negotiation and mismatch refusal (`M5-04`).
- **Refinement:** three of this pass's own findings were false alarms caught before being asserted — a console encoding artefact read as file corruption, a rubric regex that matched the *words* "C4"/"UML" in prose rather than actual diagrams, and a table parse that missed grouped rows and undercounted rule coverage. Each was re-checked with a script instead of an eye.
- **Lesson:** an audit's own findings need auditing. The failure mode is not missing a problem, it is confidently reporting one that is not there — and a scripted re-check is the cheapest defence.

## P-018 — Verifying against the lecturer's notebooks before writing code
- **Date:** 2026-07-31 · **Tool:** Claude (agentic CLI) + NotebookLM
- **Goal:** stop guessing at wire details that only the reference implementation can settle.
- **Prompt (essence):** "always ask the notebookLM then look in the `inst` folder's md files then implement" — made a standing order after an ad-hoc query caught a real defect.
- **Output:** a fixed working order — **notebook → `inst/` → code** — applied to every wire task since. It immediately paid: asking what dict the reference's tools return revealed it may answer `{"status": "ok"}`, while our client demanded its own `{"ok": true}`. Every successful delivery from a simulator-built classmate would have been read as a refusal and the game abandoned on turn one.
- **Refinement:** ask for **verbatim quotes** and require the answer to mark each part quoted or inferred; treat hedged answers ("the design indicates…") as unverified. A follow-up question is mandatory when an answer would change a signed structure — one such follow-up established that `game_id`/`game_uid` are *not* signed terms, avoiding a change that would have broken every cross-peer signature.
- **Lesson:** the expensive bugs here are not logic errors, they are **assumptions about the other side**. No local test can catch them, because both halves of a local test share our assumption.

## P-019 — Proving the client against code that shares nothing with it
- **Date:** 2026-08-01 · **Tool:** Claude (agentic CLI)
- **Goal:** close `M5-03e`, `M5-03f`, and `M5-10b` — the last open P0 items before a game loop.
- **Prompt (essence):** "continue to work according to the unDone TODO file in 2 repos… and according to the 2 links in the notebookLM… and the md files under `inst`".
- **Output:** the neutral stub placed behind a real MCP server so `FastMCPClient` is proven against an implementation sharing no source; the private opponent-URL boundary plus a leak guard that refuses a shared match object carrying an address by member *name* or by *value*; and a negotiate round trip across a real socket between two OS processes, refusing a mismatch **by name**.
- **Refinement:** the in-memory loopback was found to prove less than it appeared — both halves read the same `TOOL_ARGUMENTS` table, so a wrong argument name would have agreed with itself. The neutral-stub server writes its argument names out independently, which is what makes agreement mean anything.
- **Lesson:** a test whose two sides share a constant tests the constant, not the contract. Ask of every conformance test: *what would still pass if the shared assumption were wrong?*

## P-020 — Two notebooks, and a conclusion reversed
- **Date:** 2026-08-01 · **Tool:** Claude (agentic CLI) + NotebookLM (both notebooks)
- **Goal:** settle whether `min_center_intensity` is a required shared term.
- **Prompt (essence):** "check the second notebook. always check in both of them when needed."
- **Output:** the second notebook holds the **book PDF itself** plus the lecturer's four artifact templates. Appendix F table 16 has exactly three rows, all `Fixed`, and **no** minimum-centre row; the lecturer's own `agreed-config` template carries the same three keys. This repository's optional treatment was correct and the controlled bundle needed no change — while the companion peer, which required the key, would have refused the lecturer's own template.
- **Refinement:** the previous day's note had flagged **this** repository as the likely error and asked the coordinator to decide. That was wrong. The claim had been sourced from the `inst/` markdown, which *restates* the book, rather than from the PDF one query away.
- **Lesson:** a restatement of a source is not the source. When a decision turns on an appendix table, read the table. Also: the notebooks divide cleanly — one answers *what the reference does*, the other *what the book requires* — and a question that spans both needs both.

## P-021 — Building the turn loop, and what the reference corrected
- **Date:** 2026-08-01 · **Tool:** Claude (agentic CLI) + NotebookLM (both notebooks)
- **Goal:** `M5-11a` and `M5-11` — the declared phase machine and one turn driven through it.
- **Prompt (essence):** "yes start it, ask both notebooks first, then see `inst` md files then build."
- **Output:** the mandatory transition table transcribed unchanged with every undeclared transition refused by name, and `run_turn` driving one iteration through it. The book gave the four-phase turn, Thief-first ordering, and termination precedence; the reference gave the actual loop order and the fact that **no move is ever sent live**.
- **Refinement:** the assumed order was compute-then-send. The reference **awaits first** — a peer must receive before advancing its own step, which is what makes the alternation strict. Separately, sealing was made once-only: re-sealing after a failed send would give one step two commitment hashes and hand the opponent an audit mismatch, an automatic zero under rule 19.
- **Lesson:** most of the phase machine's value is in what it *refuses*, so most of its tests should be refusals — a machine that accepts everything passes a happy-path test and still deadlocks the first time a peer goes out of order.

---

## P-022 — A whole sub-game, and a rule I broke on the way
- **Date:** 2026-08-01 · **Tool:** Claude Opus 5 (agentic CLI) + NotebookLM
- **Goal:** `M5-10d`/`M5-10e` — play a bounded sub-game over the wire and reveal the audit that settles it.
- **Prompt (essence):** continue with the sub-game driver; then, separately, a challenge asking whether the notebooks had actually been consulted, whether `inst/` had been read, and whether the report, prompt log, and `docs/` files had all been updated.
- **Output:** `orchestration/sub_game.py` plays turns until the game is decided and then reveals every sealed record. Termination is **claimed, answered, and only later proven**: the Cop names a cell, only the Thief knows whether it stood there, and the audit settles truth retroactively. Over the wire the remote process accepts a sound audit and **rejects a tampered one**, which is rule 19 enforced across a real carrier rather than asserted locally.
- **Refinement:** the standing order is *notebook → `inst/` → implement*, and it was **half-kept**. The query to the reference notebook failed on a frozen renderer and was not retried; `inst/` was read (the book's capture conditions and duty of truth) and the controlled schema supplied the field shapes, so the build proceeded on those. When challenged, the query was retried and the reference **confirmed** the design — its precedence reads capture "when a cop's `capture_claim` is confirmed by the thief", survival at the threshold, then timeout, with the audit sent once per sub-game after the loop. The code was right; the process was not.
- **Lesson:** a tool failure is not permission to skip the step. It happened to cost nothing here, which is exactly why it was worth recording — the next skipped check is the one that silently ships a wrong assumption. Retry, or say plainly that the step was skipped.

## P-023 — Deadlines and bounded retry, and a parameter status nobody had noticed
- **Date:** 2026-08-01 · **Tool:** Claude Opus 5 (agentic CLI) + NotebookLM (both notebooks)
- **Goal:** `M5-05a`/`M5-05b` — stop the turn loop being able to wait forever.
- **Prompt (essence):** run the full eight-step workflow for the next feature in both ledgers.
- **Output:** `services/deadlines.py` — an injected-time `Deadline`, a `RetryPolicy` read from the shared signed match object, and an `attempt` helper that bounds every wait. Book §8.4.1's boxed note is the whole design: *"Missing a Deadline is a Failure, Not Patience"*, permitting only retry or a declared technical loss with the queue cleared.
- **Refinement:** the reference gave the exact config keys and defaults — `network_and_league.response_timeout_sec` 30, `rate_limiter_gatekeeper.retry_backoff_sec` 5, `.max_retries` 3, `network_and_league.watchdog_timeout_sec` 60 — and all four proved already present in our controlled match fixture. The book PDF then added something the ledger had not recorded: table 19 marks the watchdog timeout **`Negotiation`**, not `Minimum` like its neighbours. Step 1 also caught two stale ledger rows (`M5-11c` here, `M5-012` in the companion) claiming open work that was already done.
- **Lesson:** injecting the clock is what makes a timeout testable at all — every one of these tests would otherwise have had to sleep, and a suite that sleeps is a suite people stop running. Separately: re-reading the ledger *before* starting is cheap and caught two rows that would have sent someone to re-do finished work.

## P-024 — The Gatekeeper, and a word the ledger should not have claimed
- **Date:** 2026-08-01 - **Tool:** Claude Opus 5 (agentic CLI) + NotebookLM (both notebooks)
- **Goal:** `M5-05c`/`M5-05d` - queue depth and the backpressure signal.
- **Prompt (essence):** run the full eight-step workflow for the next feature in both ledgers.
- **Output:** `services/gatekeeper.py`. The guidelines settled the design in one line - **"Overflow is queued, not rejected"** - which is the opposite of the usual instinct: a busy gate returns `False` and keeps the work, and only a genuinely full queue fails, loudly. `queue_status()` exists because the guidelines require a gatekeeper to expose depth and stats.
- **Refinement:** step 2 changed the plan before any code was written. Idempotency was already implemented - the receive-side intake had been deduplicating and rejecting replays since `M4-04` - so the feature narrowed to backpressure alone. The book then narrowed it further: chapter 9.3.1 aims the Gatekeeper at **outbound** Gmail and LLM calls to avoid a `429`, not at the inbound peer mailbox. Building it as an inbound queue would have been a plausible, useless answer.
- **Lesson:** the ledger's own row said "FIFO queue depth", and the book notebook marked FIFO **inferred, not stated**. The word was removed rather than kept, because a task title that cites book authority for something the book never says is how an invented requirement becomes permanent. Check the wording of the requirement, not just the requirement.

## P-025 — The watchdog, and a Phase-4 source that was not reachable
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** `M5-06` — a liveness watchdog and a clean shutdown, so a peer that goes silent *between* requests cannot hang us the way the per-request deadline (`M5-05`) already prevents within one request.
- **Prompt (essence):** synchronise the repository, verify the reported state rather than trust it, consult both notebooks, then implement the highest-priority unblocked M5 task under TDD and the full quality gates.
- **Output:** `services/watchdog.py` — an injected-time `Watchdog` (heartbeat, sticky trip on the inclusive `watchdog_timeout_sec` boundary, refuses to be fed after tripping). `orchestration/shutdown.py` — `controlled_shutdown` (persist first, then route the declared phase machine to `TECHNICAL_LOSS` using only declared transitions, fail-closed so a failing `persist_state` still ends the game) and `heartbeat_on_transition`, which feeds the watchdog off the loop's existing per-phase `on_transition` stream rather than threading new plumbing through `run_turn`. 16 new tests; both files 100% branch; suite 714 → 730, 98.52% overall.
- **Refinement:** the standing order is *notebook → `inst/` → implement*, and the first step **could not run** — this environment exposes no NotebookLM tool, so neither the reference notebook (`f504d33d…`) nor the book notebook (`ff2216f4…`) was reachable. Per the brief's own rule ("if NotebookLM is unavailable, stop and tell me; do not silently guess"), I stopped and surfaced it. Amr authorised proceeding on the repository's already-pinned book authority: `watchdog_timeout_sec` 60 is `[AF-t19]` recorded in `services/deadlines.py`, the heartbeat/terminal duty is `[AE-6]`/`[AE-7]`, and §8.4.1's boxed note was already transcribed in M5-05. No protocol shape was invented — the schema and phase table were unchanged, and `WATCHDOG_TIMEOUT` already existed as a read-but-unused constant.
- **Lesson:** the previous entry's lesson was "a tool failure is not permission to skip the step." The honest application when the tool is *absent* rather than merely flaky is to name the gap out loud, let the human decide, and record the exact authority the work actually stood on — not to quietly relabel the entry as if the notebooks had been read. The watchdog value was safe to proceed on precisely because a prior notebook pass had already pinned it; a value with no such record would have been a genuine blocker, not a footnote.

## P-026 — Proving the adversarial milestone that was mostly already met
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** `M5-15` — prove a hostile or broken opponent cannot hang or corrupt this peer, across five fault classes.
- **Prompt (essence):** proceed to the recommended next task after the watchdog.
- **Output:** `tests/unit/test_adversarial_peer.py`. The investigation mattered more than the code: reading the suite first showed **every one of the five guards was already built and unit-tested** — silence in `test_turn_loop_faults`/`test_sub_game`, replay and conflict in `test_turn_inbox`, tamper in `test_audit_reveal`, malformed in `test_peer_inbound`, disconnect-mid-audit at `test_sub_game.py:131`. So the honest deliverable was not to re-assert them but to add the two properties nothing yet proved: **cannot corrupt** (a refused conflict/replay/malformed message leaves the accepted, audit-bearing state intact and honest play continues past it) and the **watchdog half of M5-15a** (sustained silence with no transition to feed the heartbeat trips the watchdog into a terminal shutdown — the M5-06 path composed with silence). Six tests; suite 730 → 736.
- **Refinement:** two calls not to over-build. First, "oversized input" (M5-15d): the turn schema is `additionalProperties: true` at the top level, so a large junk-laden message is *tolerated*, not rejected. The instinct to add a size cap was refused — any threshold would be un-sourced and could refuse a legitimate classmate message, and one large message is not a hang. The reality was documented in the ledger instead of papered over with an invented limit. Second, the corruption tests were written to assert through the **public** `InboundPeer` surface (idempotent re-accept proves which commit is on record) rather than reaching into `_inbox`, so the proof binds to the shipped entry point.
- **Lesson:** a "prove the runtime" milestone is not a licence to manufacture near-duplicate tests to claim a tick. Read what already exists first; the value is in the *gap* — here, the two unproven properties and the composition with the new watchdog — not in re-testing five guards that other milestones already covered test-first. And when a requirement word ("oversized") has no mechanism behind it in the contract, prove what is true and record the gap, rather than inventing the mechanism to make the word literally true.

## P-027 — Unblocking a "contract decision" by finding the half that was never blocked
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** `M5-04h`/`U-029` — the book-mandated pre-game identity (members, repo URLs, MCP server URLs, hardware spec, LLM model) and the `config_sha256` lock, long parked as PENDING / "the coordinator's call."
- **Prompt (essence):** "I don't like to skip things because I fear I might forget them. Let's unblock and work in order." — a refusal to jump past the blocked row to a later one.
- **Output:** `protocol/identity.py` (`build_identity` assembles the mandated content from **injected** sources so nothing is hard-coded; `require_complete_identity` refuses to ship an incomplete offer) and a two-line change to `build_offer`: enforce our own identity is complete, and attach `config_sha256` over the whole game object. `verify_offer` untouched. 12 tests; the three stub `IDENTITY` fixtures that had quietly encoded the gap were completed; suite 736 → 749.
- **Refinement:** the row had been filed whole as "a contract revision, the coordinator's call," and that framing was what kept it stuck. Splitting it dissolved most of the block: *populating our own offer* is contract-independent — the schema already defines every identity member and is `additionalProperties: true`, so `config_sha256` is already tolerated and **no `shared_contract/` byte changes** — while only *requiring an opponent to send them* is the interop-affecting schema change, because a simulator-built peer keeps these values in emitted artifacts, not on the wire. Amr chose "populate ours, tolerate theirs," so we ship the full mandated content and still accept a peer that omits it. The genuinely-open half (refuse the opponent) stays recorded at `U-029`/`C-031` for the coordinator, with the `OB-005` version bump it would need.
- **Lesson:** "blocked" is often a property of how coarsely the task was written, not of the work. Before deferring a whole row on an authority you don't have, test whether it decomposes into a compliance half you *can* do under existing authority and a genuinely-contested half you cannot. Here the compliance half was P0, book-mandated, and had been sitting behind a label the whole time. Also: making our own outbound stricter (enforced completeness) while keeping our inbound tolerant is the fail-safe direction — it can only ever refuse *us*, never a classmate.

## P-028 — Reconciling M5-05, and the tunnel boundary that was half-built already
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** continue in order — close the DEFERRED `M5-05`/`M5-05e` rows that the watchdog and adversarial work had actually satisfied, then `M5-07` (the public tunnel boundary).
- **Prompt (essence):** "let's continue working."
- **Output:** `M5-05`/`M5-05e` flipped to DONE with per-fault-class evidence (timeout → deadlines/watchdog, drop → turn-loop/sub-game, duplicate → turn-inbox/adversarial, reorder → turn-inbox/adversarial) — no new code, the guards were built test-first earlier. For `M5-07`: `shared.private_config.public_url` reads our advertised tunnel address from `[network].public_url` (refactored to share a `_read_network_url` helper with `opponent_url`, so the validation lives once), `config/game.toml.example` gained the key, and `tests/unit/test_tunnel_boundary.py` proves provider-neutrality and that a tunnel token beside the URL never reaches the exchanged identity. Suite 749 → 764.
- **Refinement:** two things. First, `M5-07`'s hard part turned out to be already enforced — `assert_no_network_address` and the secret scanner had covered the shared-config-leak half for milestones; the genuine gap was only our *own* advertised URL having a private-config home and a provider-neutrality proof, which connects straight to `M5-04h`'s `mcp_servers`. Second, the secret scanner did its job on me: my first tunnel-token fixture read `"SECRET-provider-token"` and the scanner flagged it as a credential assignment. The fix was to use the scanner's own placeholder convention (a value containing `dummy`), not to weaken the scanner — a check that flags a test fixture is working, and the right response is to write the fixture the way a real placeholder is written.
- **Lesson:** `M5-07c` (a game across two real machines) cannot be unit-tested, so it is recorded as **BLOCKED — needs hardware** with a concrete runbook, not quietly marked DONE or faked with a mock. The localhost two-process test already exercises the same code path; 07c only swaps the carrier. Naming exactly what remains — and that it is Amr's cross-machine run, not more code — is more honest than a green tick that proves nothing about a real tunnel.

## P-029 — The gateway, and the sibling import its own boundary test caught
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** `M5-08` — the Appendix E rule 3 single-gateway coordinator: one owner of the five subsystems, no subsystem referencing another.
- **Output:** `orchestration/ports.py` (four `Protocol` ports + the existing `peer.PeerTransport` re-exported as `MCPConnector`), `orchestration/orchestrator.py` (`Orchestrator` — injects each subsystem as a port, drives a turn through the phase machine, beats the watchdog and logs on every transition, and on shutdown persists through the log manager then routes to `TECHNICAL_LOSS`, wiring the seam M5-06 left injected), and `orchestration/services/limits.py` (new neutral infra). Twelve tests; suite 764 → 773.
- **Refinement:** writing the boundary test (`M5-08b`) is what found the defect it exists to find. The watchdog imported `read_limit` and `WATCHDOG_TIMEOUT` from the deadline tracker — a direct link between two subsystems the coordinator is supposed to keep apart. The fix was not to soften the test with an allowlist but to remove the coupling: the shared "read one signed match limit" helper is genuinely sub-subsystem infrastructure, so it moved to a neutral `services/limits.py` that the deadline tracker, the watchdog, and the gatekeeper all depend on, none depending on a sibling. `read_limit` now raises a neutral `LimitError` rather than a `DeadlineError`, which is the honest type for a config-reading utility that is no longer part of the deadline tracker.
- **Lesson:** a boundary test earns its keep the moment it fails on real code, not on a plant. The instinct when a structural test flags a shared helper is to allowlist the helper; the better move is to ask whether the helper actually belongs to the subsystem it lives in. Here it did not — reading a number from the signed config is nobody's subsystem — so extracting it fixed the design rather than hiding the smell. Also: keep the gateway depending on **ports**, not concrete subsystems (a test asserts `orchestrator.py` imports none of the four modules), so the coupling can never quietly grow back.

## P-030 — The log manager, and a secret the log must refuse to hold
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** `M5-12` — the append-only match log, the concrete subsystem behind the `LogManager` port M5-08 defined.
- **Output:** `services/log_manager.py` — `MatchLog`, append-only (no edit/delete path; `events` returns a tuple copy), per-match `logs/<id>.jsonl` with a validated file stem, and one discipline that is more than storage: `record` **refuses** any detail carrying a nonce until `open_reveal()` marks the post-game reveal. The commit hash is logged live; the nonce that opens it is not, so a log captured mid-match cannot leak the seal `[AE-18]`. Nine tests; suite 773 → 786; the boundary test now covers all five subsystems.
- **Refinement:** two small honesty points. The row said `logs/<match>.json`; the log is one append-only line per event, which a single JSON document cannot be, so it is `.jsonl` and the row now says why — a filename in a plan is a guess until the format is decided. And the nonce guard is a *name*-based refusal (`"nonce" in the member name`), which is deliberately conservative: it would rather refuse a harmless field that happens to be named `nonce` than let the real one through, because the cost of the false negative — an automatic zero for leaking the seal — is not symmetric with the cost of the false positive.
- **Lesson:** a log manager is usually treated as a dumb sink, but here it carries a rule the rest of the system depends on — the audit only works if the nonce stays secret until the reveal, and the safest place to enforce that is the thing doing the writing. Push the invariant down to where the data actually lands, rather than trusting every caller to remember it.

## P-031 — The deadline tracker, and a subsystem that spans two files
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** `M5-13` — the deadline tracker subsystem behind the `DeadlineTracker` port.
- **Output:** `services/deadline_tracker.py` — `DeadlineTracker` wraps the M5-05 `RetryPolicy`/`Deadline` primitive to track the *set* of outbound requests in flight: `open` registers one under its own expiry, `reap` returns and drops the breached ones (past expiry is failure, not patience), and `clear` empties the queue on a technical loss so nothing orphaned is answered after the game is lost. Eight tests; suite 786 → 794.
- **Refinement:** the tracker legitimately imports the deadline *primitive*, which looks like a subsystem-to-subsystem link to the M5-08 boundary test. It is not — the primitive and the tracker are two files of the *same* subsystem, so the boundary map now lists both under `deadline_tracker` and the `services.deadline` prefix names them together, while the tracker using its own primitive is excluded from the forbidden set. The distinction that matters is *cross*-subsystem coupling, not *intra*-subsystem structure, and the test now encodes exactly that.
- **Lesson:** a boundary rule needs a definition of where the boundary is, and "one module per subsystem" is too crude — a subsystem can be a primitive plus the thing that manages it. The refactor from P-029 (extracting `services.limits`) was about removing a *real* cross-link; this is the opposite case, recognising that an import is *within* a subsystem and encoding that so the test stays honest rather than forcing an artificial one-file-per-subsystem split.

## P-032 — Rejection handling, proven not built
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** `M5-14` — an opponent's content rejection is a scored outcome, never an endless retry.
- **Output:** `tests/unit/test_rejection_handling.py` (four tests); no runtime code. Reading first showed the machinery was already there — the disjoint `TransportError`/`PeerRejectionError` types (M5-03c), `attempt`'s `retry_on`, and `turn_loop._deliver` routing a rejection to `TECHNICAL_LOSS`. The one unproven property was the *combination*: retry chases a carrier fault but a decided rejection propagates at once (tried once, never retried), and a rejection in a sub-game becomes a scored `TECHNICAL_LOSS` with the audit still sent. Suite 794 → 798.
- **Refinement:** the same discipline as M5-05e and M5-15 — do not manufacture code to claim a milestone that is really about behaviour already present. The additive value here is pinning that `except TransportError` can never swallow a `PeerRejectionError` (the types are disjoint, re-asserted) and that the retry budget does not rescue a lost game.
- **Lesson:** three of M5's "handle X" rows (05e, 14, 15) turned out to be proof milestones, not build milestones, because the guards were written test-first when each mechanism landed. The honest close is a consolidated proof plus a precise ledger note pointing at the tests — and saying "no new runtime code was needed" out loud, so a reader is not left hunting for an implementation that was never the point.

## P-033 — Documenting the architecture last, when it was finally true
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** `M5-16` — draw the subsystem diagram and document every failure path.
- **Output:** a "Runtime architecture" section in `PRD_p2p_mcp.md`: a mermaid `graph TD` of the gateway and five subsystems (every arrow gateway↔subsystem, `services.limits` shown below the line), and a failure-path table mapping eight fault classes to their guard and defined terminal outcome, each row naming the test that pins it. Also corrected the PRD's stale "still absent" line, which still listed the gateway, log manager, and tunnel as unbuilt — all of them landed this session.
- **Refinement:** M5-16 was left for last on purpose. A subsystem diagram drawn before M5-08 would have been a wish, not a description; drawing it after the gateway, the five ports, and the boundary test exist means the picture and the code agree, and the diagram deliberately mirrors the boundary test (limits below the line) so the two cannot drift. The failure table is a consolidation, not new analysis — every row already had a test from the resilience milestones, and the table just gives a grader one place to see that a hostile peer has nowhere to make this peer hang.
- **Lesson:** documentation of an architecture is only worth writing once the architecture is real; written earlier it becomes a claim someone later has to reconcile. The tell that it was the right time: every cell in the failure table could cite an existing test, and the diagram could be checked against the boundary test rather than against intent.

## P-034 — Deciding the last two M5 items: one dissolved, one honestly blocked
- **Date:** 2026-08-01 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** the two items left blocking M5 — `U-029` (enforce the opponent's mandated fields?) and `M5-07c` (the two-machine tunnel rehearsal) — decided against the book and the docs.
- **Output:** `U-029` resolved as **"tolerate omission, verify presence."** `verify_offer` (moved to `protocol/offer_review.py` to keep `negotiation.py` within length) gained an optional `expected_config_sha256`: an omitted lock still verifies, a present-but-wrong lock is refused as a rule-11 config mismatch. No schema change, so no interop refusal and no version bump. Four tests. `M5-07c` left **BLOCKED**, with the runbook corrected.
- **Refinement:** the U-029 "decision" turned out to need no authority once framed correctly — rule 11 refuses on a *mismatch*, not on missing metadata, so tolerating omission is not a concession, it is what the rule actually says, and the only real enforcement (a present-and-wrong lock) is squarely a mismatch. On `M5-07c` the temptation was to add a `serve` CLI and call it progress, but reading `build_server` showed it is a passive mailbox — a `serve` that accepts and acks without the drain-and-play loop would prove connectivity, not a game, and my own earlier runbook had *already* mis-implied `python -m p2p_cop_agent` could launch a peer. Correcting that lie was worth more than shipping the stub it implied.
- **Lesson:** "make the decision" sometimes means discovering the decision was never contested — a requirement flagged for a coordinator dissolved into a plain reading of rule 11. And a blocked item is better served by naming its two real blockers (hardware, and the over-wire play loop) and fixing the doc that overstated progress than by a stub that turns a P0 into a false green. The autonomous play loop is now the clearly-named M5→M6 bridge, not a vague gap.

## P-035 — Driving the mailbox: the loop that was named everywhere and built nowhere
- **Date:** 2026-08-02 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks used**
- **Goal:** `M5-17` — the autonomous over-wire play loop, the M5→M6 bridge and the code half of `M5-07c`.
- **Prompt (essence):** work the eight-step process; pick up where the handoffs left off.
- **Notebooks (step 3, both, as required):** the *reference* notebook answered how a peer actually runs unattended — `cli.py` exposes `peer --role <thief|police>`; the FastMCP server is a passive mailbox; the driver is `PeerRuntime`, which **polls its own inboxes** at `[network].poll_interval_seconds` (0.5 s); the loop is verbatim `negotiate → turn loop (wait green → think → move → seal → send) → end-of-game audit`; `receive_turn` "does not compute the next turn; it only deposits the message"; the Thief moves first. The *book* notebook answered what is required — section 8.3 mandates a strict **state machine**, not a bare polling loop; rule 6 verbatim "Mandatory to implement a deadline-tracking mechanism to prevent deadlocks while waiting for the opponent"; rule 7 a watchdog for process crashes; the loop must emit a heartbeat and on a missing pulse `persist_state()` then `controlled_shutdown()`.
- **Output:** `orchestration/polling.py` (`poll_for_turn`, `turn_receiver`) and `adapters.take_turn`; 24 tests across `test_polling.py`, `test_turn_receiver.py`, `test_take_turn.py`, `test_autonomous_play.py`. Both new source files at 100% branch. The end-to-end test plays a whole sub-game whose only turn source is the mailbox, with nothing fed in by hand. 825 tests, 98.69% branch, all gates green.
- **Refinement:** the two notebooks appeared to disagree — the reference *polls* while the book mandates a *state machine* — and the resolution is that they answer different questions: polling is only how a queued message is picked up, while `PhaseMachine` still decides what may legally follow. Recording that as a reconciliation rather than a conflict kept a real design constraint (the machine stays authoritative) from being quietly traded away for the reference's convenience. Three `take_turn` behaviours were driven by asking what would silently break an unattended match rather than by what looked tidy: a rejected turn must be *consumed* (or the poller re-rejects it forever and starves the real turn behind it), a second queued turn must be *left* (or a peer sending two at once costs us the next step), and the other mailboxes must be drained (or a control message parked in front of a turn stalls the game). The first test run also caught a genuine error in my own harness: I had the Cop *opening*, when the book gives the first move to the Thief — the failure was in the test, but the assumption behind it would have been a real bug in a `serve` CLI.
- **What was NOT built, and why:** the `serve` CLI (`M5-17e`). `build_server(...).run()` blocks, so it needs a threaded server plus autonomous negotiation sequencing. A **passive** `serve` was rejected on 2026-08-01 as proving connectivity rather than a game; shipping one now would contradict a considered decision for the appearance of progress, so it is left explicitly PENDING with its two remaining parts named.
- **Lesson:** the most load-bearing missing piece can be the one every document *mentions* and no ledger *owns* — the Cop named this loop only inside a blocked row's prose, and the Thief ledger had no row for it at all, so the repo's own biggest gap was invisible to a grep for open tasks. A gap described in prose is not a tracked gap.

## P-036 — Launching a peer: the bind address that only fails on a second machine
- **Date:** 2026-08-02 · **Tool:** Claude Opus 5 (agentic CLI) · **NotebookLM: BOTH notebooks, different questions**
- **Goal:** `M5-17e` — host the mailbox as a long-running process and tolerate either start order.
- **Notebooks (step 3):** each was asked what only it could answer, rather than the same question twice. The **reference** (123 source files) gave the *code*: `start_peer_server` runs `server.run(...)` on a `daemon=True` thread after an `_ensure_port_free` pre-check, the CLI's `_run_peer_inner` does nothing but `SimulationSdk(...).run_peer(role)`, `connect_timeout_seconds` (60) / `retry_interval_seconds` (1.0) drive a connect-retry loop because "start order doesn't matter", and the runtime waits for the counter-signature before step 1. The **book** (PDF + four templates) gave the *authority*: rule 10 verbatim, the pre-game-declaration key set, and that Step-0 must be **exchanged and mutually signed**.
- **Output:** `adapters/serving.py` (`serve_in_background`, `ensure_port_free`, `port_answers`) and `services/readiness.py` (`wait_for_peer`), 18 tests, `ADR-009`. 843 tests, 98.73% branch, all gates green.
- **Refinement:** the notebooks **disagreed**, and the disagreement was the whole value of asking both. The reference binds `127.0.0.1`; the book prints `host="0.0.0.0"` with the comment "so a tunnel can expose it publicly", and rule 10 sanctions failure to tunnel with "Inability to compete against opponents". The reference is not wrong — it runs both peers on one machine — but copying it would produce a peer that passes every local test and is invisible through the tunnel, failing only at the two-machine rehearsal where it reads as a network fault. The book outranks the simulator, so `DEFAULT_BIND_HOST` is `0.0.0.0` and a test pins it, because it is a one-word change nothing local would catch. Readiness was also kept deliberately separate from `deadlines`/`watchdog`: startup is the one phase where an unreachable peer is expected and harmless, and that leniency must not leak into the match, where rule 6 requires the opposite.
- **Problem hit:** the first `ensure_port_free` set `SO_REUSEADDR` on its probe socket out of habit, and the check silently never fired — on Windows that option lets a socket bind a port another process already holds, which is exactly what the function exists to detect. Caught by a test that held a port and asserted the raise. A detection probe wants the strictest bind available, not the most permissive.
- **What was NOT built:** `M5-17f`, the negotiation-to-first-move sequencing. A `serve` that comes up and mailboxes without playing is the passive server rejected on 2026-08-01, so no `serve` command is wired until that row closes.
- **Lesson:** when the reference and the book disagree, the reference is usually solving a smaller problem — here, one machine instead of two. The hierarchy exists for exactly that case, and the tell is that the reference's choice is *convenient* rather than *wrong*.

## P-037 — Agreeing before the first move: sequencing what already existed
- **Date:** 2026-08-02 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** `M5-17f` — the negotiation-to-first-move sequencing `M5-17e` left open, so a peer reaches agreement on its own before playing.
- **Context:** started this having just discovered my own parallel over-wire-loop work (`P-035` on my branch) was a duplicate of Sharbel's already-merged `M5-17`/`M5-17e`; reset my branch to `main` and took `M5-17f` by explicit assignment to avoid a second collision.
- **Output:** `orchestration/negotiation_handshake.py` — `negotiate_match` sends our `build_offer`, waits on the agreements mailbox with the same `poll_for_turn` the turn loop uses, and returns an `Agreement` only once `verify_offer` accepts the opponent's against our terms and `config_sha256` lock. Three distinct outcomes (agreement / rule-11 refusal by name / `None` on a silent opponent) and a separate `HandshakeError` for a carrier fault sending our own offer. 7 tests, module at 100% branch; 850 pass, 98.75%. No `shared_contract/` change.
- **Refinement:** decomposed the parent rather than doing it all. `M5-17f` bundles three things — the agreement gate, the Step-0 attestation *exchange*, and the pre-game declaration *lock*. The gate (`-i`) is contract-independent and reuses verified primitives, so it was built now. The attestation exchange (`-ii`) needs a wire-shape decision (what crosses pre-game, and whether to require the opponent's) that is a `U-029`-style "populate ours, tolerate theirs" call, not a silent one — flagged, not guessed. The declaration (`-iii`) is an `M7-02a`/`M7-22` artifact with no schema yet, so building it here would preempt M7; the row records only the *timing/lock obligation* M5 imposes. The temptation was to wire a `serve` command on top and call the parent done, but that recreates the passive-server-that-cannot-play error rejected twice before.
- **Lesson:** when a milestone row bundles a contract-independent core with interop-uncertain extras, decompose it and ship the core — a decomposed `PENDING` parent with one `DONE` child is more honest, and more useful to the next person, than a single row half-guessed to green. And after a duplication, reusing the *existing* primitives (`build_offer`/`verify_offer`/`poll_for_turn`) rather than inventing new ones is what keeps two people's work composable.

## P-038 — Exchanging the attestation: the secret that wasn't
- **Date:** 2026-08-02 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** `M5-17f-ii` — exchange and mutually verify the Step-0 attestation before the first move, after presenting Amr the wire-shape options.
- **Decision (Amr):** Option A — fold Step-0 into the negotiation offer, verify on receipt, tolerate omission — chosen over a separate `receive_control` message or a commit-now/reveal-at-audit scheme.
- **Output:** `protocol/attestation.py` gained `attestation_wire` and `review_opponent_attestation`; `negotiate_match` gained an optional `step_zero` that rides on our offer and verifies the opponent's into `Agreement.opponent_step_zero`. Enforcement is one-directional (`U-029`): always send ours, never refuse an omission, refuse a present-and-tampered seal as a rule-11 mismatch. 11 tests, both changed modules at 100% branch; 861 pass, 98.77%. No `shared_contract/` change.
- **Refinement:** the framing question — where does Step-0 cross the wire, and do we defer its reveal like a move? — dissolved once I noticed **Step-0 has nothing to hide.** A move commitment is sealed because revealing it early lets the opponent react; hardware, model, and git commit are the opposite, they are *meant* to be public (the declaration lists them openly). So the commit-reveal machinery here is for tamper-binding, not secrecy, and the attestation can be exchanged **revealed** and verified on the spot — which is what makes "mutually signed *before* the first move" clean rather than half-met. That collapsed the three options to one obvious answer and avoided both an audit-schema change and a dependency on the optional `receive_control` tool. Enforcement needed no new thinking: it is the same "populate ours, tolerate theirs" shape as the `config_sha256` lock, so `review_opponent_attestation` mirrors `_verify_config_lock` deliberately.
- **Lesson:** before choosing *how* to transmit a sealed value, ask whether it is actually secret. Reusing a mechanism (commit-reveal) out of habit, where its defining property (secrecy) does not apply, is how a design acquires complexity it never needed — the deferral-to-audit option existed only because I had assumed Step-0 behaved like a move.

## P-039 — Pulling the declaration lock forward without pre-empting M7
- **Date:** 2026-08-03 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** `M5-17f-iii` — the pre-game declaration must be written after negotiation and cryptographically locked before the first move; the last codeable M5 gate before a `serve` command.
- **Decision (Amr):** pull a *minimal* declaration lock forward from M7 to close the preamble, rather than hold at the phase boundary or ship a `serve` with no declaration.
- **Output:** `protocol/declaration.py` — `build_declaration` (assembles the pre-game object from injected sources: both `groups`, four repo `links`, `config_sha256`, counts, `game_started_at`; `game_ended_at` null pre-play) and `lock_declaration` (a plain canonical SHA-256, the config-lock construction). 11 tests, 100% branch; 872 pass, 98.80%. No `shared_contract/` change.
- **Refinement:** the whole risk here was scope-bleed into M7, so the design draws one bright line: M5 owns the *timing-and-lock obligation* (a declaration exists after negotiation and is locked before play), M7 owns the *artifact* (the JSON-Schema envelope, file emission, email reporting). Two concrete choices keep the line clean: `game_id`/`game_uid` are **injected, not derived** — their cross-peer derivation is a contract detail I must not invent, exactly the `U-028`/`U-029` lesson that inventing an interop value silently is the defect the ledger exists to catch — and the lock is a plain canonical hash rather than a new sealed-with-nonce domain, because the declaration is public. So "pull it forward" cost one small module and preempted nothing.
- **Lesson:** "pull a later milestone's work forward" is safe only if you can name the seam precisely — here, obligation (now) vs artifact (M7). When you cannot, the honest move is to inject the uncertain values rather than derive them, so the borrowed work depends on the future contract instead of guessing it.

## P-040 — Composing the preamble, and finding the serve command's one real blocker
- **Date:** 2026-08-03 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** close `M5-17f` by running its three built children as one autonomous sequence, and see how far a `serve` command could then go.
- **Output:** `orchestration/match.py` — `play_match` runs the book's pre-play order (negotiate → verify Step-0 → lock declaration → play) end to end, and stops before the declaration if agreement is never reached, so no lock is written for a game that will not happen. Transport-neutral (injected transport + mailbox sources + clock), 3 tests in-memory, module at 100% branch; `M5-17f` parent now DONE. 875 pass, 98.82%.
- **Refinement:** the plan was to close `M5-17f` *and* wire the `serve` CLI, but building `play_match` surfaced that the CLI has exactly one unsettled input: **where the team identity lives in config.** `play_match` needs an `identity` (group_id, members, repo links, MCP URLs, hardware spec, LLM model) to build our offer and the declaration, and no config file defines that block — the private TOML holds only network addresses, the shared JSON forbids identity-shaped data, and `TEAM_INFO.md` is prose. So `play_match` takes `identity` **injected**, and the CLI that would populate it from a real config source is held, not guessed. Inventing a `[team]` TOML shape silently is precisely the `U-028`/`U-029` defect the ledger exists to catch. Recorded as the single remaining `M5-07c` code blocker rather than papered over.
- **Lesson:** composing finished pieces is where the *next* missing input reveals itself — here, the identity config source that none of the three sub-tasks needed on its own but the whole sequence does. Building the composition before the launcher found that blocker cheaply, in a testable module, instead of half-way through wiring a socket.

## P-041 — Where the team identity lives, settled from the book
- **Date:** 2026-08-03 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session (Amr supplied Appendix B citations)**
- **Goal:** resolve the one blocker `P-040` surfaced — the team-identity config source — and build the loader that `play_match`/the `serve` command need.
- **Decision (Amr, with book Appendix B.4):** identity lives in the private `game.toml` — `[game]` (group_id/group_name/members/repos), `[llm].model` — the MCP URL derives from `[network].public_url`, and the hardware spec is auto-detected where reliable and declared where not.
- **Output:** `shared/team_config.py` — `load_identity` assembles the mandated identity via `build_identity`; `load_host_spec` auto-detects `os`/`cpu` (`platform`) and reads `ram_gb`/`gpu`/`vram_gb` from an operator-declared `[hardware]` section. `config/game.toml.example` gained `[hardware]`. 11 tests, module at 100% branch; 886 pass, 98.84%.
- **Refinement:** two judgement calls. First, the example `game.toml` already carried `[game]`/`[llm]`/`[network]` from the 2026-08-01 audit, so the decision mostly *confirmed* an existing shape rather than inventing one — I verified that before writing a line. Second, hardware: the honest reading of "auto-detect" is partial. `os`/`cpu` come free from `platform`, but `ram_gb`/`gpu`/`vram_gb` cannot be gathered truthfully and portably from the stdlib (VRAM especially, and `HostSpec` requires it positive), and the book makes forging hardware forfeit the computational bonus — so fabricating a value is strictly worse than an honest operator declaration. Hence os/cpu auto, ram/gpu/vram declared. A circular import bit on the way (`shared/__init__` re-exporting `team_config`, which imports `protocol`, which imports `shared.config`); fixed by importing `team_config` directly rather than through the package __init__, with a note left so no one re-adds the export.
- **Lesson:** "auto-detect it" is often only half-true — detect what the platform gives reliably, and require a declaration for what it does not, especially when a wrong value is penalised. And when resolving a "where does X live in config" question, check whether a prior audit already answered it before designing a new shape.

## P-042 — The serve command: assembling everything over a real socket
- **Date:** 2026-08-03 · **Tool:** Claude Opus 4.8 (agentic CLI) · **NotebookLM: unavailable this session**
- **Goal:** build the `serve` command — the last M5 code item — now that the identity source (`P-041`) is settled, so `M5-07c` is blocked only on hardware and M8 evidence.
- **Output:** `adapters/serve.py` `serve_match` assembles the peer from private config, hosts the mailbox on `0.0.0.0` (`serve_in_background`), waits for the opponent (`wait_for_peer`), seals Step-0, and plays via `play_match`; `cli.py` gained a `serve` subcommand (lazy-importing the launcher so `--version` stays transport-free). Pure helpers — URL host/port split, per-game token split, deterministic game id, the placeholder decision — are unit-tested; the network body is runbook-only. 8 new tests; 894 pass, 97.68%.
- **Refinement:** kept the coverage honest by *separating the testable from the untestable* rather than mocking a socket. `serve_match`'s body (bind, wait, dial) drops to ~68% because it genuinely cannot run in CI without a second machine — the same boundary `run_peer` and `serve_in_background` already sit on — so I extracted every decision-free helper into pure functions and tested those, leaving only the irreducible network assembly uncovered. `game_id` is derived from the shared `config_sha256` so both peers compute the *same* id without a coordinator round trip; `game_uid` likewise. The decision stays the documented M5 placeholder (legal `STAY`), because belief pursuit is M6 and wiring a real policy here would be starting M6 while M5 is open.
- **Lesson:** when a module is part pure logic and part irreducible I/O, split them so the coverage number reflects what is actually testable — a 68% file whose gap is exactly the socket calls is honest, whereas mocking the socket to hit 100% would be theatre that tests the mock. Name the untested region in the docstring and the ledger so the gap is a documented boundary, not a silent hole.

## Best practices derived so far
1. **Binding values live in one table** — quote Appendix F, never paraphrase numbers.
2. **Decide, then generate** — architecture-defining choices go to the human first.
3. **Mechanical verifiability** — sequential IDs, one item per line, grep-checkable counts and section lists.
4. **Reference ≠ spec** — log every reference-code deviation and let the book win (ADRs).
5. **Audit passes are prompts too** — schedule an explicit "find what's missing" pass after any large generation; it found 4 real gaps here.
> Canonical prompt-engineering log path confirmed by Professional Software Submission Guidelines v3.0, page 19.
