# Installation and usage

Covers `M9-11`, `M9-11a`…`M9-11e`.

Unlike the companion Thief repository, **this peer runs from the command line**. `p2p-cop
serve` launches the inbound FastMCP mailbox plus the outbound connector and plays one match
against a live opponent. The Thief's CLI is still a scaffold (`M9-025` there), so a counted
game between the two real agents is not launchable end-to-end yet — this half is.

## System requirements — `M9-11a`

| Requirement | Value |
| --- | --- |
| Python | ≥ 3.11 (`pyproject.toml`); developed on 3.12/3.13 |
| Package manager | [`uv`](https://docs.astral.sh/uv/) — the lockfile is the install contract |
| OS | **Windows 11 only.** Never run on Linux or macOS (`M9-12a` open) |
| Git | Required — the history scanner and commit-provenance resolver both shell out to it |
| Network | Not needed for any test; external calls are injected and doubled |

```bash
git clone https://github.com/SharbelMaroun/p2p-cop-agent
cd p2p-cop-agent
uv sync --frozen
```

`--frozen` installs exactly `uv.lock` and fails rather than quietly resolving something newer.
A freely-resolved run is not the run the gates passed.

## Run modes and flags — `M9-11b`

### Playing a match

```bash
uv run p2p-cop serve \
  --root .                          # repository root holding the shared bundle
  --match  config/match.json        # the shared, negotiated match config
  --rate-limits config/rate_limits.json
  --private config/game.toml        # this peer's private settings (gitignored)
```

`--match`, `--rate-limits` and `--private` are all required: the split is the point. The
first two are shared and byte-identical on both sides under rule 11; the third never leaves
this machine, because rule 2 forbids sharing strategy or memory between parties.

```bash
uv run p2p-cop --help       # no subcommand starts no runtime and imports no transport
uv run p2p-cop --version
```

`build_parser` deliberately imports nothing from `adapters/`, so `--version` cannot fail
because a transport dependency is missing.

### Quality gates

```bash
uv run ruff check .
uv run python -m pytest -q                          # 1819 tests, 85% branch floor
uv run python scripts/check_file_lengths.py
uv run python scripts/check_secrets.py              # working tree
uv run python scripts/scan_git_history.py           # every blob in history
uv run python scripts/check_shared_contracts.py     # the bundle this repo owns
uv run python scripts/check_submission_contents.py
uv run python scripts/verify_clean_clone.py         # all of the above, in a fresh clone
```

Run `verify_clean_clone.py` before any submission. A gate script living untracked in your
working tree passes everywhere except in a clone of what you actually pushed.

### Evidence and figures

```bash
uv run python scripts/experiment_arena.py
uv run python scripts/render_charts.py
uv run python scripts/bench_decision.py
uv run python scripts/compare_strategies.py
uv run python scripts/capture_live_gui_screenshot.py       # rule 20 evidence
uv run python scripts/capture_replay_screenshots.py        # "Verified OK" evidence
uv run python scripts/generate_shared_manifest.py          # after any bundle change
```

## Configuration — `M9-11c`

| Path | Effect | Committed? |
| --- | --- | --- |
| `config/police/` | Board, movement, scoring, pheromone and rate-limit values — the negotiated Appendix F parameters | Yes |
| `config/game.toml` | **Private** local settings: strategy knobs, model choice, email mode | No — gitignored, rules 39/40 |
| `config/*.local.toml` | Any local override | No |
| `shared_contract/` | The wire bundle this repository owns and publishes | Yes — `G-18` |
| `.env` | Credentials; `.env-example` documents the names without values | No |
| `credentials.json`, `token.json` | Gmail OAuth; refused by the history scanner **by name** | No |

The shared/private split is enforced, not conventional: `protocol/private_fields.py` matches
on **key names** and refuses a private field before anything is sent.

## Troubleshooting — `M9-11d`

| Symptom | Cause | Fix |
| --- | --- | --- |
| `REFUSING TO SCAN: this is a shallow clone` | `--depth 1`, or CI without `fetch-depth: 0` | `git fetch --unshallow`. The scan is meaningless on a truncated clone, which is why it refuses rather than reporting OK |
| `uv sync --frozen` fails | Lockfile and manifest disagree | `uv lock`, re-run the gates. Do not install unfrozen to get past it |
| `serve` exits at negotiation | The opponent's terms differ, or a private field was offered | See `test_negotiation_refusal.py`; rule 11 requires byte-identical shared config |
| Contract checker exits 1 | No accepted parity manifest yet | Expected before Stage C — the gate is fail-closed on purpose |
| `the mutual audit did not pass` | The opponent's log does not re-verify | Do **not** send a contradicting report. Rule 19 costs them the game; racing them makes it rule 35 and costs both |
| Manifest out of date | `shared_contract/` changed without regenerating | `uv run python scripts/generate_shared_manifest.py` |
| Secret scan flags a line | A value that looks live | Change it to a recognised placeholder. Do **not** allowlist |

## Licence and attributions — `M9-11e`

**MIT License**, © 2026 Sharbel Maroun and contributors. Full text in `LICENSE`.

Runtime dependencies, all permissive (MIT/BSD/Apache-2.0) and pinned in `uv.lock`:

| Package | Role |
| --- | --- |
| `fastmcp` | The peer-to-peer transport the book mandates |
| `pydantic` | Wire-message validation |
| `uvicorn`, `starlette` | ASGI serving for the peer |
| `httpx` | Client transport under FastMCP |

Development-only: `pytest`, `pytest-cov`, `ruff`.

No third-party code is vendored into `src/`. Course material in `inst/` belongs to
Dr. Yoram Segal and is quoted under fair academic use, cited by page throughout.
