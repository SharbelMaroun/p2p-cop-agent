# Repository Audit

## Inspected baseline

At commit `72c05a18ba7a9a7fe14dad2ecb85034c64fa310a`, there were no Python package,
tests, `pyproject.toml`, or lockfile. That is historical baseline evidence, not the
state this M0–M1 branch is intended to leave.

The baseline also contained false parity claims, stale Appendix-F candidate wording,
overbroad schema unknowns, a missing schema 1.1/1.2 conflict, and blanket
“all development blocked” wording. Those active claims are corrected and the exact
baseline hashes are preserved in [PARITY_REPORT.md](PARITY_REPORT.md).

## Current disposition

| Scope | Disposition |
|---|---|
| Active README/PRD/PLAN/TODO and seven mechanism PRDs | Governing M0–M9 Cop roadmap; runtime deferred |
| `PARAMETERS_BASELINE.md` | Direct Appendix-F values/statuses; not candidates |
| `ARTIFACT_TEMPLATE_BASELINE.md` | Local generated-artifact observations; official provenance `NEEDS_MANUAL_REVIEW` |
| Proposed shared bundle | `0.1.0-proposed`, locally complete and UNFROZEN; coordinator acceptance and Thief exact-byte parity remain external dependencies |
| Cop private example config | Local only; never parity-controlled |
| `config/drafts/` | Quarantined historical material; never loaded |
| `archive/pre-audit/` | Historical coverage only; never restored as active plan |
| Lecturer simulator | Pinned learning/interoperability reference under separate EULA |
| `.env-example` / `.gitignore` | Safe placeholders and exclusions; verified by quality gate |

## Corrected M1 candidate verification

The corrected candidate gates were rerun on 2026-07-27 against CPython 3.12.13:

| Check | Actual result |
|---|---|
| `uv lock --check` | PASS; 19 packages resolved |
| `uv sync --frozen` after deleting `.venv` | PASS; clean environment created and 16 packages installed |
| `uv run ruff check .` | PASS; zero violations |
| `uv run pytest --cov --cov-branch --cov-fail-under=85` | PASS; 79 tests, 92.09% branch coverage |
| `uv run python scripts/check_file_lengths.py` | PASS; 20 source/script files and 18 test files |
| `uv run python scripts/check_secrets.py` | PASS; 122 text files, zero findings |
| Cop-local manifest integrity | PASS; 18 controlled files |
| manifest exact-byte SHA-256 | `473982dc01594b1c7abee8fc7f20cf665a6b245e53114ed4a2732c115a35d86a` |
| `git diff --check` | PASS |

The read-only Thief comparison remains an expected NO-GO: 16 of 18 controlled
paths and the manifest are absent, while `.gitattributes` and
`scripts/check_shared_contracts.py` differ. No Thief file was changed.

> **Superseded numbers.** The table above is the dated 2026-07-27 snapshot and is
> retained as history. It predates M2–M4, so its counts no longer describe the
> repository. Re-measured at end of day 2026-07-31: **505 tests, 99.31% branch
> coverage**; ruff clean; 43 source/script and 58 test files within the length cap;
> secret scan 204 files, 0 findings; shared-contract bundle 35 controlled files, manifest
> `8f24a3b9daa05b5bc3c61b30ee98b7be6d731049ecb9345c63709e4189a7688b`. The
> controlled bundle also moved from `docs/contracts/` + `docs/schemas/` to the
> top-level `shared_contract/` directory; documents written before that move name
> the old paths.

A read-only provenance comparison used the pinned simulator commit
`960499fd5e8777b4929625f5d8fdcf2ab4677b54`: 15 Cop source files were compared
with all 101 tracked simulator Python files. It found zero identical whole-file
SHA-256 hashes, zero identical normalized eight-line windows of at least 160
characters, and zero simulator-specific source markers. This is strong negative
copying evidence for the current scaffold, not a general proof of authorship.

## Milestone authorization

Authorized now: documentation, shared contract/config fixtures, typed validation
models, package/SDK smoke scaffold, tests, and quality/parity scripts.

Not authorized now: game engine, FastMCP handlers/client, live peer process, LLM,
Gmail, GUI, replay, or league behavior. Later runtime gates are deferred rather than
blocking the behavior-free scaffold.
