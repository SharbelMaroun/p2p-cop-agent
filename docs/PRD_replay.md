# PRD — Replay and Verification Viewer

Status: **verifier built and proven on foreign logs (`M8-02c`/`02d`/`08`/`08a`/`12`);
the UI that paints it is still open (`M8-02`, `M8-05`).**

Appendix E rule 20 (Mandatory), p. 129/272: "Mandatory to build a match log reconstruction
and replay app for observation and verification; **Threshold condition** for confirmation
of logs and submission of the project." Confirmed with the book notebook 2026-08-06: the
project cannot be accepted without it. `:1769` restates it — "a mandatory project
requirement, not an optional component".

## Built

- `replay/load.py` — accepts a path and nothing else, so an opponent's log opens on the
  same code path as ours. Tolerant of foreign shape (unknown `schema_version`, extra keys,
  `sub_game` for `sub_game_number`); strict about the three fields verification consumes.
- `replay/verify.py` — recomputes each commitment from the file's own bytes. Two verdicts,
  no third. One bad step voids the whole match (`:1743`, `:1753`).
- `replay/cursor.py` — step forward, back, `go_to`, `go_to_step`, `restart`, and
  `go_to_first_divergence`. The verdict is a property, never a field.

## Confirmed behavior

- The viewer loads `log_<game_id>_g<NN>.json`, moves through the history, and
  recomputes each SHA-256 commitment from revealed data.
- A match displays `Verified OK`; any mismatch displays `TAMPERED` and invalidates
  the match. There is no third state — `:1769` allows "no room for manual correction".
- **The verdict is recomputed on every navigation, never cached from load time**
  (`M8-08a`). The `Verified OK` stamp is submission evidence; a verdict computed once and
  painted forever is a claim about the past tense.
- **It must verify the opponent's log, not only ours.** Rule 36 mandates a "comprehensive
  mutual log audit" as a necessary condition for agreement (p. 131/276); p. 39/102: "each
  side presents its full log … each side reconstructs the opponent's data through the
  revealed nonces". A verifier fed only its own output proves nothing.
- The README submission report includes a `Verified OK` replay screenshot. Asked directly:
  the book requires it "within the README.md academic report" (p. 81/189) and calls it
  "absolute mandatory"; the **exact filename and directory are not specified**.

## Which hash construction (`M8-02d`, `C-023` RESOLVED)

Chapter 7's `verify_step` sketch (`:1733`) computes `sha256(f"{nonce}|{move}")`. Ours
hashes the canonical payload then the nonce. These never agree — a viewer written to the
sketch would red-banner an honest log at step 1.

This is **not** a contradiction requiring disclosure. `:1757` footnotes the listing in the
book's own voice: "the sketch simplified the input for the sake of the illustration; in
practice the signature covers all components of the step — Intent, Move, State and Nonce —
as detailed in the protocol in Chapter 5". The reference simulator diverges identically.

## Sequence integrity — reported, never bannered (`M8-08d`, `U-032`)

Every commitment covers one record, so a log whose records are **shuffled, missing one, or
carrying a duplicate** still verifies digest by digest. The first batch shipped without
noticing; a direct probe confirmed all three stamped `Verified OK`.

`replay/sequence.py` now detects them. It deliberately does **not** change the verdict:

* rule 19 is "any mismatch **in the digest**" (p.129/271) — structural damage is not rule 19;
* a missing step is instead "contradictory reports" (rule 35, p.131/275) and an illegal state
  jump (rule 5), and rule 35's sanction falls on **both** teams;
* neither the book nor the reference requires ordering to be checked at all — the reference
  verifies each record "with no reference to its place in the sequence".

So a differently-ordered opponent log is not evidence of forgery, and red-bannering it would
be a false accusation carrying "no appeal process" (`:1769`). Findings are tagged with the
rule they answer to and left for settlement, which is where both logs are actually compared.

## Open

- The UI (`M8-02` tamper view, `M8-05` screenshot capture). The reference ships Tkinter
  with `Play/Pause`, `Step >`, `Restart`, sub-game selection and `Go to step`; ours needs
  only to make the banner visible and the capture reproducible (`M8-05d`).
- Belief-heatmap rendering (`M8-05a`) is a separate deliverable from the replay banner.

Sources: book Ch. 7 (`:1689`–`:1769`); Appendix E rules 20 and 36; `SR-008`/`SR-010`.

## The view (`M8-02`, `M8-02e`)

Built. `ui/replay_app.py` is a Tk window; `replay/view_model.py` is what it reads.

**Screens and states.** One screen, two states. A stamp across the top — green
`Verified OK` or red `TAMPERED` — with the match banner beneath it, the source path, and
the sequence line. Below: every record with its own verdict, and a detail panel showing the
step under the cursor with its `nonce`, `move` and full `commit`, which is the set the book
requires (p.56/142). Controls are `|< Restart`, `< Back`, `Step >` and `Jump to divergence`,
covering "back and forth in time" (p.56/141).

**The board is deliberately absent.** Asked directly, it is not required — "the mandatory
screenshot requirement focuses on the verdict banner" — and the belief map belongs to the
live GUI, which is where the book puts it.

**No widget touches domain or protocol code** (`M8-06`). The view-model produces frozen,
display-ready values and the widgets read nothing else, so a widget cannot mutate a replay
and the screen's claims can be asserted in CI even though a Tk window cannot.

## Submission screenshots (`M8-05`)

`assets/replay-verified-ok.png` and `assets/replay-tampered.png`, regenerated by
`scripts/capture_replay_screenshots.py` from two committed fixtures.

Three things here are **project choices, not requirements**, and are recorded as such:

* the `assets/` location — the book "only mandates that the images be displayed within the
  README.md academic report" and does not mandate an `assets/` directory;
* the `TAMPERED` capture — only `Verified OK` is a mandatory submission image;
* showing our own log rather than an opponent's — the book does not say which.

They are real screen captures of the real widget tree. A rendered picture of what the app
would look like would satisfy the row and be a fabricated exhibit.
