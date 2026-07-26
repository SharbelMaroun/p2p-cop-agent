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
| Active README/PRD/PLAN/TODO and seven mechanism PRDs | Governing M0–M1 documentation |
| `PARAMETERS_BASELINE.md` | Direct Appendix-F values/statuses; not candidates |
| `ARTIFACT_TEMPLATE_BASELINE.md` | Local generated-artifact observations; official provenance `NEEDS_MANUAL_REVIEW` |
| Proposed shared bundle | `0.1.0-proposed`, UNFROZEN pending Thief parity |
| Cop private example config | Local only; never parity-controlled |
| `config/drafts/` | Quarantined historical material; never loaded |
| `archive/pre-audit/` | Historical coverage only; never restored as active plan |
| Lecturer simulator | Pinned learning/interoperability reference under separate EULA |
| `.env-example` / `.gitignore` | Safe placeholders and exclusions; verified by quality gate |

## M1 verification evidence

The final clean-state gates were run on 2026-07-25 against CPython 3.12.13:

| Check | Actual result |
|---|---|
| `uv lock --check` | PASS; 19 packages resolved |
| `uv sync --frozen` after deleting `.venv` | PASS; clean environment created and 16 packages installed |
| `uv run ruff check .` | PASS; zero violations |
| `uv run pytest --cov --cov-branch --cov-fail-under=85` | PASS; 45 tests, 89.29% branch coverage |
| `uv run python scripts/check_file_lengths.py` | PASS; 19 source/script files and 15 test files |
| `uv run python scripts/check_secrets.py` | PASS; 108 text files, zero findings |
| deterministic manifest regeneration and verification | PASS; 13 controlled files; manifest SHA-256 `4b828705e173cc061c2f19924b4b0b2fc5652c383ce1d8d2b5cf3d004a89106c` |

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
