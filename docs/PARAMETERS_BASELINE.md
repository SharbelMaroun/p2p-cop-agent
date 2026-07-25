# Parameters Baseline — directly confirmed Appendix F values

> **Confidence: HIGH. Directly confirmed from the original PDF.**
> Every value and status below was checked directly against Appendix F, tables 13–19, in the
> official project book v3.0.0 (PDF pp. 152–155 / printed pp. 136–139). The per-row derived-source
> locators are retained only as secondary cross-checks. These binding values belong in
> configuration rather than hard-coded constants. Official JSON schemas and field names remain
> `UNKNOWN`.
>
> **Status meanings (book):** *Fixed* = cannot change; deviation = disqualification ·
> *Minimum* = may be raised by mutual agreement, never lowered · *Negotiation* = any agreed
> value; the listed value is the default.
>
> ⚠️ **Board-size trap (DEV-SPEC §2):** the binding board is **7×7**. The `10×10` and `5×5`
> values elsewhere in the source are **illustrations only** — never build to them.

## Board, coordinates, opening positions (Appendix F Table 13)

| Parameter | Value | Status | Provenance |
|---|---|---|---|
| Board size (square side) | 7×7 | Minimum | DEV-SPEC §3 T13; summary :3483 |
| Number of agents | 2 | Fixed | DEV-SPEC §3 T13; summary :3484 |
| Coordinate origin corner | top-left | Negotiation | DEV-SPEC §3 T13; summary :3485 |
| Coordinate start index | 0 | Negotiation | DEV-SPEC §3 T13; summary :3486 |
| Opening position — Thief | (3,3) center | Negotiation | DEV-SPEC §3 T13; summary :3487 |
| Opening position — Police | (0,0) corner | Negotiation | DEV-SPEC §3 T13; summary :3488 |

## Arena & verbal clues (Appendix F Table 14)

| Parameter | Value | Status | Provenance |
|---|---|---|---|
| Game arena (real-world map) | New York (empty ⇒ generic) | Negotiation | DEV-SPEC §3 T14; summary :3494 |
| Word limit per clue | 15 | Negotiation | DEV-SPEC §3 T14; summary :3495 |

## Movement & obstacles (Appendix F Table 15)

| Parameter | Value | Status | Provenance |
|---|---|---|---|
| Movement array | N/S/E/W + STAY (no diagonals) | Fixed | DEV-SPEC §3 T15; summary :3507 |
| Obstacle quota (cop barriers) | 14 | Minimum | DEV-SPEC §3 T15; summary :3508 |
| Step limit | 35 | Minimum | DEV-SPEC §3 T15; summary :3509 |
| Survival threshold | 35 | Minimum | DEV-SPEC §3 T15; summary :3510 |

## Pheromones / scent (Appendix F Table 16 — all Fixed)

| Parameter | Value | Status | Provenance |
|---|---|---|---|
| Scent intensity at source | 0.9 | Fixed | DEV-SPEC §3 T16; summary :3516 |
| Scent decay rate ρ | 0.10 | Fixed | DEV-SPEC §3 T16; summary :3517 |
| Scent field size | 5×5 | Fixed | DEV-SPEC §3 T16; summary :3518 |

## Scoring (Appendix F Table 17 — all Fixed)

| Outcome | Police | Thief | Provenance |
|---|---|---|---|
| Capture | 20 | 5 | DEV-SPEC §3 T17; summary :3530–3531 |
| Survival to threshold | 5 | 10 | DEV-SPEC §3 T17; summary :3532–3533 |
| Draw / tie | 2 | 2 | DEV-SPEC §3 T17; summary :3534 |
| Technical loss | 0 | 0 | DEV-SPEC §3 T17; summary :2953 |

## Network & league (Appendix F Table 18)

| Parameter | Value | Status | Provenance |
|---|---|---|---|
| Games in a series vs one opponent | 6 | Fixed | DEV-SPEC §3 T18; summary :3540 |
| Diversity/bonus reward (beat a new opponent) | 10 | Fixed | DEV-SPEC §3 T18; summary :3541 |
| Minimum games to pass (per group) | 2 | Fixed | DEV-SPEC §3 T18; summary :3542 |
| Estimated tokens per series (report in USD) | ~200000 | Negotiation | DEV-SPEC §3 T18; summary :3543 |
| Max games per group | 10 | Fixed | DEV-SPEC §3 T18; summary :3544 |

## Rate limiter / Gatekeeper (Appendix F Table 19)

| Parameter | Value | Status | Provenance |
|---|---|---|---|
| API request rate (per minute) | 30 | Minimum | DEV-SPEC §3 T19; summary :3556 |
| Concurrent requests | 2 | Minimum | DEV-SPEC §3 T19; summary :3557 |
| Retry delay (backoff) | 5 s | Minimum | DEV-SPEC §3 T19; summary :3558 |
| Retry attempts | 3 | Minimum | DEV-SPEC §3 T19; summary :3559 |
| Queue depth | 100 | Minimum | DEV-SPEC §3 T19; summary :3560 |
| Response timeout | 30 s | Negotiation | DEV-SPEC §3 T19; summary :3561 |
| Watchdog threshold | 60 s | Negotiation | DEV-SPEC §3 T19; summary :3562 |

---

_Directly verified 2026-07-25 against original PDF pp. 152–155. The official JSON templates,
exact MCP messages, and simulator-specific defaults are outside Appendix F and remain UNKNOWN._
