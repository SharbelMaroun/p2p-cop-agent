# PRD — Cop Strategy

Status: legal objective and safe default documented; runtime policy deferred.

## Confirmed rules and recommendation

- Legal movement is `N`, `S`, `E`, `W`, or `STAY`; no diagonals.
- The Cop may place only legal barriers and must disclose every placement.
- A barrier placed on the Thief’s current cell captures the Thief.
- A Thief with no legal move is captured.
- Communication is natural language only; direct numeric location protocols are
  prohibited.
- Book Ch. 6 presents algorithmic movement and a verbal LLM layer. Appendix E rule
  25 **recommends** not delegating movement to an LLM; it has no mandatory sanction
  and warns that unchecked spatial output can cause illegal moves/technical loss.

The source-backed default is deterministic heuristics (belief update plus legal
Manhattan pursuit). Combined deterministic look-ahead and optional RL are later
alternatives. ADR-007 records this as a project policy, not as a falsely mandatory
LLM ban.

Confirmed configuration values are in
[PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md). Interfaces, weights, tie-breaking,
fallback behavior, and any provider/model are future choices. All later business
logic must be SDK-reachable.

This repository contains Cop strategy only and adds no strategy runtime in M0–M1.
