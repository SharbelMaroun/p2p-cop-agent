# Parameters Baseline — directly confirmed Appendix F values

> **Confidence: HIGH.** Values and statuses were checked directly against the
> official project book v3.0.0, Appendix F tables 13–19 (PDF pp. 152–155 /
> printed pp. 136–139).
>
> `Fixed` cannot change. `Minimum` may be made stricter by mutual agreement but
> never relaxed below the listed value. `Negotiation` may be agreed freely; the
> listed value is the default.
>
> Four inspected local simulator-generated artifacts expose observed field names and
> key sets, but their official provenance is `NEEDS_MANUAL_REVIEW`. They do not
> establish formal required/optional, type/enum, conditional, or compatibility rules.

## Board, coordinates, and opening positions — Table 13

| Parameter | Value | Status | Direct source |
|---|---|---|---|
| Square board side | 7 | Minimum | Appendix F table 13, PDF p. 152 |
| Number of agents | 2 | Fixed | Appendix F table 13, PDF p. 152 |
| Coordinate origin | top-left | Negotiation default | Appendix F table 13, PDF p. 152 |
| Coordinate start index | 0 | Negotiation default | Appendix F table 13, PDF p. 152 |
| Thief opening position | `(3, 3)` center | Negotiation default | Appendix F table 13, PDF p. 152 |
| Cop opening position | `(0, 0)` corner | Negotiation default | Appendix F table 13, PDF p. 152 |

Seven is a minimum, not an immutable board size. Do not hard-code unrelated 5×5 or
10×10 illustrations; a larger board is legal only when the parties agree and all
derived positions validate.

## Arena and verbal clues — Table 14

| Parameter | Value | Status | Direct source |
|---|---|---|---|
| Real-world map area | New York; empty means generic | Negotiation default | Appendix F table 14, PDF p. 152 |
| Words per clue | 15 | Negotiation default | Appendix F table 14, PDF p. 152 |

## Movement and barriers — Table 15

| Parameter | Value | Status | Direct source |
|---|---|---|---|
| Move set | `N`, `S`, `E`, `W`, `STAY`; no diagonals | Fixed | Appendix F table 15, PDF p. 153 |
| Cop barrier quota | 14 | Minimum | Appendix F table 15, PDF p. 153 |
| Step limit | 35 | Minimum | Appendix F table 15, PDF p. 153 |
| Survival threshold | 35 | Minimum | Appendix F table 15, PDF p. 153 |

## Scent — Table 16

| Parameter | Value | Status | Direct source |
|---|---|---|---|
| Center intensity | 0.9 | Fixed | Appendix F table 16, PDF p. 153 |
| Per-turn decay rate `ρ` | 0.10 | Fixed | Appendix F table 16, PDF p. 153 |
| Emission field | 5×5 | Fixed | Appendix F table 16, PDF p. 153 |

## Scoring — Table 17 plus Appendix E sanctions

| Outcome | Cop | Thief | Status / direct source |
|---|---:|---:|---|
| Capture | 20 | 5 | Fixed; Appendix F table 17, PDF p. 154 |
| Survival to threshold | 5 | 10 | Fixed; Appendix F table 17, PDF p. 154 |
| Tie | 2 | 2 | Fixed; Appendix F table 17, PDF p. 154 |
| Technical loss | 0 if Cop falsifies; otherwise `U-026` | 0 if Thief falsifies; otherwise `U-026` | Mandatory zero for the falsifying peer; Appendix E rules 19/48, PDF pp. 145/149 |

The falsifying peer's zero is directly confirmed, but the non-falsifying peer's
award remains unresolved under `U-026`. Technical loss is not a row in Appendix F
table 17 and must not be cited as one.

## Network and league — Table 18

| Parameter | Value | Status | Direct source |
|---|---|---|---|
| Sub-games in one series against an opponent | 6 | Fixed | Appendix F table 18, PDF p. 154 |
| Diversity reward for a new opponent | 10 | Fixed | Appendix F table 18, PDF p. 154 |
| Minimum counted opponents/games to pass | 2 | Fixed | Appendix F table 18 plus Appendix E rule 31 |
| Estimated LLM-token budget per series | ~200000 | Negotiation default | Appendix F table 18, PDF p. 154 |
| Maximum counted games per group | 10 | Fixed | Appendix F table 18, PDF p. 154 |

The actual token consumption is reported by email; the original text does not say
to convert this row to USD. A counted opponent encounter is a six-sub-game series;
the separate minimum of two concerns league participation, not series length.

## Rate limiter / Gatekeeper — Table 19

| Parameter | Value | Status | Direct source |
|---|---|---|---|
| Outgoing API requests per minute | 30 | Minimum | Appendix F table 19, PDF p. 155 |
| Concurrent requests | 2 | Minimum | Appendix F table 19, PDF p. 155 |
| Base retry delay | 5 seconds | Minimum | Appendix F table 19, PDF p. 155 |
| Retry attempts | 3 | Minimum | Appendix F table 19, PDF p. 155 |
| Queue depth | 100 | Minimum | Appendix F table 19, PDF p. 155 |
| Response timeout | 30 seconds | Negotiation default | Appendix F table 19, PDF p. 155 |
| Watchdog threshold | 60 seconds | Negotiation default | Appendix F table 19, PDF p. 155 |

The values belong in configuration, not hard-coded runtime constants. Exact MCP
names, envelope fields, commit canonical bytes, and simulator defaults are separate
ADR/contract questions.
