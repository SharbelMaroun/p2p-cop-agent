# ADR-009 — GUI Truth Model

Status: **SOURCE-BOUND PLACEHOLDER — RUNTIME DEFERRED**

## Context

The live GUI is mandatory but may display local truth only. It may show own position,
own belief heatmap of the opponent, received clues, and turn/lock status. Opponent
private truth or an objective full board is disallowed.

## Proposed decision

Define one SDK-provided immutable local-view model consumed by GUI/CLI adapters.
Rendering code contains no game/business logic and receives no opponent-private
fields.

## Acceptance

- View-model/schema review proves the local-truth allowlist.
- Tests fail if private opponent coordinates/full truth enter the view.
- GUI logic delegates through the SDK/service boundary.

No GUI framework or runtime is selected in M0–M1.
