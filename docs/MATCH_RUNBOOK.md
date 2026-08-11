# Match runbook — playing a real opponent

The one page to follow when sitting down with a classmate. Every step here was
exercised end to end on 2026-08-08: two OS processes negotiated, played 35
commit-reveal turns, agreed on the outcome, and the Thief-side log replayed
`Verified OK`.

## Before the match (both teams together)

1. **Agree the shared match file.** One `game.json`, **byte-identical** on both
   machines (Appendix F obligation 1). Copy one file — do not retype it. Verify:

   ```powershell
   Get-FileHash game.json -Algorithm SHA256   # same hash on both machines, or stop
   ```

   It must carry the league values — `num_games: 6`, `max_moves: 35`,
   `max_barriers: 14`, the agreed starts — and `agreed_between` must name **both
   group ids exactly** as each team's private config spells them (a mismatch refuses
   the match before move one; found in rehearsal).

2. **Each team fills its private `game.toml`** (never shared, never committed):
   `[game]` identity/members/repos; `[network]` `my_port`, `opponent_url` (their
   tunnel), `public_url` (ours — advertised in the offer's `mcp_servers`); `[llm]`
   model; `[hardware]` **true** specs — Step-0 seals them and forging forfeits the
   fairness bonus (rule 24).

3. **Open the tunnels** (rule 10 — mandatory; localhost is not league evidence,
   p. 97/215) and exchange public URLs.

4. **Game history declaration** (rules 37–38): this side's pre-game declaration
   carries the counted-games count derived from `results/` — confirm it is current,
   because a false declaration is absolute disqualification.

## Running one sub-game (Cop side — this repository)

```powershell
uv run p2p-cop serve --root . --match game.json --rate-limits config\rate_limits.json `
    --private config\game.toml --artifacts games\artifacts --sub-game 1
```

The Cop waits for the Thief's opening; negotiation happens automatically (signed flat
terms, identity, Step-0 attestation on the offer; any mismatch refuses by name). With
`--artifacts` the run writes the pre-game declaration, the per-sub-game config, and
the **revealed** game log (`log_<game_id>_g0N.json`) — the reveal is legitimate then
because the game has ended (rule 18's boundary).

Healthy end: `match outcome: CAPTURE after N step(s)` (or SURVIVAL at 35) — and the
number must match the opponent's, because conflicting reports score 0/0 (`[AE-35]`).

## The six-sub-game series

Lecturer's ruling: sub-games **1, 3, 5** natural roles, **2, 4, 6** swapped. One
`serve` run per sub-game of the right repository on each side, `--sub-game` set to
its number. Fresh process per sub-game — rule 2 forbids carrying state across.

| Sub-game | Our peer  | Their peer |
|---------:|-----------|------------|
| 1, 3, 5  | this Cop  | their Thief|
| 2, 4, 6  | our Thief | their Cop  |

## After the match (both teams)

1. **Replay-verify the logs in front of each other** (the companion Thief's
   `p2p-thief replay --log …` must print `Verified OK`).
2. **Reconcile outcomes** — same result and winner on both sides, or the game
   reconciles to 0/0 (`M9-021a`).
3. **Send the rule-51 JSON report** to the lecturer's address (an unreported game is
   not credited); see `docs/RUNBOOK_reporting_setup.md` for the exact addresses.
4. **Commit the artifacts** under the agreed names (Appendix F obligation 4) and take
   the mandatory screenshots: Live GUI belief map + Replay `Verified OK` (p. 81/189).

## Run preflight on their file the moment it arrives

```powershell
uv run p2p-cop preflight --match <their-game.json> --private config\game.toml
```

Do this **before** agreeing a time, not on match day. It now checks the two things that
refuse a match at the handshake, and both were live defects in the first file group
`uoh-ay26` sent us on 2026-08-11:

- `participants` — `agreed_between` must name our `group_id`. Theirs said
  `["cop", "thief"]`: the two *roles*. Appendix B prints the two **group ids**
  (`inst/police_thief_p2p_Summary.md:2928`).
- `schema version` — must be `1.2`. Theirs said `"1.00"`, the guidelines' config
  revision, which is a **different key** (the optional `version`). The reference
  simulator ships `"1.3"`, so agree the value in writing; see `C-035`.

Until that day preflight printed **`ready`** for that file — the terms projection reads
neither field — and the refusal only landed mid-handshake with the opponent waiting.

## Troubleshooting (each cost us one rehearsal run)

- `offering group '<id>' is not in agreed_between` — the shared file must name that
  exact `group_id`.
- `502` from the opponent's URL — Cloudflare (or ngrok) is up but **their** tunnel is
  not running; that is a peer-not-started, not a network fault.
- `Unexpected UTF-8 BOM` — the shared file was saved with a BOM (PowerShell
  `Out-File` does this); re-save plain UTF-8.
- Technical loss at step 1 on both sides — a peer is not reachable at the dialled
  URL; re-check tunnels and `opponent_url`.
- `agreed terms differ on: <term>` — the two machines hold different shared files;
  re-copy, re-hash.
