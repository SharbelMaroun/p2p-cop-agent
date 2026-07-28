# Shared Gameplay Rules

Contract version: `0.2.3-proposed`
Status: **PROPOSED / UNFROZEN — role-neutral**

These are the book-authoritative gameplay rules both peers implement. Exact
per-field values and bounds are machine-checked by `schemas/match-config.schema.json`;
this document is the prose specification. Where the book leaves a wire detail open,
the Option-B profile in `PROTOCOL_PROFILE.md` selects the interoperable answer.

## Mandatory rules

| Rule | Authority |
|---|---|
| The two peers are separate processes sharing no live memory, database, runtime filesystem, or private truth. | Book Ch.2; Appendix E rules 1-2 |
| Both peers load a byte-identical per-match shared game object. | Appendix E rule 11; Appendix F mandatory rule 1 |
| Legal movement is `N`, `S`, `E`, `W`, or `STAY`; diagonals are illegal. | Appendix E rules 13-14; Appendix F table 15 |
| A barrier occupies either the placing peer's own current cell or a cell exactly one orthogonal step away; diagonal and more distant targets are illegal. Placing it gives up that turn's movement, it is disclosed truthfully, and it is impassable for both players thereafter. | Book §3.4; Appendix E rules 15-16, 46-47 |
| Barriers respect the negotiated quota (`max_barriers`, Minimum 14). | Appendix F table 15 |
| SHA-256 commit-reveal is mandatory; per-turn commitment nonces stay secret until the end-game audit; a mismatch is a technical loss worth zero. | Appendix E rules 17-19 |
| Scent uses the multiplicative update `tau_ij(t+1) = max(0, (1-rho) * tau_ij(t) + delta_tau_ij)`. | Book Ch.4; ADR-005 |
| A single orchestrator entry point, explicit state machine, illegal-transition rejection, deadlines, watchdog, and public tunnel are mandatory runtime requirements. | Appendix E rules 3-7, 10 |
| A live GUI may display local truth only. | Appendix E rules 8-9 |
| Final reports are JSON attachments; a free-text final-report body is prohibited. | Appendix E rules 32-35 |

## Capture conditions

The book (§3.4 and the §3.5 scoring table) defines three capture conditions:

1. the pursuing peer lands on the evading peer's cell (the primary Capture Claim);
2. a barrier is placed on the evading peer's current cell;
3. the evading peer is trapped: every one of its four cardinal neighbours is off
   the board or occupied by a barrier.

The book's precise wording of condition 3 resolves the `STAY` question: because a
trapped peer's neighbours are all off-board or barriered, the always-available
`STAY` action does not prevent the trapped capture.
