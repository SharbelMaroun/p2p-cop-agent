# PRD — Cop Strategy

Status: legal objective and safe default documented; runtime policy deferred.

## Confirmed rules and recommendation

- Legal movement is `N`, `S`, `E`, `W`, or `STAY`; no diagonals.
- The Cop may place only legal barriers and must disclose every placement.
- Placing a barrier replaces the Police's movement for that turn: the Police gives
  up moving and instead places a barrier on either its own current cell or one
  orthogonally adjacent cell. Diagonal, more distant, off-board, duplicate, and
  over-quota targets are rejected.
- A barrier placed on the Thief’s current cell captures the Thief.
- A Thief with no legal move is captured.
- Communication is natural language only; direct numeric location protocols are
  prohibited.
- Book Ch. 6 presents algorithmic movement and a verbal LLM layer. Appendix E rule
  25 **recommends** not delegating movement to an LLM; it has no mandatory sanction
  and warns that unchecked spatial output can cause illegal moves/technical loss.

The graded mission is to replace the bundled simple baseline with a smarter
pure-Python strategy. Deterministic belief-aware pursuit/look-ahead and optional RL
are later alternatives. LLM movement remains disabled unless a future contract
revision is mutually agreed; optional low-token banter is separate. ADR-007 records
this project policy while preserving rule 25's recommendation status.

Confirmed configuration values are in
[PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md). Interfaces, weights, tie-breaking,
fallback behavior, and any provider/model are future choices. All later business
logic must be SDK-reachable.

This repository contains Cop strategy only and adds no strategy runtime in M0–M1.
