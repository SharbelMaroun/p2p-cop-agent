# Session handoff — 2026-08-01

Branch **`Amr`** (= `origin/Amr`), tip **`e45ef07`**, all pushed. Every commit below
passed the full gates: **801 tests**, ~99% branch coverage, ruff clean, file-length
clean, secret-scan clean.

## What was done this session

Worked strictly in milestone order, closing the M5 runtime. One commit per milestone:

| Commit | Milestone | Note |
|---|---|---|
| `2778dab` | **M5-06** watchdog + controlled shutdown | liveness timer distinct from the per-request deadline; `persist_state → controlled_shutdown → TECHNICAL_LOSS` |
| `fddd8a3` | **M5-15** adversarial-peer proof | "cannot corrupt" + "cannot hang" through the real `InboundPeer` |
| `c3b2ca2` | **M5-04h** mandated pre-game identity + `config_sha256` (our side) | populate ours; `protocol/identity.py` |
| `8b5903a` | **M5-05/05e** reconciled + **M5-07a/b** tunnel boundary | `public_url` reader; provider-neutral |
| `6fea223` | **M5-08** orchestrator single-gateway + subsystem decoupling | 5 ports; extracted `services/limits.py` |
| `b9f7b4f` | **M5-12** append-only log manager | nonce refused until reveal `[AE-18]` |
| `f3adc2e` | **M5-13** deadline-tracker subsystem | reap on breach; clear on technical loss |
| `4b9ef2b` | **M5-14** opponent-rejection handling | retry the carrier, never a rejection |
| `f89465a` | **M5-16** subsystem diagram + failure-path table | in `PRD_p2p_mcp.md` |
| `e45ef07` | **U-029** resolved + **M5-07c** decided | see below |

The five subsystems now sit behind one Orchestrator gateway (`orchestration/`), with an
import-boundary test forbidding subsystem-to-subsystem links, and every adversarial
fault class has a documented, tested terminal outcome (`PRD_p2p_mcp.md` failure table).

## The two decisions I was asked to make

- **U-029 (enforce the opponent's mandated fields?) → RESOLVED: tolerate omission,
  verify presence.** Rule 11 refuses on a term *mismatch*, not on missing metadata, so
  refusing a peer for omitting the fields is not book-required and would forfeit a match
  against a simulator-built classmate (which keeps `config_sha256` in artifacts, not on
  the wire). Fields stay optional; `verify_offer` now refuses only a *present-and-wrong*
  lock. No schema change, no version bump. (`protocol/offer_review.py`.)
- **M5-07c (two-machine tunnel game) → honestly BLOCKED, not faked.** Two real blockers:
  (1) hardware — two machines + a live tunnel; (2) the **autonomous over-wire play loop** —
  `adapters.build_server` is a passive mailbox, so a full game still needs the drain wired
  to the orchestrator driving turns against a live peer. A passive `serve` would prove
  connectivity, not a game. Corrected the runbook, which had wrongly implied
  `python -m p2p_cop_agent` can launch a peer (it is still the scaffold).

## Where we are

M5 is functionally complete. **Open items, none of which I can close here:**

1. **M5-07c** — needs the autonomous over-wire play loop (code, the M5→M6 bridge) **and**
   Amr's two-machine tunnel run. This is the same "no real autonomous second peer" gap the
   original handoff flagged; it is now precisely scoped in `docs/TODO.md`.
2. **M5-04h enforcement** — closed as U-029; no further action unless a coordinator/lecturer
   later *requires* the fields on the wire (then: schema `required` + `OB-005` bump).

## Suggested next step

Build the **autonomous over-wire play loop** (drain the mailbox → feed the orchestrator's
`run_turn` → send via the connector → poll for the opponent's turns), plus a thin `serve`
CLI so a peer is launchable. That turns the localhost sub-game proof into a real match
against a second process, and leaves only the physical tunnel for M5-07c. Only after that
does M6 (belief/scent strategy) open, per the project rule against starting M6 while
required M5 runtime work remains.

Authoritative status is always `docs/TODO.md`; conflicts in `SPECIFICATION_CONFLICTS.md`
(see `C-031`); unknowns in `UNKNOWN_REQUIREMENTS.md` (`U-029` closed); rationale in
`PROMPT_LOG.md` (`P-025`…`P-034`).
