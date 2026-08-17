# counted-1 vs `yanell11` — what it took to get there

Filed 2026-08-17 17:11 UTC. `sharNamr-vs-yanell11-counted-1`,
uid `c7794f4c-325a-d005-74d0-7964090c098a`, **77–77**, both reports reconciled.

This is the record of the eight series that preceded it, because almost none of the work was
about playing better. It was about discovering that our artifacts said things we had not
checked.

---

## The result

| sub-game | our role | outcome | steps | us | them |
| ---: | --- | --- | ---: | ---: | ---: |
| 1, 3, 5 | police | capture | 25 | 20 | 5 |
| 2, 4, 6 | thief | capture (conceded) | 28 | 5 | 20 |
| | | **total** | | **77** | **77** |

75 base plus the Table 17 row 5 draw score of 2 each. Filed to
`rmisegal+uoh26finalgame@gmail.com`, verified in the sent folder rather than trusted from the
driver's own output.

**Both teams' reports agree on every adjudicating field**, including the consensus digest
`f35c365326fa53e15ba2dffdb7a39e39c0739d233aefc8328efef80cd9819442`, computed independently on
each side from its own six rows. Also agreeing: all six `steps` values, and both teams'
commits in both files, each read out of the other's Step-0 attestation rather than transcribed.

---

## How we got here

Nine series against one opponent. Each one found something, and the pattern is worth stating
plainly: **every fix reported as complete before it had been checked against a real artifact
turned out to have a layer underneath it.**

| series | what it found |
| --- | --- |
| run 4 | 77–77. Their Thief was nearly stationary — 11 STAYs in 15 turns — so our three "wins" flattered us |
| run 5 | Their Thief now moved (4 → 24 real moves) and survived 35. Sub-game 2 died: a **stale hardcoded `--peer`** in the driver beat the validated config |
| run 6 | Negotiated, exchanged no turn, and the crash **destroyed the reason** — `write_match_log` raised a generic error over an empty log |
| run 7 | 6–0. Won by barrier herding: 10 of 14 placed, squeezing their Thief into `[1,0]` |
| run 8 | 77–77. Their Cop had copied it — a **column-3 partition** then a corner seal. Our new Thief policy lost to it |
| friendly-9 | Proved the **labelled uid** on real artifacts. Found the `audit` block was a hardcoded lie |
| friendly-10 | The identity gate caught the **config and declaration writers still unlabelled** — the same defect one layer above the log writer we had just "fixed" |
| friendly-11 | We launched on a stale label and **forked the consensus digest**, the exact failure we had described to them two messages earlier |
| friendly-12 | Everything reconciled. All six step rows agreed for the first time |

---

## Defects fixed, and why each mattered

### Claims the artifacts made without checking

**`audit: {log_verified: true, tampered: false}` was two hardcoded literals.** Every report
ever sent asserted a verification that had never run — while the log artifact beside it
honestly wrote `"audit": {}` with a comment saying an empty object is honest before the check
runs. One file was scrupulous and the next overwrote it. `reporting/log_audit` now recomputes
`move_commit(payload, nonce)` for every sealed record; an edited payload provably fails, and an
empty record set reports *not verified* rather than a vacuous true.

**The preflight's reporting line read the wrong setting.** It inspected
`[reporting].credential_path`, an unused placeholder, while the send reads
`[email].token_path`. So it printed `reporting DISABLED (no credential…)` through five
successful filings. A check that reads a different setting than the code it checks is not a
check. Its verdict was also inverted for a counted game: an absent credential was
*information*, when rule 32 says absence of reporting disqualifies the points. Now
`[league].counted` decides which way it points, and a counted series on a machine that cannot
file refuses at kickoff — adopted from `yanell11`, whose driver already did this.

**`first_meeting_between_groups` and `games_played_including_this` were template defaults**
that had never been set, so every report claimed a first meeting on our fifth series. We also
filed *their* `games_played`, which rule 38 makes a declaration only they are entitled to make.

### One series, three identities

friendly-10 wrote three different `game_uid` values for one series:

    Cop log     41cd0d7dc0f6bbcc0f305f051b9fbbfa       config_sha256[:32] — not a UUID
    Thief log   9b80122e-75f9-c32d-5bff-abc032ae086b   the unlabelled derivation
    result      248354ae-94b5-0617-238d-cebcf015d984   the agreed value

The result was right because the report layer recomputes it, so every check that read a summary
passed. `config_sha256[:32]` is the sharper mistake: **a value only one side can compute is not
an identity, it is a local nickname.**

The unlabelled derivation consumes only the terms and the group pair, so it *cannot*
distinguish two series between the same peers — runs 4, 7 and 8 all carried `9b80122e-…`, and
runs 4 and 8 also shared a consensus digest. `yanell11` proposed a labelled branch; both teams
reproduced each other's uids from the written formula alone, four times
(`friendly-9`, `-10`, `-12`, `counted-1`).

`scripts/check_artifact_identity.py` enforces it now, and it fails widely against our own
history — including **G008 and G009, both already filed with the lecturer**, where the result
names the series `G00N` while every log, config and declaration names it `game-772de8f029e4`,
so `log_files` points at filenames that do not exist. That remains open.

### `steps` was never defined

Our reports said 29 where theirs said 28, on the same sub-games, for four series. Neither was
wrong: each side reported its own move counter, and the book only qualifies a turn as *full*
when it means both sides, so an unqualified step is one agent's move. The fix was not to pick a
number but to name whose:

    steps = the turn on which the terminal condition occurred, in the numbering of the side
            that CAUSED it — the Cop's turn for a capture, the Thief's for a survival.
            Operationally, the `step` field of the sealed record where it first appears.

Both halves needed implementing on each side. We had applied it where we *cause* a capture and
not where we *concede* one; they had the mirror. Five of our tests asserted the old behaviour,
and one had documented the cause in its own docstring — *"the opponent's messages land one turn
later than their own numbering suggests"* — filed as a transport quirk rather than recognised as
an undefined field.

### One team, two behaviours

Twice the two repositories disagreed with each other:

- The Thief declared the **pre-clamp scent formula** while `settle()` had been clamping for
  days — a locked description of a model it does not run — and the two repos locked different
  digests as one team.
- The Cop sealed its commit as `code.git_commit`, the Thief as top-level `github_commit`. Their
  reader looks for the top-level key, so it read our Thief in every sub-game and our Cop in
  none. The gap looked symmetric from both sides and was ours alone.

### Failures that hid themselves

- `run_series.py` ignored the report's return code and printed `stdout or stderr` — and stdout
  is always non-empty, so a failed send showed four success-looking lines and exited 0.
- The empty-log crash replaced `result_reason` with a traceback, which is why two failures had
  to be diagnosed from the opponent's logs instead of ours.
- The Thief's Step-0 reader was threaded `audits_verified` (pass/fail verdicts) instead of
  `opponent_audits` (the disclosed payloads), so it searched a list with no records in it and
  correctly found nothing.

---

## Strategy

**Cop:** promoted the alpha-beta `engine` after measuring it through the live decision path
against the opponent's own recorded emissions — 4/5 captures against the incumbent's 3/5,
strictly dominating. Run 5 had been a survival with *perfect information*: the belief named
their exact cell on 34/34 turns. The failure was pursuit, not perception — a stern chase into
the cell they had just vacated, and 8 barriers ringing the board centre while the Thief ran the
perimeter.

**Thief:** `open_field_v3` defends reachable space (flood-filled Voronoi region, barriers as
walls) rather than distance, because a barrier does not change how far the pursuer is — it
changes how much board is left. It survives both of our own Cops where the incumbent loses to
each. It still **loses to their column-3 partition at step 28**, which remains the honest
strategic gap: it cannot see a pocket with a narrow mouth.

Three harness bugs produced confident wrong answers before any of this was trustworthy: the
Thief moving first (every arm looked invincible), a pursuer tie-break that pinned the Cop to
row 0, and disclosing `barriers[-1]` from a *sorted* list so the Thief walked onto barriers it
had never been told about — then being blamed for it.

---

## Open

1. **G006–G009 evidence pointers.** Four filed reports naming log files that do not exist. The
   evidence exists and hashes; the pointers are wrong. `yanell11`'s framing: a corrected
   re-filing reads as an audit trail working.
2. **`games_played_including_this` disagrees on counted-1** — we filed 0, they filed 1. On the
   field's own wording (*including this*) theirs appears right, and rule 38 judges the figure on
   whether the two reports agree.
3. **The lecturer's address is still armed.** Rule 32 auto-sends at the end of any completed
   series, so nothing may be run until it is disarmed.
4. **The Thief loses to a partitioning Cop.** Needs bottleneck-width scoring, tested against a
   partitioner rather than against our own Cop.
5. **`check_artifact_identity.py` walks `games/*`**, so its behaviour depends on what is on
   disk — the same laptop-dependence `yanell11` found and fixed in their own version.

---

## What the opponent contributed

Recorded because it changed the outcome. `yanell11` diagnosed our Cop's attestation key without
seeing our code; caught `first_meeting` and were right; supplied the labelled-uid scheme and
the identity law that then found three defects of ours; established the step definition from the
book's *full turn* phrasing; and refused a compare-before-send protocol we proposed, on the
correct grounds that rule 9.3 forbids it by name — a claim we had made about our own code
without checking, and which was false.
