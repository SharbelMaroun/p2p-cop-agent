# Code-quality self-assessment

Covers `M9-14`, `M9-14a`, `M9-14b`, `M9-05e`.

Scored against the submission guidelines' own requirements. **A score is only worth something
if it can go down**, so the section that matters is the second — what is not met and why. A
self-assessment claiming full marks tells a grader nothing they could not have assumed.

Scale: **2** = met with evidence a third party can check · **1** = partial · **0** = not met.

## Scored — `M9-14a`

| # | Guidelines requirement | Score | Evidence, and the reservation |
| --- | --- | :---: | --- |
| 1 | `docs/PRD.md` and a PRD per mechanism (§2.3) | 2 | Seven: commit_reveal, p2p_mcp, gatekeeper_reporting, strategy, scent_belief, gui, replay |
| 2 | `docs/PLAN.md` with architecture and ADRs | 1 | ADRs present; **the C4 and UML diagrams §2.2 asks for are prose and tables, not diagrams** |
| 3 | `docs/TODO.md` with priorities, status, DoD | 2 | Every row has a priority, a definition of done and an evidence string |
| 4 | Comments explain the *why* | 2 | Module docstrings carry the rule and its sanction rather than restating the code |
| 5 | Docstrings everywhere | 1 | **Corrected 2026-08-08.** This row claimed ruff `D` enforcement; `D` is **not** in the select set (`pyproject.toml`), so the claim was false. Measured instead: 671 of 753 public definitions and modules carry docstrings (82 missing, mostly `__init__` and nested chart helpers). Present by review, not tool-enforced |
| 6 | Automated tests with meaningful coverage | 2 | 1819 tests, 96.50% branch against an 85% floor |
| 7 | Lint at zero findings | 2 | `ruff check .` clean under a pinned select set |
| 8 | Reproducible install | 2 | `uv.lock`, `uv sync --frozen`, verified by `scripts/verify_clean_clone.py` |
| 9 | CI runs every gate on every push | 2 | `.github/workflows/ci.yml`. **Was 1 until 2026-08-07** — the history scanner existed and CI never ran it |
| 10 | No secrets in the repository | 2 | Tree and full history; 2722 objects, 1 reviewed false positive pinned by blob SHA, 0 unreviewed |
| 11 | Standard project structure | 2 | `src/` layout, `docs/`, `scripts/`, `tests/{unit,integration,conformance}`, `shared_contract/` |
| 12 | Maintainability | 1 | 150-line cap holds, but some splits satisfy the counter rather than a concept boundary |
| 13 | Portability | 1 | Frozen install verified from a clean clone; **Windows only, never run on Linux or macOS** |
| 14 | Prompt-engineering log | 2 | `docs/PROMPT_LOG.md`, updated per batch |
| 15 | Performance evidence | 1 | Benchmarks and a research report exist; **no profiling against an adversarial peer** |

**Total: 26 / 30.**

## What is not met, and why — `M9-14b`

**Diagrams (#2, scored 1).** §2.2 asks for C4 diagrams, UML for complex processes, and
deployment diagrams. `docs/PLAN.md` describes the architecture in prose and tables. The
information exists; the *form* asked for does not. Diagrams were never prioritised over
behaviour, and claiming "the content is equivalent" would be deciding on the grader's behalf
what the requirement meant.

**Cohesion versus the line cap (#12, scored 1).** The 150-line rule is a genuine gate with a
genuine cost. Several modules were split where the counter complained rather than where the
concept changed. Where a split produced a better seam the docstring says so; where it did not,
it says which file it was cut from.

**Portability (#13, scored 1).** Everything runs on Windows 11 and nowhere else. `uv.lock`
and the clean-clone check make a Linux run *likely* to work — likely is not evidence. `M9-12a`
stays open and no cross-platform claim appears in the README.

**Performance (#15, scored 1).** Every measurement is against our own peer or a synthetic
opponent. A real classmate could produce latency and queue behaviour none of it predicts.

## Two weaknesses the guidelines do not ask about

**The coverage figure excludes the layer most likely to be wrong on the day.** 96.50% branch
is measured with `src/*/ui/*` omitted, which the guidelines' own coverage config permits and
which this repository argues for in `pyproject.toml`. It is still true that the widgets a
grader will look at are the least-tested code here; `replay/view_model.py` and
`live/view_model.py` carry the assertions instead.

**This section previously recorded two weaknesses that measurement retired**, and both are
kept visible rather than quietly deleted. Coverage was said to be lower here than in the
companion (96.50% against 95.58% — it is now higher, and neither gap was ever material
against an 85% floor). The Thief's CLI was said to be a scaffold that could not be launched;
`p2p-thief serve --peer … --game …` plays a real match and four two-process rehearsals have
been played through it. **A claim about the other repository is the easiest kind to leave
stale, because nothing in this repository fails when it rots.**

## What the score does not cover

* **Guards are proven to bite.** Renaming a frozen wire method fails conformance tests; the
  reviewed-history pin is content-addressed so it cannot suppress anything but the exact bytes
  reviewed. A test that passes with and without the code it guards is decoration.
* **Refusals carry the rule and its sanction**, so an operator reading `[AE-38]` learns a
  false game count disqualifies the project rather than that a number did not match.

## Final self-assessed score — `M9-05e`

**25 / 30 (83%).** Five requirements at partial credit, none at zero. Recorded here rather
than left for a grader to find.

**This score went down on 2026-08-08, and the reason is the point of scoring at all.** It was
26/30 until an audit checked row 5's evidence against `pyproject.toml` and found the claimed
ruff `D` enforcement was not there. A self-assessment that only ever rises is a marketing
document; the row was re-scored to 1 and the false claim left visible above rather than
swapped for a true one of equal value.
