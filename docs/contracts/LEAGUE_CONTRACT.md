# Proposed Stable League Contract

Contract version: `0.1.0-proposed`
Status: **PROPOSED / UNFROZEN**

This document separates stable public semantics from match-specific values and
private peer configuration. It is a Cop-authored review candidate, not an accepted
cross-repository contract.

## Evidence-backed semantics

| Area | Public semantic rule | Authority |
|---|---|---|
| Isolation | Cop and Thief are independent peers with no shared live state or private truth. | Appendix E rules 1–2 |
| Agreement | Both participants agree the played-match configuration and hold identical shared values. | Appendix B; Appendix E rule 11; Appendix F instructions |
| Retention | A uniquely named configuration is retained for each game. | Appendix F instructions and table 20 |
| Locking | The complete shared `game.json` object is canonically hashed and cryptographically locked before play. | Appendix B; owner-supplied lecturer direction dated 2026-07-27 |
| Series | A counted opponent encounter contains six sub-games. | Appendix F table 18 |
| Roles | Natural role on odd sub-games; opposite role on even sub-games. | Owner-supplied lecturer direction dated 2026-07-27, corroborated by pinned simulator |
| Private override | Agreed shared JSON overrides overlapping local peer TOML. | Appendix B |

Artifact cardinality and identity are defined in `ARTIFACT_CONTRACT.md`.

## Appendix F status and ownership

`Fixed` values are source-owned and cannot be changed. `Minimum` values are mutually
owned: participants may agree on a stricter value in the permitted direction but
never cross the stated floor. `Negotiated` values are mutually owned; the Appendix F
example is the fallback when no different value is explicitly agreed.

| Status | Parameters |
|---|---|
| Fixed | number of agents; move set; scent center/decay/field; scoring; six sub-games; diversity reward; minimum counted opponents; maximum counted games |
| Minimum | grid size; barrier quota; max moves; survival threshold; requests/minute; concurrency; retry delay; retries; queue depth |
| Negotiated | axis origin/index; opening positions; map area; hint word cap; series token budget; response timeout; watchdog timeout |

The exact values and direct Appendix F locators are in
`docs/PARAMETERS_BASELINE.md`. The machine schema applies fixed constants and minimum
floors to actual proposed match values; it does not turn example defaults into fixed
requirements.

## Proposed extension and version policy

- Book example profile `1.2`, local generated-artifact observation `1.1`, and
  simulator runtime profile `1.3` are distinct. No normalization is defined.
- This candidate validates only `1.2` match input and rejects other versions clearly.
- The JSON Schema documents and their field names are project proposals, not official
  course schemas.
- A closed known-field surface plus an explicit `extensions` object is proposed for
  deterministic review. Whether official artifacts permit extra properties remains
  unresolved.

## Excluded private data

Ports, local opponent-URL storage, provider/model choices, credentials, private
strategy or tuning, tunnel secrets, API tokens, nonces, and other secrets are never
members of the public parity bundle. Public identity or URL fields required by an
authenticated artifact schema remain subject to clarification.
