# Submission Checklist

This checklist is source-backed but is not claimed to be byte-identical with the
Thief repository.

## Repository and release

- [ ] Separate Cop and Thief repositories; reciprocal README links.
- [ ] Both repositories accessible to the lecturer/general address
      `rmisegal@gmail.com`.
- [ ] Annotated Git tag marks the final submission commit; confirm the literal name
      against current Moodle guidance.
- [ ] Each repository contains README, config, PRDs, PLAN, TODO, code,
      `pyproject.toml`, and committed `uv.lock`.
- [x] Cop clean `uv sync --frozen`, Ruff, tests/coverage, length, secret, and
      contract-parity checks pass for M1.
- [ ] Thief independently runs its frozen install and matching parity checks after
      accepting the proposed bundle.

## Six-section README report

- [ ] Dec-POMDP model.
- [ ] FastMCP communication dilemma and orchestration choices.
- [ ] Implemented strategy.
- [ ] RL learning curves, if RL is used.
- [ ] Live belief-map and `Verified OK` replay screenshots.
- [x] Companion-repository link.

## Reporting

- [ ] Each side independently sends the signed final JSON as an attachment; no
      free-text final-report body.
- [ ] Destination is `rmisegal+uoh26finalgame@gmail.com`.
- [ ] Both sides agree the result; missing/conflicting reports yield zero for both.
- [ ] Required report content includes four repository links, each game’s commit
      hash, and total token use, without inventing unsupported formal key rules.

## League integrity

- [ ] Each counted opponent encounter uses the fixed six-sub-game series.
- [ ] Complete the required minimum against at least two different opponents/teams.
- [ ] Count only one series/match per opponent; warm-ups are uncounted.
- [ ] Declare counts accurately; false declaration is disqualifying.

## Moodle, secrets, and provenance

- [ ] Complete the supplied Moodle form without moving fields; submit PDF as directed.
- [ ] Every team member submits separately.
- [ ] Provide the eight-character team code.
- [ ] No secrets committed; `.gitignore` covers `.env`, credentials, tokens, and keys.
- [ ] No substantial lecturer-simulator source copied without ADR-008
      provenance/license resolution or permission.
