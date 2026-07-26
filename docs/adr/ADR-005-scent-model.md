# ADR-005 — Scent Model

Status: **SOURCE-BACKED PROPOSAL — UNACCEPTED**

## Context

Book Ch. 4 defines:

`τᵢⱼ(t+1) = max(0, (1-ρ)·τᵢⱼ(t) + Δτᵢⱼ)`

Appendix F fixes center intensity `0.9`, decay `ρ=0.10`, and field size 5×5. The
lecturer simulator has been observed using subtractive decay, creating a reference
deviation.

## Proposed decision

Use the book’s multiplicative update and fixed Appendix-F values. Do not copy the
simulator’s subtractive behavior. Exact radial-emission fixture values and update
timing require source-backed tests before runtime implementation.

## Acceptance

- Cross-peer numeric test vectors agree exactly.
- Shared configuration locks the fixed values/model identifier.
- Tests distinguish multiplicative from subtractive decay.

No scent runtime is implemented in M0–M1.
