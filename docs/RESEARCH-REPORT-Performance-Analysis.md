# Research report — parameter sensitivity and performance analysis

The book names this file directly (p.142/265) and sets its standard in one line: the
research must be **"based on numbers and not on guesses"** (p.142/266). Guidelines §9.1
asks for "systematic experiments with controlled changes to parameters", §9.3 for bar,
line, heatmap and box-plot visualisations, and `M9-06c` for "experiment tables with **run
counts**, not anecdotes".

Every number below was produced by `orchestration.harness.run_sub_game` refereeing real
matches. Nothing here is illustrative. To reproduce the whole report:

```text
uv run python scripts/run_experiments.py     # writes results/*.json
uv run python scripts/render_charts.py       # writes assets/chart-*.svg
```

## Protocol

| Aspect | Value |
|---|---|
| Board | the negotiated fixture, `shared_contract/fixtures/match_config.example.json` |
| Runs per measurement | **40 seeds** (`SEEDS = range(40)`) |
| Design | **paired** — seed *i* gives every arm and every configuration the identical Thief trajectory |
| Opponent | a seeded random legal walk that emits scent but does not react to the Cop |
| Cop's information | the 5×5 scent window only; never the referee's Thief position |
| Arms | `blind` (random legal move), `belief` (what we ship), `oracle` (perfect information) |

The oracle is **not a legal agent**. It is the ceiling, included so a reader can see how
much of the *available* gap belief closes rather than only that it beat random.

## 1. Strategy comparison (`M9-07a`)

![Capture rate and mean score by strategy arm](../assets/chart-strategy-comparison.svg)

| Arm | Capture rate | Mean turns | Mean Cop score | sd |
|---|---|---|---|---|
| blind | 0.525 | 27.20 | 12.88 | 7.59 |
| **belief** | **1.000** | **9.68** | **20.00** | **0.00** |
| oracle | 1.000 | 8.62 | 20.00 | 0.00 |

Belief-driven pursuit closes **100%** of the blind-to-oracle score gap: on this opponent it
captures in **40 of 40** seeds, which is the oracle's own result. Paired seed by seed it wins
**19 of 40** against blind and **loses 0**; the other 21 are ties — the seeds where a random
walk happened to blunder into the Cop anyway. Against the oracle the score is tied **40 of
40**: belief is not *near* perfect play here, it is worth exactly as much, and the only thing
perfect information still buys is speed (8.62 turns against 9.68).

![Cop score distribution by arm](../assets/chart-strategy-distribution.svg)

**The distribution is where a mean alone would mislead, and the reason is structural.** A Cop
score is 20 for a capture and 5 for a survival — there is no value in between, so an arm's
mean is a *mixture ratio*, never a typical game. Blind shows it plainly: Q1 = 5.0, median
20.0, Q3 = 20.0, sd 7.59. Its 12.88 mean describes no game blind ever played. Belief's sd of
**0.00** is the other end of the same fact — every one of its forty games ended 20.

![Turns to resolution by arm](../assets/chart-turns-distribution.svg)

The turn count separates the arms more honestly than the score does, because it is
continuous: blind's median is **35.0** — the survival horizon, i.e. no capture — with Q1
19.8; belief's median is **8.5** and its worst seed still closes by turn 26.

## 1b. The opponent grid (`M9-30`) — every number above has an asterisk

**The opponent model was the untested half of section 1.** Every figure there is earned
against a seeded random walk — the weakest plausible Thief. Re-measured 2026-08-08 against
two deterministic fleeing archetypes (`scripts/experiment_opponents.py`,
`results/opponent_grid.json`; same 40 paired seeds):

| Cop arm | random walk | flee-greedy (reference shape) | flee-smart (distance+mobility) |
|---|---:|---:|---:|
| belief (pursuit only) | 40/40 | **0/40** | 0/40 |
| anticipating (pursuit only) | 40/40 | **0/40** | 0/40 |
| barrier stack (served until 2026-08-08) | 39/40 | **40/40** | 0/40 |
| oracle (pursuit only, sees truth) | 40/40 | **0/40** | 0/40 |
| oracle + barrier stack | 40/40 | **40/40** | 0/40 |

Three findings, each carrying a design decision:

1. **Pursuit alone never captures a competent evader — the oracle included.** An
   equal-speed evader on an open board holds distance forever; §1's 100% headline is
   a property of the random walk, not of the pursuit. Barriers are the entire capture
   mechanism against real opposition, which is why the served policy is now the full
   trap → squeeze → containment-ratchet → interception-chase stack (`M6-21..26`), not
   `pursue_belief`.
2. **The stack converts the likeliest league opponent completely.** `flee_greedy` is the
   reference simulator's own `ThiefBrain` shape — maximise distance from the Cop — and the
   probable classmate default. 0/40 → **40/40**, at the cost of one game against the walk
   (39/40): the containment ratchet's wall turns stall pursuit exactly once in forty walks.
3. **`flee_smart` was an open boundary when this section was written, and it is now
   closed — see §1c.** Distance *plus mobility* escaped every arm in the table above,
   including the barrier stack aimed with referee truth, and the probe read the terminal
   shape as a locked orbit the quota could not cut. That diagnosis was wrong in an
   instructive way: the orbit was produced by the **chase**, not by the walls, and §1c
   is the re-measurement that converts it. This table is kept as the state that motivated
   the fix rather than deleted, because the wrong diagnosis is the finding.
   *(Cross-reference, 2026-08-08:
   the companion **closed its side of the mirror**. Its sixth attempt localised the gap
   to the estimator — truth-fed, its exact planner escapes every committed pursuer
   24/24 — and its seventh rebuilt the estimator as a model-matched emitter decoder
   that inverts the hash-locked scent physics. Its live evasion now scores **24/24
   against all three pursuit archetypes, 240/240 league points, robustness configs
   included**. Read together with §1c, the two repositories now each corner the
   archetypes the other publishes, which is the expected end state of a mirror: each
   side's measured ceiling is the other side's next opponent model, and neither result
   is evidence about a classmate. See the companion's `results/pursuer_grid.json`.)*

Measured here and **reverted**: a Bayes-recursive belief (prior carried and multiplied
every turn) collapsed tracking — `flee_greedy` went 40/40 → 0/40 on that change alone.
Recursion under a static likelihood has no motion model, so history accumulates and the
argmax calcifies on old trail. Both live loops now rebuild belief fresh per observation and
carry the prior only across silent turns.

## 1c. The tournament grid (`M6-25`, `M6-26`) — the policy actually served

§1b measured `barrier_stack`. **It is no longer what this peer serves.** Since 2026-08-08
the served policy is `strategy/shrink.shrinking_turn_intent`, and the archetype set was
widened from three to five and re-run on two board sizes
(`scripts/experiment_tournament.py`; `results/tournament_grid.json`,
`results/tournament_grid_9x9.json`; 40 paired seeds per cell).

| Cop arm | random | flee-greedy | flee-smart | flee-deadend | flee-territory |
|---|---:|---:|---:|---:|---:|
| barrier stack (previous) | 40/40 | 40/40 | **0/40** | **0/40** | 40/40 |
| **shrink stack (served)** | **40/40** | **40/40** | **40/40** | **40/40** | **40/40** |
| oracle + shrink (sees truth) | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 |

Identical on 7×7 and on 9×9 — every cell above holds at both sizes.

Two things are worth stating precisely, because both are easy to overclaim:

1. **The fix was in the chase, not in the walls.** §1b concluded that `flee_smart` needed
   more or better barriers. It did not: the wall trio is unchanged. The Cop was losing an
   edge-bobbing evader to its own tie-breaking — Manhattan rank plus a fixed
   north-before-east tie order mirrors the evader's step forever. Ranking instead by the
   **summed** BFS distance over the believed cell's whole flight set breaks the mirror, and
   that single change converts both failing archetypes.
2. **`belief` now equals `oracle` on every cell.** The served stack aimed by private belief
   scores exactly what the same stack aimed by referee truth scores. That is the strongest
   statement this repository can make about its estimator, and it is still a statement about
   *these five archetypes* — none of which is a classmate.

## 2. Parameter sweeps (`M9-06a`)

Appendix F marks each parameter `Fixed`, `Minimum` or `Negotiation`. Asked directly:
`Minimum` "may be raised by agreement but never lowered", so every sweep here runs **upward
from its minimum**. Sweeping below would study a configuration rule 12 forbids.

![Parameter sensitivity heatmap](../assets/chart-parameter-sensitivity.svg)

**All three sweeps are now flat, and that is itself the result.** When this section was
first written the survival threshold was the one Minimum that moved the outcome. It no
longer is — the policy improved underneath the sweep, and every capture now lands so far
inside the horizon that the horizon stopped mattering. A sweep that goes flat because the
agent got better is worth more than one that was never sensitive.

### 2.1 Survival threshold — no longer a lever

| Threshold | Capture rate | Mean turns |
|---|---|---|
| 35 (minimum) | 1.000 | 9.68 |
| 45 – 75 | 1.000 | 9.68 |

Identical to four decimals at every value, turns included. Every capture happens by turn 26
at the very latest (§1), so nothing the horizon does past 35 can change a single game.
**Earlier this sweep showed 0.975 → 1.000 between 35 and 45**, because one seed then
survived the minimum horizon; no seed does now, and the lever disappeared with it.

### 2.2 Board size — flat, with one escape

| Grid | Capture rate | Mean turns |
|---|---|---|
| 7×7 (minimum) | 1.000 | 9.68 |
| 8×8 | 1.000 | 9.18 |
| 9×9 | 1.000 | 9.32 |
| 10×10 | 1.000 | 9.35 |
| 11×11 | **0.975** | 9.60 |
| 12×12 | 1.000 | 9.60 |

A larger board should make capture harder, and it very nearly does not. The single escape at
11×11 is one seed out of forty and does not recur at 12×12, so it is noise at this n rather
than a threshold — stated that way rather than explained.

The sweep alone cannot say why the line is flat, so `results/board_reach.json` measures how
much of the board is actually used:

| Grid | Highest index the Thief ever reached | Available |
|---|---|---|
| 7×7 | 6 | 6 |
| 9×9 | 8 | 8 |
| 12×12 | **9** | 11 |

On 7×7 and 9×9 the walk now reaches the far edge; on 12×12 the outer two ranks stay
unvisited within the 35-turn horizon. So the flatness is no longer explained by unreachable
space — up to 9×9 the space *is* reached and capture holds anyway. The honest conclusion has
moved: board size is not a lever for this policy against this opponent, and the start
positions (`thief_start (3,3)`, `cop_start (0,0)`, both `Negotiation`) only still matter at
the largest sizes.

### 2.3 Barrier quota — flat because the measured arm never places a barrier

| Quota | Capture rate |
|---|---|
| 14 (minimum) – 30 | 1.000 (identical to four decimals) |

A perfectly flat line is a warning, not a result. `results/decision_mix.json` counts what
the arm actually decides:

```json
{"matches": 40, "decisions": 375, "by_type": {"Action": 375}, "barrier_intents": 0}
```

**Zero barrier intents in 375 decisions.** The belief arm is pursuit-only, so the quota
sweep is measuring an unused parameter. This is a real finding about our own measurement
rather than about the parameter: `strategy/barrier_policy.py` and `strategy/squeeze.py`
exist, are tested (`M6-06`), and are wired into the **served** stack whose results are in
§1c — but they are not in the arm §1 and §2 measure. Reporting "barrier quota has no effect"
would therefore be false; the correct statement is that *this arm does not use barriers*, so
the quota's effect is unmeasured here. §1c is where the barrier machinery is actually
exercised, and there it is the entire capture mechanism.

## 3. Decision cost (`M6-13`)

![Per-turn decision cost](../assets/chart-decision-cost.svg)

| Statistic | Milliseconds |
|---|---|
| mean | 1.98 |
| median | 1.85 |
| p95 | 3.05 |
| **max** | **4.43** |
| Negotiated response timeout | 30 000 |

Worst case is **0.0148%** of the response-timeout budget, over 400 samples. The computational
fairness claim is therefore not close to contested: the agent could be 6 700× slower and
still answer inside the negotiated window.

## 4. The scent model (`M9-06b`)

![Scent decay from a single deposit](../assets/chart-scent-decay.svg)

Source intensity 0.9 and decay 0.10 per turn are both Appendix F **`Fixed`** — deviation
cancels the game under rule 23. The curve is published to *explain* the model, not to
propose retuning it: a single deposit falls below 0.1 after 21 turns, which is why a trail
stays informative for roughly two thirds of a minimum-length game.

## 5. Learning curves

The book requires learning curves **"if RL was used"** (p.81/189). This policy is
deterministic and weight-free — a fixed lexicographic ranking, no training, no parameters
fitted from data — so there is no convergence to plot. Asked directly, the book is *silent*
on what should replace the section for a deterministic policy.

Rather than leave it empty, §1's paired comparison is offered in its place: it is the same
question a learning curve answers — *is this policy actually better than the alternative,
and by how much* — settled by measurement rather than by asserting that it is.

## Threats to validity

Stated because the numbers above are strong, and strong numbers deserve their limits printed
next to them.

1. **One opponent in §1 and §2.** Those measurements are against a seeded random walk that
   does not react to the Cop, so belief's 100% gap closure is an upper bound on that
   opponent class only. §1b and §1c exist precisely because that was the weakest half of
   the evidence.
2. **Five archetypes are still not a classmate.** §1c's 40/40 is measured against evaders
   *we wrote*, and an opponent model written by the same team that beats it is the oldest
   way to be wrong. No counted league game has been played, so nothing here is evidence
   about another group's agent.
3. **The arm is not the whole agent.** As §2.3 shows, the arm measured in §1 and §2 excludes
   the barrier machinery the repository actually serves; §1c measures the served stack.
4. **40 seeds.** Enough for the paired result (19–0–21 with zero losses), thin for the flat
   sweeps, where the honest claim is "no effect detected at n=40" rather than "no effect" —
   and thin enough that §2.2's single 11×11 escape is not a finding.
