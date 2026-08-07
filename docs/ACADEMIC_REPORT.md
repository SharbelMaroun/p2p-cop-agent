# Academic report — model, decisions, results

Covers `M9-10`, `M9-10a`, `M9-10b`, `M9-10c`, `M9-10d`, `M9-07c`, `M9-03`, `M9-03a`.

The README carries the six components §9.4.2 requires. This is the body underneath: the
formalism in the book's own notation, the architectural decisions with what each one cost,
and the measurements.

## 1. The formalism

### 1.1 The Dec-POMDP tuple

The book models the game as a decentralised partially-observable Markov decision process
(p.4/109), an ordered tuple of eight components:

$$\langle n,\; S,\; \{A_i\},\; P,\; R,\; \{\Omega_i\},\; O,\; \gamma \rangle$$

| Symbol | Meaning | On the Cop side |
| --- | --- | --- |
| $n$ | agents | 2 — symmetric peers, no referee |
| $S$ | state space | positions × barrier placement × turn index |
| $A_i$ | actions | move N/E/S/W, or place a barrier — exclusive, never both in a turn |
| $P$ | transition | deterministic; `domain/` applies a legal move or refuses it |
| $R$ | reward | Appendix F table 17 |
| $\Omega_i$ | observations | own cell, disclosed barriers, the 5×5 scent window, the opponent's hint |
| $O$ | observation function | partial — the Cop never sees the Thief's position |
| $\gamma$ | discount | $\gamma \in [0,1]$; unused, because the pursuit policy is myopic (§2.2) |

$O$ being partial is the entire problem. Under full observation the pursuit is a
shortest-path computation, which is why the `oracle` arm in §3.1 exists only as a ceiling.

### 1.2 The scent model

Scent intensity in cell $(i,j)$ updates once per full turn (p.27/115):

$$\tau_{ij}(t+1) = \max\left(0,\; (1-\rho)\cdot\tau_{ij}(t) + \Delta\tau_{ij}\right)$$

with $\rho = 0.10$. The $\max(0,\cdot)$ prevents floating-point drift carrying a decayed cell
negative, which would put a negative prior into the belief update.

> **Two contradictions in the source, disclosed under chapter 110** (`M9-10c`). Both are
> recorded in `docs/SPECIFICATION_CONFLICTS.md` as `C-014` and `C-015`; they were identified
> during M6 and are restated here because §1.2's formula relies on the resolution.
>
> **`C-014`** — the prose (ch. 4.3, p.43; `inst/:930`) says $(1-\rho)$ means "the existing
> scent is **reduced by 90%**". The formula beside it says the opposite: $(1-\rho) = 0.90$
> *retains* 90%, reducing by 10%. We implement the **formula** — rule 23's lock is taken
> over the formula, and the prose reading would decay ten times too fast, erasing the very
> history trail the mechanism exists to leave.
>
> **`C-015`** — the book (ch. 4.4, p.46) says raising $\rho$ toward 1.0 would leave the
> board "**saturated** with scent". Reversed: $\rho \to 1.0$ drives $(1-\rho) \to 0$ and
> scent vanishes almost immediately; saturation is what $\rho \to 0$ approaches. The
> sensitivity sweeps in §3.2 use the correct direction.

> **A third contradiction, in the scoring boundary** (`M3-07c`, `C-024`). Appendix F table
> 15 sets `[Step Limit]` and `[Survival Threshold]` to the **same value**, 35. Two readings
> follow and the book never chooses between them: does the Thief win by surviving *exactly*
> 35 steps, or must it exceed them? One turn separates the two, and a whole sub-game — 20
> points — hangs on it.
>
> **Where it is.** Not in a figure or an aside: in the mandatory parameters table, the one
> document both peers negotiate from. Two agents built from the same appendix can disagree
> about who won a game they both played correctly.
>
> **What we chose.** The **inclusive** horizon — completing step 35 uncaptured is a Thief
> win.
>
> **Why.** Chapter 3 table 2 (PDF p. 38) defines the survival outcome as the Thief surviving
> "the limit of valid moves" without capture, and table 15 makes that limit *equal* the
> threshold. The two tables together settle what either alone leaves open, so no ruling was
> needed. `run_sub_game` already behaved this way; what was missing was the record and the
> test. `tests/unit/test_horizon_boundary.py` now asserts threshold−1, threshold and
> threshold+1 — one assertion at the threshold cannot distinguish the two readings, since
> both stop somewhere near it. `U-027` is closed and `C-024` marked `RESOLVED`.
>
> This is disclosed rather than quietly implemented because an off-by-one here does not
> crash and does not look wrong. It surfaces only in the score, which is exactly where a
> silent disagreement with an opponent becomes expensive.

### 1.3 The belief map

The posterior over the Thief's position (p.48/123):

$$b(s) = P(\text{thief} = s \mid \text{hints})$$

updated by Bayes from observation only:

$$b_{t+1}(s) \;=\; \frac{P(o_{t+1} \mid s)\; \sum_{s'} P(s \mid s')\, b_t(s')}{\sum_{u} P(o_{t+1} \mid u) \sum_{s'} P(u \mid s')\, b_t(s')}$$

The policy aims at $\arg\max_s b(s)$ rather than at a last-known cell. **Observation only** is
a commitment, not a detail: rule 2 forbids sharing memory between parties, sanction immediate
disqualification for data leakage, so a belief updated from anything the Thief did not emit
would be that breach. The belief is Cop-private and never crosses the wire.

### 1.4 Rate limiting

The gatekeeper is a token bucket (Appendix F table 19):

$$\text{tokens} \leftarrow \min\left(C,\; \text{tokens} + r\cdot\Delta t\right), \qquad \text{allow} \iff \text{tokens} \geq 1$$

Burst to $C$, then a steady $r$ — the shape that survives a provider answering `429`.

## 2. Architectural decisions and their cost — `M9-10a`

### 2.1 The language model never chooses a move

Movement is pure Python and fully deterministic; the shipped provider is a zero-token
template.

**Gained:** two agents in the same state produce the same move, so a match replays from its
log — which is what makes rule 20's verification mean anything. No API key, no flaky suite.
**Cost:** no tactical contribution from a model, and no claim to an LLM-driven strategy. The
book permits either; we took the one an auditor can re-derive.

### 2.2 Lexicographic ranking, and $\gamma$ left unused

Candidate actions are ranked by a strict criterion order rather than a weighted score.

**Gained:** auditable — a reader can say why a move was chosen.
**Cost:** no lookahead, and $\gamma$ appears in the formalism while doing nothing in the code.
Said plainly rather than inventing a discount factor to look complete. No calibration data
exists that would justify weights, and coefficients nobody can defend are worse than an order
anybody can read.

### 2.3 Barrier placement is exclusive with movement

The Cop either moves or places, never both in one turn.

**Gained:** the turn stays a single legal action, so a replay cannot be ambiguous about what
happened.
**Cost:** real tempo. A turn spent placing is a turn not closing distance, and §3.1's capture
rate is achieved despite that constraint rather than because of it.

### 2.4 Artifact validation by JSON Schema

**Gained:** a schema file can be handed to an opponent and checked by anything.
**Cost:** the schemas assert requiredness the sources may not support (`U-019`), and one of
them shipped broken — `X-04`: `per-subgame-config.schema.json` pinned the literal pattern
`g<NN>`, so it validated a *template* and refused every real artifact, which is exactly the
failure the row exists to prevent. The companion Thief chose a citation table instead; both
are pinned as correct for their own side rather than reconciled.

### 2.5 Two sanctions, kept apart

Rule 19 scores 0 for the *falsifying group*; rule 35 scores 0 for **both**.

**Gained:** catching an opponent's forgery does not trigger our own contradicting report.
`require_reportable` refuses to send after a failed audit, because racing them to the lecturer
converts their loss into a shared one.
**Cost:** a game we know we won can end unreported and unscored. That is the correct trade —
0 is better than −(our own points too).

## 3. Empirical results — `M9-10b`

40 paired seeds; seed $i$ gives every arm the identical Thief trajectory. Protocol and threats
to validity in `docs/RESEARCH-REPORT-Performance-Analysis.md`.

### 3.1 Strategy comparison

| Arm | Capture rate | Mean turns | Mean Cop score | sd |
| --- | ---: | ---: | ---: | ---: |
| blind | 0.225 | 32.83 | 8.38 | 6.34 |
| **belief** | **0.975** | **12.83** | **19.62** | **2.37** |
| oracle | 1.000 | 12.10 | 20.00 | 0.00 |

The belief policy captures **97.5%** against the blind baseline's 22.5%, and sits within
**0.73 turns** of perfect information. The gap to `oracle` is the cost of partial
observability, and it is small — the 5×5 scent window carries most of the signal a perfect
observer would have.

The standard deviations matter as much as the means: 2.37 against blind's 6.34. The belief
policy is not merely better on average, it is **consistent**, which is what a league rewards.

### 3.2 Parameter sweeps

**Survival threshold** is the only `Minimum` that moves the outcome, and only at its floor:
0.975 at 35, 1.000 from 45 upward. Every extra turn past ~45 is a turn the Cop did not need.

**Board size is flat**, and the reason is not the obvious one — see the research report. A
larger board does not dilute the scent signal because the Thief's trail lengthens with it.

### 3.3 Token and cost accounting — `M9-03`, `M9-03a`

Rule 54 requires tokens per game **and** per series. Both figures are emitted: `tokens_total`
per sub-game in the log artifact, `tokens_total_series` in the result.

| Configuration | Tokens per 6-sub-game series | Monetary cost |
| --- | ---: | --- |
| Shipped default (template provider) | **0** | **0** |
| Reference implementation, live model | ~17 500 | provider-dependent |

**The shipped configuration consumes no tokens at all**, because movement is deterministic and
the verbal layer emits templates. The agreed limit exists and is enforced by the ledger; we
simply never approach it. That is a real result rather than an omission: the token budget is
not a constraint on this design, and a league opponent burning 17.5k per series is paying for
capability we chose not to buy (§2.1).

No monetary cost is computed at runtime, here or in the reference. Cost is a function of the
provider and the plan, neither of which is fixed at play time, and a number invented at
runtime would be less honest than none.

## 4. References — `M9-10d`, `M9-07c`

Numbered per the guidelines' bibliography format (`inst/:1082`).

1. Y. Segal, *Distributed Cop-and-Thief Race over a Peer-to-Peer Network — Final Project v3.0.0*, University of Haifa, 2026. — binding source for every rule, appendix and parameter cited.
2. Y. Segal, *Software Submission Guidelines v3*, University of Haifa, 2026. — §2.2 documentation structure, §13.1 ISO/IEC 25010, and this reference format.
3. ISO/IEC 25010:2011, *Systems and software engineering — SQuaRE — System and software quality models*, ISO, 2011.
4. F. A. Oliehoek and C. Amato, *A Concise Introduction to Decentralized POMDPs*, Springer, 2016. — the formalism of §1.1.
5. M. Naor, *Bit commitment using pseudorandomness*, Journal of Cryptology 4(2), 1991.
6. NIST, *FIPS PUB 180-4: Secure Hash Standard (SHS)*, 2015. — SHA-256, on whose collision resistance rule 19's audit rests.
7. M. Dorigo, M. Birattari and T. Stützle, *Ant Colony Optimization*, IEEE Computational Intelligence Magazine 1(4), 2006. — stigmergy and the emission/decay model of §1.2.
8. J. Nielsen, *10 usability heuristics for user interface design*, https://www.nngroup.com/articles/ten-usability-heuristics/, 1994. — guidelines reference [13]/[14].
9. Anthropic, *API key best practices*, https://support.claude.com/en/articles/9767949-api-key-best-practices, 2024. — guidelines reference [10].
10. Model Context Protocol, *Specification*, https://modelcontextprotocol.io/, 2025. — the transport the book mandates.

Course material in `inst/` is quoted under fair academic use and cited by page throughout.
