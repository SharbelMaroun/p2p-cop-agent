# Cop Delivery Plan

The active roadmap uses the common M0–M9 phase vocabulary. It decomposes only work
owned in this Cop repository. External review, Thief consumption, and lecturer
clarifications are exit dependencies, not Cop implementation tasks.

Current state: **`0.1.0-proposed` rejected; the M1.5 Option-B repair completed at
`0.2.3-proposed`, then advanced through `0.2.4`/`0.2.5-proposed` reconciling the
simulator-v3.0.0 wire profile with the book (see
[OPTION_B_HANDOFF.md](OPTION_B_HANDOFF.md) for the per-revision change log). The
stable/per-match boundary, explicit local rate mirror, public negotiation challenge,
secret per-turn commitment nonce, canonicalization, and FastMCP profile are resolved
and tested. M2 core domain, M3 local state/scoring/rules-harness and the
deterministic move-or-barrier baseline, and the M4 protocol/commit-reveal/audit
layer are complete. M5 is next. Independent review and contract freeze remain later
external gates and do not reopen M1.5.**

| Phase | Status | Cop outcome | Exit gate |
|---|---|---|---|
| M0 Evidence and source reconciliation | DONE | Authority order, provenance, conflicts, and unknowns are evidence-backed | Coordinator audit corrections are reflected |
| M1 Public contract, match configuration, parity and freeze | SUPERSEDED | `0.1.0-proposed` was rejected; the stable-semantics work carries into M1.5 | Replaced by the M1.5 Option-B gate |
| M1.5 Option-B contract repair and conformance | DONE | Option-B decision recorded, role-neutral `0.2.3-proposed` bundle, explicit per-run config inputs, public/secret nonce-domain separation, protocol/message schemas, hash vectors, and neutral conformance | Green conformance suite and published `0.2.3-proposed` handoff; independent parity/freeze remains separate |
| M2 Core domain rules | DONE | Immutable board/actions, legal moves, barriers, and capture rules through the SDK | Complete hardened unit suite (barrier-aware moves, adjacency, capture) |
| M3 Local state, scoring and deterministic baseline | DONE | Cop-only state/history, Appendix F scoring, transport-free rules harness, and deterministic move/barrier policy | A full local sub-game runs to capture or survival; the Cop policy receives no objective Thief cell, move/barrier intents are SDK-reachable and executable, and the provisional actor/check schedule is injected |
| M4 Protocol, canonicalization and commit-reveal | DONE | Accepted messages, exact canonical vectors, commit/reveal/audit state machine, receive-side replay/conflict guards, tamper/technical-loss outcomes, and Step-0 attestation | Independent vectors and tamper/failure tests pass |
| M5 FastMCP runtime and resilience | NEXT | Server/client peer, negotiation, deadlines, idempotency, retry, watchdog, tunnel boundary | Two independent local processes complete a resilient game |
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
3. a role-neutral top-level `shared_contract/` bundle at `0.2.3-proposed` that
   separates the stable specification/schema/fixture/verifier set from any
   per-match configuration and requires explicit match/mirror paths;
4. Option-B protocol and message schemas with positive/negative fixtures;
5. separated hash domains (per-turn commitment, `config_sha256`,
   `config_file_sha256`) and distinct public negotiation-challenge semantics;
6. unknown-opponent conformance against a neutral stub plus LF/controlled-byte
   hardening.

Exit gate: satisfied by the green conformance suite and published
`0.2.3-proposed` handoff. Copying or freezing any superseded bundle is not
authorized; independent parity, contract freeze, and any release authorization
remain separate later gates.

## Continuous gates

Every implementation commit must keep frozen `uv` sync, Ruff, branch coverage at
least 85%, file-length checks, secret scanning, Cop-local contract integrity, and
`git diff --check` green. Controlled-file changes also regenerate and review the
manifest while keeping the manifest outside its own file list.

The archived T001–T635 backlog remains historical coverage only.
