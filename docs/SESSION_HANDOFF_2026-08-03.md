# Session handoff — 2026-08-03

Branch **`Amr`**, tip **`b189024`**, pushed to `origin/Amr` (fast-forward, no PR/merge —
that stays the coordinator's call). Every commit passed the full gates: **894 tests**,
~98% branch coverage, ruff clean, file-length clean, secret-scan clean, shared-contract
manifest unchanged (`0.2.5-proposed`).

## How this session started (important context)

It opened by discovering that a prior local commit on `Amr` (an over-wire play loop)
**duplicated Sharbel's already-merged `M5-17`/`M5-17e`** on `main`, and his was the
better implementation (it binds `0.0.0.0`; mine bound `127.0.0.1`, invisible through a
tunnel). We reset `Amr` to `origin/main` to discard the duplicate, then took **`M5-17f`
by explicit assignment** to avoid a second collision. Lesson for next time: **sync with
Sharbel before starting any shared-milestone row.**

## What was done this session

Closed the entire M5 pre-play protocol and the launcher. One commit per sub-task:

| Commit | Item | Note |
|---|---|---|
| `c72755e` | **M5-17f-i** agreement gate | `negotiate_match`: play starts only after both verify |
| `cc466ab` | **M5-17f-ii** Step-0 attestation exchange | folded into the offer, verified on receipt |
| `305bc9d` | **M5-17f-iii** declaration + lock | minimal pre-game declaration, canonical-SHA-256 lock |
| `5005415` | **M5-17f composition** | `play_match` sequences negotiate→verify→lock→play; **parent DONE** |
| `3c388b3` | **team identity loader** | `shared/team_config.py`; identity from private `game.toml` |
| `b189024` | **`serve` command** | `adapters/serve.py` + `p2p-cop serve …`; M5-07c code closed |

## Decisions taken this session (all Amr-confirmed)

- **Attestation wire shape → Option A**: fold Step-0 into the negotiation offer and
  verify on receipt, tolerate omission (`U-029`). Key realisation: Step-0 is not secret,
  so it is exchanged *revealed* and verified before the first move — no audit deferral,
  no schema change. (`P-038`)
- **Declaration lock pulled forward** from M7 as a *minimal* form: M5 owns the
  timing-and-lock obligation; M7 owns the artifact (schema envelope, emission, email).
  `game_id`/`game_uid` are injected, not derived, so M7's contract is not pre-empted.
  (`P-039`, `P-040`)
- **Team-identity config source settled** (book Appendix B.4): identity lives in the
  private `game.toml` `[game]` + `[llm].model`; MCP URL from `[network].public_url`;
  hardware spec os/cpu auto-detected, ram/gpu/vram operator-declared in `[hardware]`
  (the book requires signing *true* specs). (`P-041`)

Rationale for every step is in `PROMPT_LOG.md` (`P-037`…`P-042`).

## Where we are

**M5 is code-complete.** `p2p-cop serve --root . --match <shared.json> --rate-limits
config/rate_limits.json --private config/game.toml` assembles the peer from config,
hosts the mailbox on `0.0.0.0`, waits for the opponent, seals Step-0, negotiates,
verifies attestation, locks the declaration, and plays a whole match autonomously.

**`M5-07c` remaining blockers are not code:**
1. **Hardware** — two machines + a live tunnel (Amr's run; runbook is in the `M5-07c`
   ledger row).
2. **M8 evidence** — the milestone's mandated proof is GUI/replay screenshots, both M8
   deliverables, so `M5-07c` cannot be *evidenced* until M8 exists.

The `serve_match` network body (bind/wait/dial) is intentionally **runbook-only** and
uncovered in CI (no second machine); its pure helpers are unit-tested.

## Suggested next step

- **M6 (scent/belief strategy)** is now unblocked — the phase rule is satisfied. The
  one seam to replace is `serve_decide` / the `decide` callable (currently the M5
  placeholder: a legal `STAY`). Belief-driven pursuit (`M6-01`…`M6-03`) plugs in there.
- **Amr:** the physical two-machine tunnel run whenever hardware is available.
- **Before starting M6 or M7:** coordinate with Sharbel — this branch now carries a lot
  of shared-milestone work.

Authoritative status is always `docs/TODO.md`; unknowns in `UNKNOWN_REQUIREMENTS.md`;
rationale in `PROMPT_LOG.md`.
