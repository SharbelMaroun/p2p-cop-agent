# PRD — Live GUI

Status: deliverable and truth boundary confirmed; framework/layout deferred.

## Confirmed behavior

- The live GUI shows local truth only: own position, own belief heatmap of the
  opponent, and received clues.
- It never displays the objective full board or the opponent’s private state;
  violating that boundary is disqualifying.
- The turn banner shows `YOUR TURN` when action is enabled and `LOCKED` after Commit.
- The README submission report includes a live belief-map screenshot.

Sources: book Ch. 7; Appendix E rules 8/9; `SR-008`/`SR-010`.

ADR-009 records the local-truth model. Framework, layout, accessibility, and event
wiring remain later SDK-boundary implementation choices. This milestone adds no GUI
behavior.
