# Submission Checklist (mandatory process requirements)

Shared, byte-identical in both repositories. Captures the mandatory **submission and league-
integrity** requirements from the book so none is forgotten at submission time. Confirmed
obligations are also recorded in [REQUIREMENTS_LEDGER.md](REQUIREMENTS_LEDGER.md); items needing
team or Moodle input are tracked in [TEAM_INFO.md](TEAM_INFO.md) and
[UNKNOWN_REQUIREMENTS.md](UNKNOWN_REQUIREMENTS.md). The boxes are completed during
implementation/submission, not during the requirements phase.

## Repository & release (Appendix E rules 41, 49, 50; Appendix C)
- [ ] Two separate repos (Cop + Thief); each README cross-links the other — `SR-001/002`.
- [ ] Both repos accessible to the lecturer (public, or shared with the lecturer address) — `SR-003`.
- [ ] Annotated Git tag marks the submission commit (book example `v1.0-submission`; confirm on Moodle) — `SR-007`.
- [ ] Each repo contains README, `/config`, PRD(s), PLAN, TODO, and code — `SR-006`.

## Academic report in README (rule 42; Ch.9.4.2) — `SR-008`
- [ ] Six sections: (1) Dec-POMDP model, (2) FastMCP dilemma, (3) strategy, (4) learning curves if RL,
      (5) screenshots (belief-map GUI + "Verified OK" replay), (6) companion-repository link.

## Reporting (rules 32–35, 51–54) — exact templates pending
- [ ] Each side auto-sends a signed JSON result at the end of every legal game (JSON only; free text rejected).
- [ ] Both sides agree the result; conflicting reports → 0/0.
- [ ] Reporting address (candidate, verify spelling — `C-004`): `rmisegal+uoh26finalgame@gmail.com`.
- [ ] Every game's commit hash and total tokens are included in the JSON.

## League integrity (rules 31, 37, 38, 52) — league play pending
- [ ] Play at least the minimum number of **different** teams (candidate min-to-pass 2 — PARAMETERS_BASELINE).
- [ ] Declare accurately how many games were played vs each opponent; false declaration = disqualification.
- [ ] Only one scored game per opponent; warm-up games are uncounted.

## Moodle (rules 43, 44, 45)
- [ ] Fill the Moodle Word/PDF template without moving fields; submit as PDF.
- [ ] Each team member submits separately in Moodle.
- [ ] Provide the unique **8-character team code** (no spaces) — team input (`U-016`).

## Secrets (rules 39, 40) — `PS-006`
- [ ] No secrets committed; `.gitignore` excludes `.env`, `credentials.json`, `token.json`, `*.key`.
