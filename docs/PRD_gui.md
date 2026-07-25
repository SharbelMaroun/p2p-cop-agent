# PRD — Live GUI

Status: requirement `CONFIRMED` (`SR-010`); exact framework/layout is an implementation choice.

## Confirmed structure (cited — book Ch.7; Appendix E rules 8, 9)

- A **live GUI** displays **local information only**: own position, own belief **heatmap** of the
  opponent (deeper = higher probability), and received clues.
- It **must never** show the full objective board or the opponent's private state — doing so is a
  **disqualification** (rule 9).
- A **turn banner** reflects the async state machine: **YOUR TURN** when the MCP server hands
  over, **LOCKED** (input disabled) after Commit.
- A **screenshot of the belief-map GUI is a submission requirement** (README section 5, `SR-008`).

## Pending / UNKNOWN

- GUI framework (Tkinter/PyQt) and exact layout are a team implementation choice, not an official
  mandate; decided during the implementation phase behind the SDK boundary (`PS-007`).

No GUI code is authorized during the requirements phase. This PRD exists so the mandatory GUI
deliverable is tracked (guidelines §2.3 requires a PRD per complex component).
