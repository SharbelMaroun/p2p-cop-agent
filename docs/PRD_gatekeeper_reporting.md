# PRD — Gatekeeper and Reporting

Status: required shape, Appendix F limits, destinations, filename patterns, and
JSON-attachment rule are confirmed. Runtime delivery is not implemented.

## Confirmed behavior

- All external API calls go through one Gatekeeper providing limiting, FIFO queueing,
  backpressure, retries, monitoring, and DOS protection.
- Gmail reporting uses least-privilege send authorization; credentials and tokens are
  runtime-local secrets and stay out of Git. `credentials.json` and generated
  `token.json` are required for the documented OAuth flow and are already ignored.
- Each side separately sends the signed final JSON as an attachment at the end of a
  legal game. A free-text final-report body is rejected; conflicting/missing reports
  yield zero for both.
- Both attachments must be byte-identical to the mutually agreed aggregate result.
- Required report **content** includes four repository links, each game’s commit
  hash, and total token consumption. This does not prove the exact JSON key
  requiredness/type schema.
- Rate-limit minimums are 30 requests/minute, 2 concurrent requests, 5-second base
  retry, 3 retries, and queue depth at least 100.
- General/repository address: `rmisegal@gmail.com`; automated report address:
  `rmisegal+uoh26finalgame@gmail.com`.

Sources: book Ch. 9/Appendix A; Appendix E rules 28–35/49/53/54; Appendix F tables
19/20; `PS-008`.

## Schema and implementation boundary

The four observed schema-1.1 exemplar key sets and filename patterns are recorded in
[ARTIFACT_TEMPLATE_BASELINE.md](ARTIFACT_TEMPLATE_BASELINE.md). Formal
required/optional, exhaustive type/enum, conditional, and compatibility constraints
remain unresolved. ADR-003 isolates these fixtures from shared config schema 1.2;
ADR-010 owns Gmail delivery choices.

The behavior-free milestone may validate configuration and fixtures. Each run names
its local rate-limit enforcement mirror explicitly; its Gatekeeper object must equal
the authoritative shared match terms exactly, but its own bytes and local extensions
are not a byte-identical peer contract. This milestone does not implement a
Gatekeeper or Gmail/reporting runtime.

---

## Built state as of 2026-08-07 (`M7-21`)

This document described intentions; below is what the code now does, so the two cannot drift
apart unnoticed.

### The pipeline, end to end

```
play → audit_series → agree → settlement_record
                                     │
     ┌───────────────────────────────┴────────────────────────────┐
     │                                                            │
build_log → reveal_log (refuses without ended_at)          build_report_message
validated_write (schema, then write)                       (refuses non-agreed settlement)
store_config → games/<game_id>/                            encoded_message → base64url
     │                                                            │
check_one_identity (one game_uid)                          guard(gatekeeper) → send
```

Rule 36 fixes the **order** — the mutual audit is "a mandatory condition before agreement on
the JSON result" — and two things enforce it rather than one, because a precondition a caller
can forget is not a precondition:

- `settlement.agree(audit, ours, theirs)` takes the audit as its first argument.
- `gmail_message.build_report_message(..., settlement=…)` refuses any state short of `agreed`
  with `audit_passed is True` (`X-09`). `require_reportable` already existed and was a call a
  caller could skip; nothing downstream would have noticed.

### What each requirement is built as

| Requirement | Source | Built as |
| --- | --- | --- |
| One gatekeeper for every external call | `PS-008` | `services/gatekeeper.py` |
| Send-only OAuth scope | `AE-030` | `REQUIRED_SCOPE` |
| JSON attachment, never body text | `AE-033`, `AE-034` | `build_report_message` |
| base64url with padding | Gmail API | `encoded_message` |
| Artifacts validated before writing | `M7-14` | `validated_write` |
| Declaration / log / result schemas | book-mandated fields only | `shared_contract/schemas/` |
| Nonces secret until the game ends | `AE-018` | `reveal_log` refuses without `ended_at` |
| Every game's config committed | Appendix F obligation 4 | `reporting/retention.py`, `games/` |
| Accurate count of games played | `AE-037`, `AE-038` | `reporting/league.py` |
| Tokens per game *and* per series | `AE-054` | `reporting/token_ledger.py` |
| Diversity reward for a new opponent | Appendix F table 18 | `league.diversity_reward` |
| Commit hash of the code that played | `AE-053` | `reporting/provenance.py` |
| Evidence a report was sent | `AE-032` | `evidence.SendReceipt` |
| Token refresh without human action | — | `services/credential_refresh.py` |

### Deliberate departures

**Schemas require only what the *book* requires, and accept unknown fields.** The book was
asked directly: it is `NOT-SPECIFIED` on whether extra non-contradicting fields are forbidden
in the reporting artifacts. Refusing an opponent's declaration over a key no source forbids
would fail the very audit rule 36 requires. The **config** is the exception — p.111/243 says
it must hold "only items the parties must agree on", and an unagreed field means a refusal to
play. `X-04` is what asserting more than the sources support cost last time.

**The three new schemas joined the bundle at `0.2.9-proposed` rather than bumping to
`0.2.10`.** A version tells a *consumer* something changed, and this bundle is `-proposed`
and has never been accepted (`M1.5-13`). Bumping meant editing 27 declarations across 19
files, several of them historical narrative of the form "0.2.8 → 0.2.9" — and rewriting
history is how `X-03` did its damage. The bump belongs to acceptance, not to authoring.

**`SendReceipt` is not `ProofOfDelivery`.** The book's decisive layer is receipt at the
lecturer's address (p.78/183), and a sender cannot observe receipt — only the recipient can.
Every record written carries `evidences: API acceptance, not receipt by the lecturer`.

### Still open

The OAuth consent flow itself (`M7-15`, `M7-15a`) — the operator's action on their own
machine; see `docs/RUNBOOK_reporting_setup.md`. Template requiredness remains `U-019`.
