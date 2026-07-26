# Cop Delivery Plan

The active roadmap uses the common M0–M9 phase vocabulary. It decomposes only work
owned in this Cop repository. External review, Thief consumption, and lecturer
clarifications are exit dependencies, not Cop implementation tasks.

Current state: **M1 corrected candidate ready for review; CONTRACT FREEZE NO-GO; M2
BLOCKED.**

| Phase | Status | Cop outcome | Exit gate |
|---|---|---|---|
| M0 Evidence and source reconciliation | DONE | Authority order, provenance, conflicts, and unknowns are evidence-backed | Coordinator audit corrections are reflected |
| M1 Public contract, match configuration, parity and freeze | IN PROGRESS / BLOCKED | Cop-authored stable semantics, neutral match proposal, local integrity, cross-root comparison, CI, and handoff | P0 questions resolved; coordinator acceptance; Thief byte consumption and independent proof |
| M2 Core domain rules | DEFERRED | Immutable board/actions, legal moves, barriers, and capture rules through SDK | M1 freeze GO plus complete unit suite |
| M3 Local state, scoring and deterministic baseline | DEFERRED | Cop-only state/history, scoring, harness, and deterministic policy | Full local series simulation without private-truth leakage |
| M4 Protocol, canonicalization and commit-reveal | DEFERRED | Accepted messages, exact canonical vectors, commit/reveal/audit state machine | Independent vectors and tamper/failure tests pass |
| M5 FastMCP runtime and resilience | DEFERRED | Server/client peer, negotiation, deadlines, idempotency, retry, watchdog, tunnel boundary | Two independent local processes complete a resilient game |
| M6 Scent, belief and private strategy | DEFERRED | Multiplicative scent, Cop-local belief, deterministic strategy, optional private verbal layer | Legal deterministic behavior under observation/fallback tests |
| M7 Series orchestration, artifacts, gatekeeper and reporting | DEFERRED | Six-sub-game series, validated artifacts, API gatekeeper, signed report delivery | One complete local series produces accepted audit artifacts |
| M8 GUI, replay, interoperability and security hardening | DEFERRED | Local-truth GUI, verified/tampered replay, unknown-opponent interop, security/failure hardening | Remote rehearsal and evidence screenshots pass |
| M9 League evidence, submission and release | DEFERRED | League runs, academic report, cost/evidence package, annotated release | Submission checklist and current Moodle instructions satisfied |

## M1 freeze gate

M1 remains NO-GO while any of these conditions is unresolved:

1. Authentic provenance and formal status of the four local JSON artifacts.
2. Schema compatibility among book example 1.2, local observation 1.1, and simulator
   runtime 1.3.
3. Formal identifier syntax, UUID creation/version, and resolved-versus-pattern
   `links` representation.
4. Complete artifact required/optional/type/conditional rules.
5. Coordinator decision on whether the operational `rate_limits.json` mirror remains
   in exact-byte cross-repository parity.
6. Coordinator acceptance followed by Thief exact-byte consumption and independent
   local/cross-root verification.

Participant representation/order, unified shared config, artifact lifecycle, config
hash scope/bytes, and the six-game role schedule are now incorporated with a
reproducible vector.
No gameplay work begins until the coordinator changes the M1 gate to GO.

## Continuous gates

Every implementation commit must keep frozen `uv` sync, Ruff, branch coverage at
least 85%, file-length checks, secret scanning, Cop-local contract integrity, and
`git diff --check` green. Controlled-file changes also regenerate and review the
manifest while keeping the manifest outside its own file list.

The archived T001–T635 backlog remains historical coverage only.
