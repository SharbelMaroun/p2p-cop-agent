# Cop Delivery Plan

The active roadmap uses the common M0–M9 phase vocabulary. It decomposes only work
owned in this Cop repository. External review, Thief consumption, and lecturer
clarifications are exit dependencies, not Cop implementation tasks.

Current state: **`0.1.0-proposed` rejected; M1.5 Option-B repair at
`0.2.1-proposed` with the barrier-rule and role-alternation blockers closed but
four semantic blockers still open (unsupported required root fields, incomplete
cross-field validation, canonicalization profile, and book-level FastMCP
interoperability); M2 core domain implemented and hardened; coordinator review,
contract freeze, and `M2_GAMEPLAY: GO` remain later gates.**

M1.5 is not complete. Two open blockers are Cop-side work; two require an
authoritative external answer and cannot be closed from this repository.

| Phase | Status | Cop outcome | Exit gate |
|---|---|---|---|
| M0 Evidence and source reconciliation | DONE | Authority order, provenance, conflicts, and unknowns are evidence-backed | Coordinator audit corrections are reflected |
| M1 Public contract, match configuration, parity and freeze | SUPERSEDED | `0.1.0-proposed` was rejected; the stable-semantics work carries into M1.5 | Replaced by the M1.5 Option-B gate |
| M1.5 Option-B contract repair and conformance | IN PROGRESS — semantic blockers open | Option-B decision recorded, role-neutral `0.2.1-proposed` bundle, protocol/message schemas, hash-domain vectors, unknown-opponent conformance, and the barrier/alternation semantic corrections | Green conformance suite, all semantic blockers closed or externally deferred, and a published `0.2.1-proposed` handoff |
| M2 Core domain rules | IMPLEMENTED (hardened in M1.5) | Immutable board/actions, legal moves, barriers, and capture rules through the SDK | Complete hardened unit suite (barrier-aware moves, adjacency, capture) |
| M3 Local state, scoring and deterministic baseline | DEFERRED (movement policy carved out and delivered) | Cop-only state/history, scoring, harness, and deterministic policy | Full local series simulation without private-truth leakage |
| M4 Protocol, canonicalization and commit-reveal | DEFERRED | Accepted messages, exact canonical vectors, commit/reveal/audit state machine | Independent vectors and tamper/failure tests pass |
| M5 FastMCP runtime and resilience | DEFERRED | Server/client peer, negotiation, deadlines, idempotency, retry, watchdog, tunnel boundary | Two independent local processes complete a resilient game |
| M6 Scent, belief and private strategy | DEFERRED | Multiplicative scent, Cop-local belief, deterministic strategy, optional private verbal layer | Legal deterministic behavior under observation/fallback tests |
| M7 Series orchestration, artifacts, gatekeeper and reporting | DEFERRED | Six-sub-game series, validated artifacts, API gatekeeper, signed report delivery | One complete local series produces accepted audit artifacts |
| M8 GUI, replay, interoperability and security hardening | DEFERRED | Local-truth GUI, verified/tampered replay, unknown-opponent interop, security/failure hardening | Remote rehearsal and evidence screenshots pass |
| M9 League evidence, submission and release | DEFERRED | League runs, academic report, cost/evidence package, annotated release | Submission checklist and current Moodle instructions satisfied |

## M1.5 Option-B contract repair and conformance gate

The 2026-07-28 coordinator decision rejected `0.1.0-proposed`, authorized
contract-independent M2 domain work, and selected Option B (the `simulator-v3`
interoperability profile pinned to `960499fd5e8777b4929625f5d8fdcf2ab4677b54`) as a
documented academic-freedom choice where the book leaves wire details open. It did
**not** rank the simulator above the book in general.

M1.5 replaces the old freeze gate. It delivers, as focused green milestones:

1. the recorded Option-B decision (ledger, conflicts, ADR-001/006, TODO, PLAN);
2. hardened barrier-aware M2 domain semantics;
3. a role-neutral top-level `shared_contract/` bundle at `0.2.1-proposed` that
   separates the stable specification/schema/fixture/verifier set from any
   per-match configuration;
4. Option-B protocol and message schemas with positive/negative fixtures;
5. separated hash domains (move-commit, `config_sha256`, `config_file_sha256`) with
   canonicalization vectors;
6. unknown-opponent conformance against a neutral stub plus LF/controlled-byte
   hardening.

Exit gate: a green conformance suite and a published `0.2.1-proposed` handoff.
Copying or freezing the rejected `0.1.0-proposed` bundle is not authorized, and
contract freeze plus a separate `M2_GAMEPLAY: GO` remain later coordinator gates.

## Continuous gates

Every implementation commit must keep frozen `uv` sync, Ruff, branch coverage at
least 85%, file-length checks, secret scanning, Cop-local contract integrity, and
`git diff --check` green. Controlled-file changes also regenerate and review the
manifest while keeping the manifest outside its own file list.

The archived T001–T635 backlog remains historical coverage only.
