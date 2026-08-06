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

## The live GUI (`M8-01`, `M8-01d`)

Built. `ui/live_app.py` is the window; `live/local_truth.py` and `live/view_model.py` are
what it reads.

**Screens and states (`M8-11a`).** One screen. A banner across the top in one of four
states, the board beneath it, received hints beside it, a legend, and five move buttons.

| Banner | Colour | Means | Input |
|---|---|---|---|
| `YOUR TURN` | green `#2ecc71` | turn received (act enabled) | accepted |
| `LOCKED` | grey `#95a5a6` | commit sent (input locked) | **ignored** |
| `WAITING` | grey `#95a5a6` | awaiting the opponent's turn | ignored |
| `GAME OVER` | slate `#546e7a` | the sub-game has ended | ignored |

The first two are Figure 9's, labels included. Locking is mandatory rather than advisory —
asked directly, the interface "enforces the lock" after the commit to stop both sides acting
on one turn — so the buttons are genuinely disabled and a click that lands during the
repaint is dropped rather than queued. A queued move would surface a turn later as an action
nobody chose.

**What it may never show.** Rule 8 (Mandatory): "display true local information only",
sanction "disqualification due to data breach". Rule 9 (Prohibited): "do not display the
full objective board state", sanction **project disqualification**. Enforced by the type,
not by care: `LocalTruth`'s field set is closed and built from explicit keyword arguments,
so there is nowhere to put the opponent's position and no runtime object to read it from.
`test_local_truth_boundary.py` fails if a field is added or if the package imports anything
that knows an objective coordinate.

The `T?` mark is our own inference from scent, not a reported position — the distinction
the whole trust map rests on.

**Accessibility (`M8-11b`).** Colour is not the only signal: every believed cell prints
its probability, the most likely is marked in text, barriers carry `#` as well as a dark
fill, and the legend names each mark. Below one percent the label degrades to `<1%` rather
than rounding to `0%`, which would print a board claiming the opponent is nowhere.

**Barriers (`M8-07a`).** Rule 15 makes a barrier public *once declared*, so
`disclosed_barriers` is the snapshot's own input — an undeclared barrier is not filtered
out of the view, it never enters it. A barrier also outranks the heat beneath it, because
an operator who cannot see one will plan a move into it.
