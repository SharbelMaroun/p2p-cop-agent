# ADR-007 — LLM Movement Policy

Status: **PROPOSED — UNACCEPTED**

## Context

Book Ch. 6 uses algorithmic movement and an LLM verbal layer. Appendix E rule 25
recommends not delegating movement to an LLM and warns about illegal spatial output,
but explicitly provides no mandatory sanction.

## Proposed decision

Use deterministic Python movement as the default Cop policy. An LLM may contribute
only to the verbal/behavioral layer in the baseline. This is a safety,
reproducibility, latency, and cost choice—not a falsely mandatory rule.

Any later exception requires an explicit accepted revision, mutual compatibility,
and a deterministic local legality filter; the party remains responsible for errors.

## Acceptance

- Default move selection is deterministic and works with no LLM/provider.
- Every chosen move passes local legality validation.
- Documentation and tests never describe rule 25 as an automatic sanction.
