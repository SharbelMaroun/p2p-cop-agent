# Committed game configurations

Each counted game's configuration artifact is committed here, one directory per `game_id`:

```
games/<game_id>/config_<game_id>_g<NN>.json
```

## Why this directory is not gitignored

Appendix F obligation 4 (p.140/288): "It is mandatory to attach each game's configuration
file to the GitHub repository." It is the **only** hard commit obligation among the four
artifacts — the log has none in §9.4.1's minimum-contents list, though it is needed to run
the Replay app, which rule 20 makes a threshold condition; and the result's duty is to be
emailed under rule 51.

`.gitignore` excludes `/logs/`, which is right for run output and exactly wrong for the one
artifact an obligation says to commit. A config written there is retained on one machine and
lost to the repository, silently: the write succeeds and the file is present.

`src/p2p_cop_agent/reporting/retention.py` refuses to store a config under an ignored path,
and `tests/unit/test_retention.py` fails if `games/` is ever added to `.gitignore`. The way
this regresses is somebody tidying the working tree, which is the same reasoning that put
`/logs/` there in the first place.

## Why committing these is safe under rule 39

Rule 39 forbids pushing secrets "even if it is private and shared only with the lecturer".
What lands here is the negotiated match config — board, movement, scoring, pheromones, rate
limits — and nothing else, because `protocol/private_fields.py` keeps strategy, model and
credential fields out of the shared config in the first place, matching on **key names**
rather than values.

Obligation 4 and rule 39 are jointly satisfiable only because that guard runs before anything
reaches this directory.

## On nonces

An earlier note in the companion repository justified excluding logs on the grounds that
committing them would publish nonces. **That reasoning is wrong** and is corrected there.
Rule 18 keeps a nonce secret *until the end of the game* (`inst/:3354`), and Step 4 is the
Final Reveal, where "all values, including the Nonce, are revealed for a full mutual audit"
(`inst/:1136`). The obligation expires.

Logs are not committed wholesale here simply because no rule asks for it — not because doing
so would leak anything.
